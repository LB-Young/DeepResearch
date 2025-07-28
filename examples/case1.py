import asyncio
import sys
import os
# 将项目根目录添加到 sys.path
project_root = '/Users/liubaoyang/Documents/YoungL/project/DeepResearch'
sys.path.append(project_root)

from src.DeepResearch.deep_research import DeepResearch


deep_research = DeepResearch(max_steps=10)

async def main():
    question = """中国新能源行业在未来五年的发展趋势"""
    history = []
    async for response in deep_research.execute(query=question, history=history):
        print(response, end="")
    pass


asyncio.run(main())
