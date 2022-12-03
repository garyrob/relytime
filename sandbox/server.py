from typing import Union

from fastapi import FastAPI
from pydantic import (
    BaseModel,
)  # https://github.com/pydantic/pydantic/issues/1961#issuecomment-759522422
from fastapi.middleware.cors import CORSMiddleware
import boto3
from botocore.exceptions import ClientError

S3_BUCKET = "timestamp1000"

app = FastAPI()

# try this for making code cleaner: https://stackoverflow.com/questions/59929028/python-fastapi-error-422-with-post-request-when-sending-json-data

# https://fastapi.tiangolo.com/tutorial/cors/
origins = [
    "http://localhost",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8001/*",
    "http://127.0.0.1/*",
    "http://localhost/*",
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
    S3.Bucket(S3_BUCKET).put_object(Key=item.hash_str, Body="")
    object_summary = S3.ObjectSummary(S3_BUCKET, item.hash_str)
    print("timestamp: ", object_summary.last_modified)
    return item


@app.get("/verifyHash/{hash_str}")
def verifyHash(hash_str) -> Item:
    print(hash_str)
    # bucket = S3.Bucket("timestamp369")
    # bucket.get_key(hash_str)
    object_summary = S3.ObjectSummary(S3_BUCKET, hash_str)
    try:
        print("timestamp: ", object_summary.last_modified)
        # return object_summary.last_modified
    except ClientError as err:
        print(err.args)
        if "Not Found" in err.args[0]:
            print("Not Found")
            return "Not Found"
        else:
            print("Unknown Error")
            return "Unknown Error"
    else:
        return object_summary.last_modified
