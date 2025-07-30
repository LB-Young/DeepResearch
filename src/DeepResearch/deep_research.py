from src.DeepResearch.agent import CriticAgent, ResearchAgent, SummaryAgent
from src.DeepResearch.memory import DeepResearchMemory
from src.DeepResearch.message import AgentMessage
from src.DeepResearch.config.config import CONFIG


class DeepResearch:
    def __init__(self):

        
        self.config = CONFIG
        if self.config is None:
            raise ValueError("Configuration cannot be None")
        if self.config.get("agents", None) is None:
            raise ValueError("Agents configuration cannot be None")
        
        self.max_steps = self.config.get("max_steps", 5)
        if self.max_steps <= 0:
            raise ValueError("max_steps must be greater than 0")

        self.critic_agent = CriticAgent(self.config)
        self.research_agent = ResearchAgent(self.config)
        self.summary_agent = SummaryAgent(self.config)

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
        deep_research_memory.set_origin_query(query_message)
        deep_research_memory.set_history(history)
        cur_step = 1
        while cur_step <= self.max_steps:

            #   Search agent's turn
            yield f"\n\n### 🔍 研究步骤 {cur_step} - 信息收集\n\n"
            
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

            cur_step += 1
            if cur_step > self.max_steps:
                break

            #   Critic agent's turn
            yield f"\n\n### 🤔 研究步骤 {cur_step} - 进一步思考\n\n"
            
            critic_response = self.critic_agent.step(deep_research_memory)
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

            

        yield f"\n\n---\n\n### 研究总结\n\n"

        summary_response = self.summary_agent.step(deep_research_memory)
        summary_response_content = ""
        async for response in summary_response:
            summary_response_content += response.content
            yield response.content
            
        deep_research_memory.add_memory(AgentMessage(
            role="assistant",
            content=summary_response_content,
            message_type="summary_agent",
            message_from="summary_agent",
            message_to="research_agent"
        ))

        yield f"\n\n---\n\n### ✅ 研究完成，共执行了 {cur_step-1} 个步骤，已为您提供全面的研究结果。"

