from openai import OpenAI

from src.DeepResearch.config.config import CONFIG

class ModelClient:
    def __init__(self, models_config):
        if models_config is None:
            raise ValueError("models cannot be None")
        self.models_config = models_config
        self.models_valid = {}
        for item in self.models_config:
            if item.get("model_platform", None) is None or item.get("platform_api_key", None) is None:
                raise ValueError("Platform and API key must be provided for each model")

            cur_client = self.get_client(item["model_platform"], item["platform_api_key"])

            for model_name in item.get("models", []):
                self.models_valid[model_name] = cur_client

    def get_client(self, platform=None, api_key=None):
        if platform == "deepseek":
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        elif platform == "openrouter":
            client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        elif platform == "aliyun":
            client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        elif platform == "moonshot":
            client = OpenAI(api_key=api_key, base_url="https://api.moonshot.cn/v1")
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        return client

    async def chat(self, messages, model_name, temperature=0.7, stream=True):
        client = self.models_valid.get(model_name, None)
        if client is None:
            raise ValueError(f"Model {model_name} is not valid or not supported")
        
        with open("messages.txt", "a", encoding="utf-8") as f:
            f.write(str(messages))
            f.write("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        
        if stream:
            stream = client.chat.completions.create(
                model = model_name,
                messages = messages,
                temperature = temperature,
                stream=stream, # <-- 注意这里，我们通过设置 stream=True 开启流式输出模式
            )
            return stream
        else:
            response = client.chat.completions.create(
                model = model_name,
                messages = messages,
                temperature = temperature,
            )
            return response.choices[0].message.content

model_client = ModelClient(CONFIG.get("models", None))