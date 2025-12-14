from abc import ABC, abstractmethod

from mbti_analysis.domain.mbti_analysis import MbtiAnalysis
from mbti_analysis.domain.mbti_result import MbtiResult


class MbtiPort(ABC):

    @abstractmethod
    def train(self, dataset_path: str) -> str:
        pass

    @abstractmethod
    def predict(self, analysis: MbtiAnalysis) -> MbtiResult:
        pass
