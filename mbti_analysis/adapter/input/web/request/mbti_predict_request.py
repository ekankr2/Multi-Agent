from pydantic import BaseModel

class MbtiPredictRequest(BaseModel):
    text: str
