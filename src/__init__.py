import base64
import tempfile
from contextlib import asynccontextmanager
from typing import List

import cv2
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


@app.post("/uploadfile")
async def create_upload_file(files: List[UploadFile]):
    ocr = Easyocr()

    images = []
    all_data = []
    for file in files:
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(await file.read())
            temp_file.flush()

            image = cv2.imread(temp_file.name)
            if image is None:
                all_data.append([])
                images.append(None)
                continue

            result = ocr.reader.readtext(temp_file.name)

            response = []
            for i in range(len(result)):
                coords, text, conf = result[i]

                response.append(
                    {
                        "Position": [
                            [int(coord[0]), int(coord[1])] for coord in coords
                        ],
                        "Text": text,
                        "Confidence": conf,
                    }
                )

                text_top_left_coord = (int(coords[0][0]), int(coords[0][1]))
                text_bottom_right_coord = (int(coords[2][0]), int(coords[2][1]))

                cv2.rectangle(
                    image, text_top_left_coord, text_bottom_right_coord, (0, 0, 255), 5
                )

            all_data.append(response)
            _, buffer = cv2.imencode(".jpeg", image)
            images.append(base64.b64encode(buffer).decode("utf-8"))

    return {"data": all_data, "images": images}
