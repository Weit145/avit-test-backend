from pydantic import BaseModel


class Auth(BaseModel):
    uuid:str
    role:str
    pass

class JWT(BaseModel):
    jwt: str