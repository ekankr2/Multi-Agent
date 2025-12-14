from config.openai.config import get_sync_openai_client, get_openai_config


class OpenAiClient:

    def __init__(self):
        self.client = get_sync_openai_client()
        self.config = get_openai_config()

    def upload_dataset(self, dataset_path: str):
        return self.client.files.create(
            file=open(dataset_path, "rb"),
            purpose="fine-tune"
        )

    def create_fine_tune_job(self, file_id: str):
        return self.client.fine_tuning.jobs.create(
            training_file=file_id,
            model=self.config.model
        )

    def chat(self, model_name: str, prompt: str):
        return self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an MBTI analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
