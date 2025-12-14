from mbti_analysis.domain.port.mbti_port import MbtiPort


class TrainMbtiModelUseCase:

    def __init__(self, mbti_port: MbtiPort):
        self.mbti_port = mbti_port

    def execute(self, dataset_path: str) -> str:
        return self.mbti_port.train(dataset_path)
