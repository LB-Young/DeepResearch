from typing import Dict, Any, Iterator
from src.DeepResearch.utils.help import AgentResponse
from src.DeepResearch.memory.agent_memory import AgentMemory
from src.DeepResearch.model_client.client import model_client
from src.DeepResearch.utils.constant import SUMMARY_PROMPT_FORMAT


class SummaryAgent:
    def __init__(self, config):
        self.config = config
        if self.config['agents'].get('summary_agent', None) is None:
            raise ValueError("Summary agent configuration cannot be None")
        self.agent_info = self.config['agents']['summary_agent']
        self.model = self.agent_info.get("model", None)

        self.summary_prompt = self.agent_info.get("summary_prompt_format", "")

        self.agent_memory = AgentMemory()

    async def step(self, deep_research_memory=None) -> AgentResponse:
        if deep_research_memory is None:
            raise ValueError("Memory cannot be None")

        # init cur research_agent input info
        await self.agent_memory.clear()
        await self.agent_memory.set_history(await deep_research_memory.get_history())

        deep_research_memorys = await deep_research_memory.get_deep_search_memory()
        deep_research_query = await deep_research_memory.get_query()

        if len(deep_research_query) != 0:
            deep_research_memorys = deep_research_memorys[:-1]
        await self.agent_memory.set_deep_research_memory(deep_research_memorys)
        await self.agent_memory.add_memory(deep_research_query)

        all_history_messages, all_deep_research_messages, all_messages = await self.agent_memory.get_model_messages()

        summary_agent_system_messages = await self.get_summary_agent_system_messages()

        origin_query = await deep_research_memory.get_origin_query()
        summary_query = {
            "role": "user",
            "content": "为我的初始问题：“{origin_query.content}”生成一个完整的回答总结。"
        }

        all_request_messages = all_history_messages + all_deep_research_messages + summary_agent_system_messages + [summary_query]

        response = await model_client.chat(all_request_messages, self.model)
        self.full_content = ""
        for item in response:
            self.full_content += item.choices[0].delta.content
            yield AgentResponse("summary_agent", "running", item.choices[0].delta.content, None)
            
        yield AgentResponse("summary_agent", "cummary finished!", "", deep_research_memory)

    async def get_summary_agent_system_messages(self):
        """
        format the query to be a prompt
        """
        if len(self.summary_prompt.strip()) == 0:
            system_prompt_format = SUMMARY_PROMPT_FORMAT
        else:
            system_prompt_format = self.summary_prompt
        summary_agent_system_messages = [
            {"role": "user", "content": SUMMARY_PROMPT_FORMAT},
            {"role": "assistant", "content": "我已经明确了我的任务，我会在为用户的初始问题生成一个完整的答案。"}
        ]
        return summary_agent_system_messages


