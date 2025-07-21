from src.DeepResearch.agent import CriticAgent, SearchAgent
from src.DeepResearch.memory import AgentMemory
from src.DeepResearch.message import AgentMessage


class DeepResearch:
    def __init__(self, max_steps=10):
        self.max_steps = max_steps
        self.critic_agent = CriticAgent()
        self.search_agent = SearchAgent()

    def execute(self, query, history):
        #   Initialize the agent's state
        self.critic_agent.reset(history)
        self.search_agent.reset(history)

        if isinstance(query, str):
            query = AgentMessage(query)

        cur_step = 1
        finish = False
        while cur_step <= self.max_steps and (not finish):
            #   Critic agent's turn
            critic_response = self.critic_agent.step(query)
            if critic_response is not None:
                yield critic_response

            #   Search agent's turn
            search_response = self.search_agent.step(query)
            if search_response is not None:
                yield search_response

            cur_step += 1
        




