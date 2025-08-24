import asyncio
import sys
import os
# 将项目根目录添加到 sys.path
project_root = '/Users/liubaoyang/Documents/YoungL/project/DeepResearch'
sys.path.append(project_root)

from src.DeepResearch.deep_research import DeepResearch


deep_research = DeepResearch()

async def main():
    question = """新能源汽车行业有哪些值得投资的公司"""
    history = []
    
    with open(f'examples/reports/{question}.md', 'w', encoding='utf-8') as f:
        async for response in deep_research.execute(query=question, history=history):
            print(response, end="")
            f.write(response)
    pass


asyncio.run(main())
