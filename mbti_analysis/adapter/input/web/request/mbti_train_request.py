from pydantic import BaseModel

class MbtiTrainRequest(BaseModel):
    dataset_path: str
