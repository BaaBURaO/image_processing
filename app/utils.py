from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from google.cloud import storage
from PIL import Image
import io
import os
import uuid
import urllib.request
from app.models import ImageProcessRequest, FileProcessRequest
from app.database import SessionLocal

# FastAPI instance
app = FastAPI()
credential_path = "./adept-watch-434307-c5-a6c0e72ab5db.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# Initialize Google Cloud Storage client
client = storage.Client()
bucket_name = "processed_img"
bucket = client.bucket(bucket_name)

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

async def upload_image_to_gcs(image: Image, image_name: str) -> str:
    """Uploads an image to Google Cloud Storage and returns the URL."""
    blob = bucket.blob(image_name)
    
    # Save image to a BytesIO object
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)

    # Upload the image
    blob.upload_from_file(buffer, content_type='image/jpeg')
    
    # Make the image public and return the public URL
    blob.make_public()
    return blob.public_url

async def compress_images(image_urls):
    """Compress images and upload them to Google Cloud Storage."""
    compressed_image_urls = []
    
    for image_url in image_urls:
        try:
            # Download the image
            with urllib.request.urlopen(image_url) as response:
                image_bytes = response.read()
                image = Image.open(io.BytesIO(image_bytes))

                # Compress the image
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=50)
                buffer.seek(0)

                # Generate a unique name and upload to GCS
                image_name = f"compressed_{uuid.uuid4().hex}.jpg"
                compressed_image_url = await upload_image_to_gcs(Image.open(buffer), image_name)
                
                compressed_image_urls.append(compressed_image_url)

        except Exception as e:
            print(f"Error processing image {image_url}: {e}")
            continue
    
    return compressed_image_urls

async def compress_images_endpoint(file_request_id: int, session: AsyncSession = Depends(SessionLocal)):
    """Endpoint to compress and upload images."""
    try:
        print(f"file_request_id: {file_request_id}, type: {type(file_request_id)}")
        
        # Ensure the ID is an integer before using it in the query

        # Correct usage of select statement with valid comparison
        stmt = select(FileProcessRequest)
        print("###########", FileProcessRequest, file_request_id)
        result = await session.execute(stmt)
        file_request = result.scalar_one_or_none()
        
        if not file_request:
            raise HTTPException(status_code=404, detail="File request not found")

        # Get related image process requests
        image_requests = await get_image_process_requests(file_request.id, session)

        for image_request in image_requests:
            compressed_image_urls = await compress_images(image_request.input_image_urls)
            
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


