from typing import Dict, Any, Iterator
from src.DeepResearch.utils.help import AgentResponse
from src.DeepResearch.memory.agent_memory import AgentMemory
from src.DeepResearch.model_client.client import model_client
from src.DeepResearch.utils.constant import CRITIC_PROMPT_FORMAT


class CriticAgent:
    def __init__(self, config):
        self.config = config
        if self.config['agents'].get('critic_agent', None) is None:
            raise ValueError("Critic agent configuration cannot be None")
        self.agent_info = self.config['agents']['critic_agent']
        self.model = self.agent_info.get("model", None)

        self.critic_prompt = self.agent_info.get("critic_prompt_format", "")

        self.agent_memory = AgentMemory()


    async def step(self, deep_research_memory=None) -> Iterator[Dict[str, Any]]:
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

        assert len(all_messages) == 0, "Critic agent should not have agent messages"

        critic_agent_system_messages = await self.get_critic_agent_system_messages()

        critic_query = {
            "role": "user",
            "content": "请根据我之前的对话，给我一个更深入的问题。"
        }

        all_request_messages = all_history_messages + all_deep_research_messages + critic_agent_system_messages + [critic_query]

        response = await model_client.chat(all_request_messages, self.model)
        self.full_content = ""
        for item in response:
            self.full_content += item.choices[0].delta.content

        if self.full_content.strip() == "completed":
            deep_research_memory.finished = True
            
        yield AgentResponse("critic_agent", "critic finished!", self.full_content, deep_research_memory)

    async def get_critic_agent_system_messages(self):
        """
        format the query to be a prompt
        """
        if len(self.critic_prompt.strip()) == 0:
            system_prompt_format = CRITIC_PROMPT_FORMAT
        else:
            system_prompt_format = self.critic_prompt
        critic_agent_system_messages = [
            {"role": "user", "content": CRITIC_PROMPT_FORMAT},
            {"role": "assistant", "content": "我已经明确了我的角色身份，我会在已有的对话基础上提出更深入的问题。"}
        ]
        return critic_agent_system_messages
