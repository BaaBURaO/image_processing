from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models import FileProcessRequest

async def get_status(request_id: int, session: AsyncSession) -> str:
    try:
        # Create the select statement
        stmt = select(FileProcessRequest).where(FileProcessRequest.id == request_id)
        
        # Execute the statement
        result = await session.execute(stmt)
        record = result.scalars().first()
        
        # Return status if record is found
        return record.status if record else "Status not found"
    
    except Exception as e:
        # Handle exceptions
        print(f"Error fetching status: {e}")
        raise HTTPException(status_code=500, detail="Error fetching status")
