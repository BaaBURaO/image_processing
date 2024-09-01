import csv
from io import StringIO
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Response
from fastapi.responses import StreamingResponse
from app.models import FileProcessRequest

async def get_status(request_id: int, session: AsyncSession) -> Response:
    try:
        # Create the select statement
        stmt = select(FileProcessRequest).where(FileProcessRequest.id == request_id)
        # Execute the statement
        result = await session.execute(stmt)
        record = result.scalars().first()
        # If record is not found, return a specific message
        if not record:
            return "Request ID not found"

        # Handle INPROGRESS status
        if record.status== "INPROGRESS":
            return record.status
        # print(type(record))
        # record=list(record)
        # print("<<<<<<<<<",type(record))
        # Handle SUCCESS status
        if record.status == "SUCCESS":
            # Convert the images data to CSV format
            csv_file = StringIO()
            csv_writer = csv.writer(csv_file)
            # Write the CSV header
            csv_writer.writerow(['S. No.', 'Product Name', 'Input Image Urls', 'Output Image Urls'])
            # Iterate over images and write each as a row
            for image in record.images:
                sl_no = image.sl_no
                product_name = image.product_name
                
                # Convert the input and output URLs list to comma-separated strings
                input_urls = ','.join(image.input_image_urls)
                output_urls = ','.join(image.output_image_urls)
                # Write the data row
                csv_writer.writerow([sl_no, product_name, input_urls, output_urls])
            # Get the CSV content
            csv_content = csv_file.getvalue()
            csv_file.close()
            
            # Return as CSV response
            response = StreamingResponse(
                iter([csv_content]),
                media_type="text/csv"
            )
            response.headers["Content-Disposition"] = f"attachment; filename=record_{request_id}.csv"
            return response
        
        # For other statuses, return the status as a response
        return record.images

    except Exception as e:
        # Handle exceptions
        print(f"Error fetching status: {e}")
        raise HTTPException(status_code=500, detail="Error fetching status")
