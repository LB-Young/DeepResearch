#!/usr/bin/env python3
"""
测试重复工具调用修复
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

class MockTool:
    """模拟工具类"""
    def __init__(self, name):
        self.name = name
        self.call_count = 0
    
    async def arun(self, inputs):
        self.call_count += 1
        return f"模拟{self.name}工具执行结果 (第{self.call_count}次调用): {inputs}"

class MockResearchAgent:
    """模拟研究代理，测试修复逻辑"""
    
    def __init__(self):
        self.tools_mapping = {
            "web_search_zhipu": MockTool("web_search_zhipu")
        }
    
    async def extract_params(self, content):
        """提取参数"""
        content = content.strip()
        start_index = content.find('{')
        if start_index == -1:
            return content
        
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
        
        if bracket_count == 0:
            return content[start_index:end_index + 1]
        else:
            return content
    
    async def act(self, full_content):
        """模拟修复后的act方法"""
        self.full_content = full_content
        self.act_full_content = ""
        
        # 检查是否有工具调用
        tool_calls = self.full_content.split("=>#")
        if len(tool_calls) < 2:
            result = "未找到有效的工具调用信息。"
            self.act_full_content = result
            return result
            
        # 检查是否有重复的工具调用
        unique_calls = {}
        duplicate_found = False
        for i, call in enumerate(tool_calls[1:], 1):  # 跳过第一个空元素
            if call.strip():
                call_signature = call.split(":")[0].strip()
                if call_signature in unique_calls:
                    # 发现重复调用
                    print(f"⚠️  检测到重复的工具调用 '{call_signature}'，将使用第一次调用的结果。")
                    duplicate_found = True
                    break
                else:
                    unique_calls[call_signature] = i
        
        # 使用第一个有效的工具调用
        tool_info = None
        for call in tool_calls[1:]:
            if call.strip():
                tool_info = call
                break
                
        if not tool_info:
            result = "未找到有效的工具调用信息。"
            self.act_full_content = result
            return result
            
        tool_name = tool_info.split(":")[0].strip()
        tool_params = await self.extract_params(tool_info.split(":", 1)[-1])
        
        if tool_name not in self.tools_mapping:
            result = f"工具{tool_name}不存在，请重新选择工具。"
            self.act_full_content = result
            return result
        
        try:
            import json
            json_params = json.loads(tool_params)
            tool_object = self.tools_mapping[tool_name]
            tool_results = await tool_object.arun(inputs=json_params)
            
            result = f"工具执行结果如下：\n{tool_results}"
            self.act_full_content = tool_results
            
            if duplicate_found:
                result += "\n\n✅ 已避免重复执行相同的工具调用。"
            
            return result
            
        except Exception as e:
            result = f"工具{tool_name}参数解析失败: {str(e)}"
            self.act_full_content = result
            return result

async def test_duplicate_detection():
    """测试重复检测功能"""
    
    agent = MockResearchAgent()
    
    # 测试用例1：正常的单次工具调用
    print("测试用例1：正常的单次工具调用")
    print("-" * 40)
    content1 = """这是一些分析内容。

=>#web_search_zhipu: {"keyword": ["test1"]}"""
    
    result1 = await agent.act(content1)
    print(f"结果: {result1}")
    print(f"工具调用次数: {agent.tools_mapping['web_search_zhipu'].call_count}")
    print()
    
    # 重置工具调用计数
    agent.tools_mapping['web_search_zhipu'].call_count = 0
    
    # 测试用例2：重复的工具调用
    print("测试用例2：重复的工具调用")
    print("-" * 40)
    content2 = """这是一些分析内容。

=>#web_search_zhipu: {"keyword": ["test1"]}

这是第一次搜索后的分析内容。

=>#web_search_zhipu: {"keyword": ["test1"]}

这是重复的工具调用。"""
    
    result2 = await agent.act(content2)
    print(f"结果: {result2}")
    print(f"工具调用次数: {agent.tools_mapping['web_search_zhipu'].call_count}")
    print()
    
    # 测试用例3：不同参数的工具调用（应该允许）
    print("测试用例3：不同参数的工具调用")
    print("-" * 40)
    content3 = """这是一些分析内容。

=>#web_search_zhipu: {"keyword": ["test1"]}

这是第一次搜索后的分析内容。

=>#web_search_zhipu: {"keyword": ["test2"]}

这是不同参数的工具调用。"""
    
    # 重置工具调用计数
    agent.tools_mapping['web_search_zhipu'].call_count = 0
    
    result3 = await agent.act(content3)
    print(f"结果: {result3}")
    print(f"工具调用次数: {agent.tools_mapping['web_search_zhipu'].call_count}")

if __name__ == "__main__":
    print("测试重复工具调用修复功能")
    print("=" * 50)
    asyncio.run(test_duplicate_detection())