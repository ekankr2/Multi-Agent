from mbti_analysis.domain.mbti_analysis import MbtiAnalysis
from mbti_analysis.domain.mbti_result import MbtiResult
from mbti_analysis.domain.port.mbti_port import MbtiPort
from mbti_analysis.infrastructure.client.openai_client import OpenAiClient
import json


class MbtiRepositoryImpl(MbtiPort):

    def __init__(self):
        self.client = OpenAiClient()
        self.model_name = "gpt-4o-mini"  # 나중에 ft 모델로 교체 가능

    def train(self, dataset_path: str) -> str:
        file = self.client.upload_dataset(dataset_path)
        job = self.client.create_fine_tune_job(file.id)
        return job.id

    def predict(self, analysis: MbtiAnalysis) -> MbtiResult:
        prompt = f"""
너는 MBTI 분류기다.

[규칙]
1. 반드시 16개 MBTI 중 하나만 선택하라.
2. "UNKNOWN", "가능성", "둘 중 하나", "추가 정보 필요" 같은 표현은 절대 사용하지 마라.
3. 가장 가능성이 높은 하나를 무조건 확정해서 선택하라.
4. 출력은 반드시 아래 JSON 형식만 허용한다.
5. JSON 외의 다른 출력은 절대 하지 마라.

[출력 형식]
{{
  "mbti": "INTJ",
  "explanation": "왜 이 MBTI인지 간단한 근거"
}}

[사용자 입력]
{analysis.user_text}
"""

        response = self.client.chat(self.model_name, prompt)
        content = response.choices[0].message.content.strip()

        try:
            data = json.loads(content)
            mbti = data.get("mbti", "UNKNOWN")
            explanation = data.get("explanation", "")
        except json.JSONDecodeError:
            # GPT가 규칙 어겨도 서버는 절대 안 죽게 방어
            mbti = "UNKNOWN"
            explanation = content

        return MbtiResult(
            mbti=mbti,
            explanation=explanation
        )
