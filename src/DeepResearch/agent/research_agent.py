import json
from typing import Any, Coroutine, Dict, Iterator
from .base_agent import BaseAgent
from src.DeepResearch.memory.agent_memory import AgentMemory
from src.DeepResearch.message.agent_message import AgentMessage
from src.DeepResearch.tools import TOOLS_MAPPING
from src.DeepResearch.model_client.client import model_client
from src.DeepResearch.utils.help import AgentResponse
from src.DeepResearch.utils.constant import THINK_PROMPT_FORMAT, ACT_PROMPT_FORMAT


class ResearchAgent(BaseAgent):
    def __init__(self, config):
        self.config = config
        if self.config['agents'].get('research_agent', None) is None:
            raise ValueError("Search agent configuration cannot be None")
        self.agent_info = self.config['agents']['research_agent']
        self.model = self.agent_info.get("model", None)
        if self.model is None:
            raise ValueError("Model must be specified for the search agent")
        self.think_prompt = self.agent_info.get("think_prompt_format", "")
        self.act_prompt = self.agent_info.get("act_prompt_format", "")
        self.tools = self.config.get("tools", {})
        self.agent_tools_mapping = self.set_tools(self.tools)
        self.init_tools(self.agent_tools_mapping)
        self.agent_memory = AgentMemory()

    def set_tools(self, tools):
        self.agent_tools_mapping = {}
        for key, value in tools.items():
            if key not in TOOLS_MAPPING:
                raise ValueError(f"Tool {key} is not defined in TOOLS_MAPPING")
            self.agent_tools_mapping[key] = TOOLS_MAPPING[key](value)
        return self.agent_tools_mapping

    def init_tools(self, tools):
        self.tools_mapping = {}
        self.tools_call_format = []
        for key, value in tools.items():
            tools_proerties = {}
            required_params = []
            for param_key, param_value in value.inputs.items():
                tools_proerties[param_key] = {
                            "type": param_value['type'],
                            "description": param_value['description']
                    }
                if param_value['required']:
                    required_params.append(param_key)

            self.tools_mapping[key] = value

            self.tools_call_format.append({
                                "type": "function",
                                "function": {
                                    "name": value.name,
                                    "description": value.description,
                                    "parameters": {
                                        "type": "object",
                                        "properties": tools_proerties,
                                        "required": required_params
                                    },
                                }
                            })

    async def step(self, deep_research_memory=None):
        """
        step: this is a origin user query to be researched or a critic agent query to be researched further
        """
        if deep_research_memory is None:
            raise ValueError("Memory cannot be None")

        # init cur research_agent input info
        self.agent_memory.clear()
        self.agent_memory.set_history(deep_research_memory.get_history())
        deep_research_memorys = deep_research_memory.get_deep_search_memory()
        deep_research_query = deep_research_memory.get_query()
        if deep_research_query != 0:
            deep_research_memorys = deep_research_memorys[:-1]
        self.agent_memory.set_deep_research_memory(deep_research_memorys)
        self.agent_memory.add_memory(deep_research_query)

        max_steps = self.agent_info.get("max_steps", 10)
        step = 0

        while step < max_steps:
            step += 1

            # reason step
            reason_response = self.reason()
            async for item in reason_response:
                yield_status = item['status']
                yield_content = item['content']

                # "finished!" status represent the complete of this deep_research query instead of cur reason step
                if yield_status != "finished!":
                    yield AgentResponse("research_agent_reason", "reasoning……", yield_content, deep_research_memory)
                else:
                    full_response_content = self.agent_memory.get_full_response_content()
                    # deep_research_memory.add_memory({"role":"assistant", "content":full_response_content})
                    yield AgentResponse("research_agent_reason", "finished!", yield_content, deep_research_memory)
            
            if "=>#" not in self.full_content:
                break
            
            # act step
            act_response = self.act()
            async for item in act_response:
                yield_content = item['content']
                yield AgentResponse("research_agent_act", "act finished!", yield_content, deep_research_memory)
            
            yield AgentResponse("research_agent_act", "finished!", "", deep_research_memory)

    async def reason(self):
        """
        reason step: 
        1. analyze the query of cur deep_research step
        2. consider which tool need to be used
        3. generate the tool input parameters.
        """
        all_history_messages, all_deep_research_messages, all_messages = self.agent_memory.get_model_messages()
        explore_system_messages = await self.get_explore_system_messages()
        all_request_messages = all_history_messages + all_deep_research_messages + explore_system_messages + all_messages
        response = await model_client.chat(all_request_messages, self.model)
        self.full_content = ""
        for item in response:
            self.full_content += item.choices[0].delta.content
            yield {
                "status": "reasoning……",
                "content": item.choices[0].delta.content
            }
        reason_message = AgentMessage(
            role="assistant",
            content=self.full_content,
            message_type="research_agent_reason",
            message_from="research_agent_reason",
            message_to="research_agent_act"
        )
        self.agent_memory.add_memory(reason_message)
        
        yield {
            "status": "finished!",
            "content": ""
        }

    async def act(self):
        """
        act step:
        1. parser the parameters of tool
        2. call the tool and return the response
        """
        tool_info = self.full_content.split("=>#")[-1]
        tool_name = tool_info.split(":")[0]
        tool_params = await self.extract_params(tool_info.split(":", 1)[-1])

        self.act_full_content = ""
        if tool_name.strip() not in self.tools_mapping.keys():
            yield {
                "status": "act finished!",
                "content": f"工具{tool_name}不存在，请重新选择工具。"
            }
            self.act_full_content = f"工具{tool_name}不存在，请重新选择工具。"
        else:
            try:
                json_params = json.loads(tool_params)
                tool_object = self.tools_mapping[tool_name]
                tool_results = await tool_object.arun(inputs = json_params)
                if isinstance(tool_results, str):
                    yield {
                        "status": "acting……",
                        "content": "\n工具执行结果如下：\n"
                    }
                    
                    yield {
                        "status": "act finished!",
                        "content": tool_results
                    }
                    self.act_full_content = tool_results
                else:
                    yield {
                        "status": "acting……",
                        "content": "\n工具执行结果如下：\n"
                    }
                    for result in tool_results:
                        yield {
                            "status": "acting……",
                            "content": result
                        }
                    yield {
                        "status": "act finished!",
                        "content": result
                    }
                    self.act_full_content = result
            except:
                yield {
                    "status": "act finished!",
                    "content": f"工具{tool_name}参数解析失败，请重新生成完整工具调用信息。"
                }
                self.act_full_content = f"工具{tool_name}参数解析失败，请重新生成完整工具调用信息。"

        act_message = AgentMessage(
            role="user",
            content=self.act_full_content,
            message_type="function",
            message_from="research_agent_act",
            message_to="research_agent_reason"
            )
        self.agent_memory.add_memory(act_message)

    async def get_explore_system_messages(self):
        """
        format the query to be a prompt
        """
        system_prompt_format = THINK_PROMPT_FORMAT
        tools_info = ""
        for index, item in enumerate(self.tools_call_format):
            tool_info = str(item).replace("\n", "")
            tools_info += f"{index+1}. {tool_info};\n"
        formatted_system_prompt = system_prompt_format.replace("{tools}", str(tools_info))
        explore_system_messages = [
            {"role": "user", "content": formatted_system_prompt},
            {"role": "assistant", "content": "我会严格遵循要求，思考后作答，并且在生成工具调用信息之后立刻停止,等待工具返回结果。"}
        ]
        return explore_system_messages

    async def extract_params(self, content):
        # 提取content中的json格式内容，去除掉json格式外的内容，注意json的括号匹配
        content = content.strip()
        
        # 找到第一个 { 的位置
        start_index = content.find('{')
        if start_index == -1:
            return content
        
        # 使用栈来匹配括号
        bracket_count = 0
        end_index = start_index
        
        for i in range(start_index, len(content)):
            char = content[i]
            if char == '{':
                bracket_count += 1
            elif char == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    end_index = i
                    break
        
        # 如果括号匹配成功，返回json部分
        if bracket_count == 0:
            return content[start_index:end_index + 1]
        else:
            return content

        

"""
裸车价：280000左右
购置税：24778
保险：8500
装潢、服务费（原厂玻璃膜、行车记录仪、脚垫后备箱垫、五年五次大保养）：3000左右

可以贷款五年，两年提前还款，前两年利息控制在15000左右
"""

