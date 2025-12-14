from mbti_analysis.domain.mbti_analysis import MbtiAnalysis
from mbti_analysis.domain.port.mbti_port import MbtiPort


class PredictMbtiUseCase:

    def __init__(self, mbti_port: MbtiPort):
        self.mbti_port = mbti_port

    def execute(self, user_text: str):
        analysis = MbtiAnalysis(user_text=user_text)
        return self.mbti_port.predict(analysis)
