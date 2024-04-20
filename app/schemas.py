import re
from pydantic import BaseModel, validator


class User(BaseModel):
    username: str
    email: str
    password: str


    
# Schema para login
class UserLogin(BaseModel):
    username: str
    password: str

class Userreset(BaseModel):
    username: str


class ForgotPassword(BaseModel):
    username: str
    email: str

class ResetRequest(BaseModel):
    username: str