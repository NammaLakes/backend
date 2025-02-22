from pydantic import BaseModel

class EchoRequest(BaseModel):
    message: str

class EchoResponse(BaseModel):
    response: str
