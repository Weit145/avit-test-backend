from pydantic import BaseModel
import uuid


class Auth(BaseModel):
    uuid:uuid.UUID
    role:str
    pass

class JWT(BaseModel):
    jwt: str