from fastapi import FastAPI, UploadFile, File, HTTPException
from app.database import engine, Base
import csv 
from io import StringIO 
from app.database import SessionLocal
from app.models import ImageProcessRequest, FileProcessRequest
from app.utils import compress_images_endpoint
from app.utils import get_file_status

app = FastAPI()

# Creating database tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await create_tables()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    data = {}
    new_file_request = FileProcessRequest(status="INPROGRESS")

    async with SessionLocal() as session: 
        session.add(new_file_request)
        await session.commit()
        await session.refresh(new_file_request)
        data["file_id"] = new_file_request.id

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")

    try:
        file_content = await file.read()
        buffer = StringIO(file_content.decode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read the file: {str(e)}")

    try:
        csv_reader = csv.reader(buffer)

        for row in csv_reader:
            id = row[0]  # First column is 'ID'
            product_name = row[1]  # Second column is 'Product Name'

            # All remaining columns are part of 'Input Image Urls'
            input_image_urls = row[2:] 
            input_image_urls = input_image_urls[0].split(',')
            new_image_request = ImageProcessRequest(
                    sl_no = id,
                    file_process_id=new_file_request.id,
                    product_name=product_name,
                    input_image_urls=input_image_urls,  
                    output_image_urls=[]
                    )

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

    buffer.close()

    return data

@app.get("/status/{request_id}")
async def get_status(request_id: int):
    async with SessionLocal() as session:
        status = await get_file_status(request_id,session)
        if status:
            return {"status": status}
        raise HTTPException(status_code=404, detail="Request ID not found")
