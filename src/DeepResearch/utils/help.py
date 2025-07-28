class AgentResponse:
    def __init__(self, agent_name, status, content, agent_memory=None):
        """
        Initialize the AgentResponse object.

        Args:
            status (str): The status of the response.
            content (str): The content of the response. yield to frontend
            agent_memory (dict): An object representing the agent's memory.
        """
        self.name = agent_name
        self.status = status
        self.content = content
        self.agent_memory = agent_memory
