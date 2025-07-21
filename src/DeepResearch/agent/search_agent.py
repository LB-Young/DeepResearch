from typing import Any, Coroutine, Dict, Iterator
from base_agent import BaseAgent
from DeepResearch.memory.agent_memory import AgentMemory

class SearchAgent(BaseAgent):
    def __init__(self, config, tools=None):
        self.config = config
        self.memory = AgentMemory()
        if tools is not None:
            self.init_tools(tools)

    def init_tools(self, tools):
        self.tools_mapping = {}
        self.tools_call_format = []
        for key, value in tools.items():
            tools_proerties = {}
            required_params = []
            for param_key, param_value in value["object"].inputs.items():
                tools_proerties[param_key] = {
                            "type": param_value['type'],
                            "description": param_value['description']
                    }
                if param_value['required']:
                    required_params.append(param_key)

            self.tools_mapping[key] = value["object"]

            self.tools_call_format.append({
                                "type": "function",
                                "function": {
                                    "name": value["object"].name,
                                    "description": value["object"].description,
                                    "parameters": {
                                        "type": "object",
                                        "properties": tools_proerties,
                                        "required": required_params
                                    },
                                }
                            })
 
    def execute(self, messages=None):
        self.memory.add_memory(messages=messages)

        max_steps = self.config.get("max_steps", 10)
        step = 0

        while step < max_steps:
            step += 1

            self.think(memory=self.memory)
            self.act(memory=self.memory)
            
            current_memory = self.memory.get_memory()
            if current_memory:
                yield current_memory

        return self.memory.get_memory()

    def think(self, memory=None):
        pass

    def act(self, memory=None):
        pass
    
