from fastapi import APIRouter, UploadFile, File, Depends
from fastapi import BackgroundTasks

from src.conf.cognito import get_current_user
from src.service.image_process import ImageDetector
from src.service.media import S3Service
from src.service.video_process import VideoDetector

media_router = APIRouter()


@media_router.post("/detect/image")
async def upload_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        current_user=Depends(get_current_user)):
    s3_service = S3Service()
    print(f"user: {current_user}")

    def process_and_upload():
        processor = ImageDetector()
        image = file.file.read()
        img_processed = processor.run(image)
        file_processed = processor.nparray_to_bytes(img_processed)

        upload_successful = s3_service.upload_file_to_s3(file_processed, current_user["username"], file.filename)
        if upload_successful:
            print("Image uploaded to S3 successfully")

    background_tasks.add_task(process_and_upload)
    return {"message": "Processamento iniciado com sucesso"}


@media_router.post("/detect/video")
async def process_video(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        current_user=Depends(get_current_user)
):
    s3_service = S3Service()
    print(f"user: {current_user}")

    def process_and_upload():
        processor = VideoDetector(file.filename)
        video = file.file.read()
        processor.run(video)
        upload_successful = s3_service.upload_video_to_s3(current_user["username"], file.filename)
        if upload_successful:
            print("Video uploaded to S3 successfully")

    background_tasks.add_task(process_and_upload)
    return {"message": "Processamento iniciado com sucesso"}


@media_router.get("/download/{filename}")
async def download_file(filename: str, current_user=Depends(get_current_user)):
    s3_service = S3Service()
    print(f"user: {current_user}")

    presigned_url = await s3_service.download_file_from_s3(current_user["username"], filename)

    if presigned_url:
        return {"url": presigned_url}
    else:
        return {"error": "Could not generate URL or file not found"}


@media_router.get("/view/files")
async def view_files(current_user=Depends(get_current_user)):
    s3_service = S3Service()
    print(f"user: {current_user}")

    files = await s3_service.view_files_from_s3(current_user["username"])
    return files
