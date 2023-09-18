import io

from fastapi import APIRouter, UploadFile, File, Depends

from src.conf.cognito import get_current_user
from src.service.media import S3Service
from src.service.image_process import ImageDetector
from src.service.video_process import VideoDetector

media_router = APIRouter()


@media_router.post("/detect/image")
async def upload_file(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    s3_service = S3Service()
    print(f"user: {current_user}")

    processor = ImageDetector()
    image = file.file.read()
    img_processed = processor.run(image)
    file_processed = processor.nparray_to_bytes(img_processed)

    upload_successful = await s3_service.upload_file_to_s3(file_processed, current_user["username"], file.filename)
    if upload_successful:
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "message": "Processamento iniciado com sucesso"
        }
    else:
        return {"message": "Processamento não iniciado"}


@media_router.post("/detect/video")
async def process_video(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    s3_service = S3Service()
    print(f"user: {current_user}")

    processor = VideoDetector(file.filename)
    video = file.file.read()
    processor.run(video)

    upload_successful = await s3_service.upload_video_to_s3(current_user["username"], file.filename)
    if upload_successful:
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "message": "Processamento iniciado com sucesso"
        }
    else:
        return {"message": "Processamento não iniciado"}
