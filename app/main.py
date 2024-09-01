from fastapi import FastAPI, APIRouter, UploadFile, File, Depends, HTTPException
from app.database import engine, Base
from app import crud, schemas
import csv 
from io import StringIO 
from app.database import SessionLocal
from app.models import ImageProcessRequest, FileProcessRequest

from app.utils import compress_images_endpoint
import time
import random


app = FastAPI()


# Ensure database tables are created
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup") #wWhen server starts
async def startup():
    await create_tables()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):

    data = {}

    new_file_request = FileProcessRequest(status="INPROGRESS")
      
    async with SessionLocal() as session: 
        session.add(new_file_request)
        
        # Commit the transaction to save the new request to the database
        await session.commit()
        
        # Refresh the instance to load the auto-generated ID
        await session.refresh(new_file_request)
        
        # Return the newly inserted request ID
        data["file_id"] = new_file_request.id

    # Validate CSV file
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")

    # Read the file content
    try:
        file_content = await file.read()
        buffer = StringIO(file_content.decode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read the file: {str(e)}")

    # Process CSV file content
    try:
        csv_reader = csv.DictReader(buffer)
        for row in csv_reader:
            # Ensure the row has an 'ID' key
            id = row['ID']
            product_name = row['Product Name']
            input_image_urls = row['Input Image Urls'].split(',')
            new_image_request = ImageProcessRequest(
                    sl_no = id,
                    file_process_id=new_file_request.id,  #
                    product_name=product_name,  # 
                    input_image_urls=input_image_urls,  
                    output_image_urls=[]
                    )
            print("#####",new_image_request)
                     
            try:
                async with SessionLocal() as session: 
                    session.add(new_image_request) 
                    await session.commit()
                    await session.refresh(new_image_request)   
                    await compress_images_endpoint(new_image_request.file_process_id, session)
            except Exception as e:
                raise Exception("failed to insert into db", e)
            
    except csv.Error as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV file: {str(e)}")

    # Close buffer
    buffer.close()

    # Return JSON data
    
    return data

@app.get("/status/{request_id}")
async def get_status(request_id: int):
    print("******",request_id)
    async with SessionLocal() as session:
        status = await crud.get_status(request_id,session)
        if status:
            return {"status": status}
        raise HTTPException(status_code=404, detail="Request ID not found")
