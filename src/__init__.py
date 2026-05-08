import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile

from src.components.easyocr import Easyocr


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    print("Loading ocr")
    Easyocr()
    print("Ocr Loading Complete")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    ocr = Easyocr()

    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(await file.read())

        result = ocr.reader.readtext(temp_file.name)

        response = []
        for i in range(len(result)):
            coords, text, conf = result[i]

            response.append(
                {
                    "Position": [[int(coord[0]), int(coord[1])] for coord in coords],
                    "Text": text,
                    "Confidence": conf,
                }
            )

    return {"data": response}
