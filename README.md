# DeepResearch

DeepResearch是一个基于大型语言模型的深度研究助手系统，能够帮助用户进行深入的信息检索、分析和研究工作。

## 项目介绍

DeepResearch采用多代理协作的方式，通过研究代理(Research Agent)和批评代理(Critic Agent)的交互，实现对用户问题的深度探索和持续研究。系统具有以下特点：

- **多轮深度研究**：系统能够自动进行多轮研究，每轮研究都会基于前一轮的结果进行更深入的探索
- **智能工具调用**：研究代理能够根据需要调用外部工具（如网络搜索）获取信息
- **批评式引导**：批评代理会分析当前研究结果，提出更深入的问题，引导研究向更有价值的方向发展
- **可配置性强**：通过配置文件可以灵活设置模型、工具参数等

## 系统架构

DeepResearch主要由以下几个部分组成：

1. **代理模块(Agent)**：
   - 研究代理(ResearchAgent)：负责分析问题、调用工具、整合信息并提供答案
   - 批评代理(CriticAgent)：负责评估研究结果，提出更深入的问题

2. **记忆模块(Memory)**：
   - 管理对话历史和研究过程中的信息

3. **工具模块(Tools)**：
   - 提供网络搜索等外部工具的接口

4. **模型客户端(Model Client)**：
   - 负责与大型语言模型的交互

## 安装指南

### 环境要求

- Python 3.8+
- 相关依赖包

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/DeepResearch.git
cd DeepResearch
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

## 配置说明

DeepResearch通过`config/config.yaml`文件进行配置，主要配置项包括：

### 代理配置

```yaml
agents:
  critic_agent:
    model: "deepseek-chat"  # 批评代理使用的模型
  research_agent:
    model: "deepseek-chat"  # 研究代理使用的模型
    max_steps: 3  # 每次研究的最大步骤数
```

### 工具配置

```yaml
tools:
  web_search_zhipu:
    api_key: ""  # 智谱AI搜索API密钥
    num_results: 2  # 搜索结果数量
```

### 模型配置

```yaml
models:
  - models: ["deepseek-chat"]
    model_platform: "deepseek"
    platform_api_key: ""  # 模型平台API密钥
    temperature: 0.7  # 生成参数
```

## 使用示例

```python
from src.DeepResearch import DeepResearch

# 初始化DeepResearch实例
deep_research = DeepResearch(max_steps=5)

# 执行研究
async def run_research():
    query = "量子计算的最新进展是什么？"
    history = []  # 可以提供历史对话
    
    async for response in deep_research.execute(query, history):
        if isinstance(response, dict) and response.get("status") == "finished":
            print("研究完成:", response.get("steps"))
        else:
            print(response)

# 运行研究
import asyncio
asyncio.run(run_research())
```

## API文档

### DeepResearch类

主要类，用于初始化和执行深度研究。

```python
DeepResearch(max_steps=10)
```

参数:
- `max_steps`: 最大研究步骤数，默认为10

方法:
- `execute(query, history)`: 执行研究，返回异步生成器
  - `query`: 研究问题
  - `history`: 历史对话记录

## 许可证

[在此添加许可证信息]