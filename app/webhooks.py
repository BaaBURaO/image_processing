from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhook/")
async def webhook_handler(request: Request):
    json_body = await request.json()
    # Process webhook callback here
    return {"message": "Webhook received"}
