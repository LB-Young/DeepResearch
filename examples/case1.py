import asyncio
import sys
import os
# 将项目根目录添加到 sys.path
project_root = '/Users/liubaoyang/Documents/YoungL/project/DeepResearch'
sys.path.append(project_root)

from src.DeepResearch.deep_research import DeepResearch


deep_research = DeepResearch()

async def main():
    question = """meta将在2025年09月将要发布的ai眼镜是什么型号？这款产品的生产合作商有哪些？给我一个分析报告。"""
    history = []
    
    with open(f'examples/reports/{question}.md', 'w', encoding='utf-8') as f:
        async for response in deep_research.execute(query=question, history=history):
            print(response, end="")
            f.write(response)
    pass


asyncio.run(main())
