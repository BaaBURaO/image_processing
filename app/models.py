from sqlalchemy import Column, String, Integer
from app.database import Base
from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy import Column, String, ForeignKey, ARRAY
from sqlalchemy.orm import relationship

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.database import Base

class FileProcessRequest(Base):
    __tablename__ = "file_process_requests"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Integer primary key with auto-increment
    status = Column(String)  # Status of processing (e.g., 'pending', 'completed')

    # Relationship to link to ImageProcessRequest
    images = relationship("ImageProcessRequest", back_populates="file_process")

class ImageProcessRequest(Base):
    __tablename__ = "image_process_requests"
    
    sl_no = Column(String, index=True, primary_key=True)  # Unique request ID as part of composite key
    file_process_id = Column(Integer, ForeignKey('file_process_requests.id'), index=True, primary_key=True)  # Foreign key and part of composite key
    product_name = Column(String, index=True)  # Product name associated with images
    input_image_urls = Column(ARRAY(String))  # List of input image URLs
    output_image_urls = Column(ARRAY(String))  # List of output image URLs

    # Relationship to link back to FileProcessRequest
    file_process = relationship("FileProcessRequest", back_populates="images")
