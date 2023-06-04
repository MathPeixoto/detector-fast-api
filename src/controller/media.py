from fastapi import APIRouter, UploadFile, File, Depends

from src.conf.cognito import get_current_user
from src.service.media import S3Service

media_router = APIRouter()


@media_router.post("/media/")  # Requires to be logged in
async def upload_file(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    s3_service = S3Service()
    print(f"user: {current_user}")
    upload_successful = await s3_service.upload_file_to_s3(file)
    if upload_successful:
        return {"filename": file.filename, "content_type": file.content_type, "message": "Upload Successful"}
    else:
        return {"message": "Upload Failed"}
