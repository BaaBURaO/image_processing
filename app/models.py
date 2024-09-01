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
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    
    # Relationship to link to ImageProcessRequests
    images = relationship("ImageProcessRequest", back_populates="file_process", lazy="selectin")

class ImageProcessRequest(Base):
    __tablename__ = "image_process_requests"

    sl_no = Column(String, index=True, primary_key=True)
    file_process_id = Column(Integer, ForeignKey('file_process_requests.id'), index=True, primary_key=True)  # Foreign key and part of composite key
    product_name = Column(String, index=True)
    input_image_urls = Column(ARRAY(String))
    output_image_urls = Column(ARRAY(String))

    # Relationship to link back to FileProcessRequest
    file_process = relationship("FileProcessRequest", back_populates="images")
