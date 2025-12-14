from fastapi import APIRouter

from mbti_analysis.adapter.input.web.request.mbti_predict_request import MbtiPredictRequest
from mbti_analysis.adapter.input.web.request.mbti_train_request import MbtiTrainRequest
from mbti_analysis.adapter.output.repository.mbti_repository_impl import MbtiRepositoryImpl
from mbti_analysis.application.usecase.predict_mbti_usecase import PredictMbtiUseCase
from mbti_analysis.application.usecase.train_mbti_model_usecase import TrainMbtiModelUseCase

mbti_analysis_router = APIRouter()

repo = MbtiRepositoryImpl()
train_usecase = TrainMbtiModelUseCase(repo)
predict_usecase = PredictMbtiUseCase(repo)

@mbti_analysis_router.post("/train")
def train_mbti(req: MbtiTrainRequest):
    job_id = train_usecase.execute(req.dataset_path)
    return {"job_id": job_id}

@mbti_analysis_router.post("/predict")
def predict_mbti(req: MbtiPredictRequest):
    result = predict_usecase.execute(req.text)
    return {
        "mbti": result.mbti,
        "explanation": result.explanation
    }
