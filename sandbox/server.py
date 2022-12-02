from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import boto3

app = FastAPI()

# try this for making code cleaner: https://stackoverflow.com/questions/59929028/python-fastapi-error-422-with-post-request-when-sending-json-data

# https://fastapi.tiangolo.com/tutorial/cors/
origins = [
    "http://localhost",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    hash_str: str


S3 = boto3.resource("s3")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/sendHash/")
def storeHash(item: Item):
    print(item.hash_str)
    S3.Bucket("timestamp369").put_object(Key=item.hash_str, Body="")
    object_summary = S3.ObjectSummary("timestamp369", item.hash_str)
    print("timestamp: ", object_summary.last_modified)
    return item
