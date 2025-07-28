THINK_PROMPT_FORMAT = """ALL TOOLS:
{tools}


## TOOLS USE
- 当需要调用工具的时候，你需要使用"=>#tool_name: {key:value}"的格式来调用工具,其中参数为严格的json格式，例如"=>#send_email: {subject: 'Hello', content: 'This is a test email'}"。
- 每一次回答，你只能调用一个工具，不能同时调用多个工具。
"""

ACT_PROMPT_FORMAT = """You are a search agent. Your task is to perform actions based on the information gathered."""
