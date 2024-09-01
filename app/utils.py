from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from google.cloud import storage
from PIL import Image
import io
import os
import uuid
import urllib.request
import csv
from io import StringIO
from app.models import ImageProcessRequest, FileProcessRequest
from app.database import SessionLocal, engine, Base
from io import BytesIO
import pandas as pd
import tempfile


# FastAPI instance
app = FastAPI()
credential_path = "./auth.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
project_id= "adept-watch-434307-c5"

# Initialize Google Cloud Storage client
client = storage.Client(credential_path)
bucket_name = "processed_img"
bucket = client.bucket(bucket_name)

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
        
async def upload_image_to_gcs(file_path: str, image_name: str) -> str:
    """Uploads an image to Google Cloud Storage and returns the URL."""
    print(f"filepath: {file_path}", image_name)

    try:
        blob = bucket.blob(image_name)
        blob.upload_from_filename(file_path, content_type='image/jpeg')
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"Error uploading image to GCS: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image to Google Cloud Storage.")

async def compress_images(image_urls):
    """Compress images and upload them to Google Cloud Storage."""
    compressed_image_urls = []
    print("******", image_urls)

    for image_url in image_urls:
        try:
            # Download the image
            with urllib.request.urlopen(image_url) as response:
                image_bytes = response.read()
                image = Image.open(io.BytesIO(image_bytes))

                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                    temp_file_path = temp_file.name

                    # Compress the image and save to the temporary file
                    image.save(temp_file_path, format='JPEG', quality=50)

                    # Generate a unique name and upload to GCS
                    image_name = f"compressed_{uuid.uuid4().hex}.jpg"
                    compressed_image_url = await upload_image_to_gcs(temp_file_path, image_name)

                    compressed_image_urls.append(compressed_image_url)

                    # Clean up the temporary file
                    os.remove(temp_file_path)

        except Exception as e:
            print(f"Error processing image {image_url}: {e}")
            continue

    return compressed_image_urls

async def compress_images_endpoint(file_request_id: int, session: AsyncSession):
    """Endpoint to compress and upload images."""
    try:
        # Ensure the ID is an integer before using it in the query
        stmt = select(FileProcessRequest).where(FileProcessRequest.id == file_request_id)
        result = await session.execute(stmt)
        file_request = result.scalar_one_or_none()
        
        if not file_request:
            raise HTTPException(status_code=404, detail="File request not found")

        # Get related image process requests
        image_requests = await get_image_process_requests(file_request.id, session)

        for image_request in image_requests:
            compressed_image_urls = await compress_images(image_request.input_image_urls)
            
            # Update output_image_urls in the database
            image_request.output_image_urls = compressed_image_urls
            await session.commit()

        file_request.status = "SUCCESS"
        await session.commit()

        return {"status": "Images processed and uploaded successfully"}

    except Exception as e:
        print(f"Error compressing and uploading images: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Image compression and upload failed.")

async def get_image_process_requests(file_process_id: int, session: AsyncSession):
    """Fetch image process requests linked to a file process request."""
    try:
        stmt = select(ImageProcessRequest).where(ImageProcessRequest.file_process_id == file_process_id)
        result = await session.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        print(f"Error fetching image process requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch image process requests.")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):

    data = {}

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")

    try:
        file_content = await file.read()
        buffer = StringIO(file_content.decode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read the file: {str(e)}")

    async with SessionLocal() as session:
        new_file_request = FileProcessRequest(status="INPROGRESS")
        session.add(new_file_request)
        await session.commit()
        await session.refresh(new_file_request)
        data["file_id"] = new_file_request.id

        try:
            csv_reader = csv.DictReader(buffer)
            for row in csv_reader:
                id = row['ID']
                product_name = row['Product Name']
                input_image_urls = row['Input Image Urls'].split(',')
                new_image_request = ImageProcessRequest(
                    sl_no=id,
                    file_process_id=new_file_request.id,
                    product_name=product_name,
                    input_image_urls=input_image_urls,
                    output_image_urls=[]
                )
                session.add(new_image_request)
                await session.commit()
                
            # Process images
            await compress_images_endpoint(new_file_request.id, session)

        except csv.Error as e:
            raise HTTPException(status_code=400, detail=f"Error processing CSV file: {str(e)}")

    buffer.close()
    return data

@app.get("/status/{request_id}")
async def get_status(request_id: int):
    async with SessionLocal() as session:
        stmt = select(FileProcessRequest).where(FileProcessRequest.id == request_id)
        result = await session.execute(stmt)
        file_request = result.scalar_one_or_none()
        
        if file_request:
            return {"status": file_request.status}
        raise HTTPException(status_code=404, detail="Request ID not found")
