from src.DeepResearch.agent import CriticAgent, ResearchAgent
from src.DeepResearch.memory import DeepResearchMemory
from src.DeepResearch.message import AgentMessage
from src.DeepResearch.config.config import CONFIG


class DeepResearch:
    def __init__(self, max_steps=10):
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than 0")
        
        self.config = CONFIG
        if self.config is None:
            raise ValueError("Configuration cannot be None")
        if self.config.get("agents", None) is None:
            raise ValueError("Agents configuration cannot be None")

        self.max_steps = max_steps

        self.critic_agent = CriticAgent(self.config)
        self.research_agent = ResearchAgent(self.config)

    async def execute(self, query, history):
        if isinstance(query, str):
            query_message = AgentMessage(
                role="user", 
                content=query, 
                message_type="user_input", 
                message_from="user", 
                message_to="research_agent"
            )

        deep_research_memory = DeepResearchMemory()
        deep_research_memory.add_memory([query_message])
        deep_research_memory.set_history(history)

        cur_step = 1
        while cur_step <= self.max_steps:

            #   Search agent's turn
            research_response = self.research_agent.step(deep_research_memory)
            
            research_response_content = ""
            async for response in research_response:
                research_response_content += response.content
                yield response.content

            deep_research_memory.add_memory(AgentMessage(
                role="assistant",
                content=research_response_content,
                message_type="research_agent",
                message_from="research_agent",
                message_to="critic_agent"
            ))
            breakpoint()

            #   Critic agent's turn
            critic_response = await self.critic_agent.step(deep_research_memory)

            critic_response_content = ""
            async for response in critic_response:
                critic_response_content += response.content
                yield response.content
            
            deep_research_memory.add_memory(AgentMessage(
                role="user",
                content=critic_response_content,
                message_type="critic_agent",
                message_from="critic_agent",
                message_to="research_agent"
            ))

            if deep_research_memory.get_finished():
                break

            cur_step += 1
        
        yield {"status": "finished", "steps": f"{self.max_steps} steps completed."}

