# from sqlalchemy.future import select  # For asynchronous operations
# from fastapi import FastAPI, HTTPException
# from sqlalchemy import Column, Integer, String, create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from PIL import Image
# import aiohttp
# import io
# import os
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.models import ImageProcessRequest, FileProcessRequest
# from sqlalchemy.future import select  # For asynchronous operations
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import sessionmaker
# import aiohttp
# import io
# import os
# import uuid

# import urllib.request
# import uuid

# from google.cloud import storage
# import io
# from PIL import Image

# # Initialize Google Cloud Storage client
# client = storage.Client()
# bucket_name = "your-bucket-name"
# bucket = client.bucket(bucket_name)

# async def upload_image_to_gcs(image: Image, image_name: str) -> str:
#     """Uploads an image to Google Cloud Storage and returns the URL."""
#     blob = bucket.blob(image_name)

#     # Save image to a BytesIO object
#     buffer = io.BytesIO()
#     image.save(buffer, format='JPEG')
#     buffer.seek(0)

#     # Upload the image
#     blob.upload_from_file(buffer, content_type='image/jpeg')
    
#     # Make the image public and return the public URL
#     blob.make_public()
#     return blob.public_url

# async def download_image_from_gcs(image_url: str) -> Image:
#     """Downloads an image from Google Cloud Storage and returns a PIL Image object."""
#     blob = bucket.blob(image_url)
#     image_data = blob.download_as_bytes()
#     return Image.open(io.BytesIO(image_data))

# # FastAPI instance
# app = FastAPI()

# # Utility function to download and compress images
# async def compress_images(image_urls):
#     compressed_image_urls = []
    
#     for image_url in image_urls:
#         try:
#             # Download the image
#             with urllib.request.urlopen(image_url) as response:
#                 image_bytes = response.read()
#                 image = Image.open(io.BytesIO(image_bytes))

#                 # Compress the image
#                 buffer = io.BytesIO()
#                 image.save(buffer, format='JPEG', quality=50)
#                 buffer.seek(0)

#                 # Create a compressed image path
#                 compressed_image_filename = f"compressed_{uuid.uuid4().hex}.jpg"
#                 compressed_image_path = os.path.join('compressed_images', compressed_image_filename)
                
#                 # Save the compressed image locally
#                 if not os.path.exists('compressed_images'):
#                     os.makedirs('compressed_images')
                
#                 with open(compressed_image_path, 'wb') as f:
#                     f.write(buffer.getvalue())
                
#                 # Add to the list of compressed image URLs
#                 # Assuming images are served from a local server, adjust the base URL accordingly
#                 compressed_image_url = f"/compressed_images/{compressed_image_filename}"
#                 compressed_image_urls.append(compressed_image_url)
#         except Exception as e:
#             print(f"Error processing image {image_url}: {e}")
#             continue
    
#     return compressed_image_urls

# # FastAPI route to handle image compression

# async def compress_images_endpoint(file_request: FileProcessRequest, session: AsyncSession):
    
    
#     try:
#         requests = await get_image_process_requests(file_request.id, session)
#         for request in requests:
            
#             stmt = select(ImageProcessRequest).where(
#                 ImageProcessRequest.sl_no == request.sl_no,
#                 ImageProcessRequest.file_process_id == file_request.id
#             )
            
#             result = await session.execute(stmt)
#             image_process_request = result.scalar_one_or_none()
            
#             if image_process_request:
#                 compressed_image_urls = await compress_images (image_process_request.input_image_urls)
                
#                 image_process_request.output_image_urls = compressed_image_urls

            
#         file_std = select(FileProcessRequest).where(
#                 FileProcessRequest.id == file_request.id
#             )
#         result_std = await session.execute(file_std)
#         this_request = result_std.scalar_one_or_none()
#         this_request.status = "SUCCESS" 
#         try:
#             await session.commit()
#         except Exception as e:
#             print("SUCCESS for this file upload")
        
#     #     return {"request_id": request_id, "status": "completed", "compressed_image_urls": compressed_urls}
    
#     except Exception as e:
#         print("success")
        
    


# async def get_image_process_requests(file_process_id: int, session: AsyncSession):
#     try:
#         stmt = select(ImageProcessRequest).where(ImageProcessRequest.file_process_id == file_process_id)
#         result = await session.execute(stmt)
#         image_process_requests = result.scalars().all()
#         return image_process_requests
#     except Exception as e:
#         print(f"E {e}")
#         raise HTTPException(status_code=500, detail=e)
        