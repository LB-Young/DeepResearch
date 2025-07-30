# DeepResearch

DeepResearch是一个基于大型语言模型的深度研究助手系统，能够帮助用户进行深入的信息检索、分析和研究工作。

## 项目介绍

DeepResearch采用多代理协作的方式，通过研究代理(Research Agent)、批评代理(Critic Agent)和总结代理(Summary Agent)的交互，实现对用户问题的深度探索和持续研究。系统具有以下特点：

- **多轮深度研究**：系统能够自动进行多轮研究，每轮研究都会基于前一轮的结果进行更深入的探索
- **三代理协作**：研究代理负责信息收集，批评代理进行深度思考，总结代理提供最终总结
- **智能工具调用**：研究代理能够根据需要调用外部工具，支持多关键词并行网络搜索获取信息
- **批评式引导**：批评代理会分析当前研究结果，提出更深入的问题，引导研究向更有价值的方向发展
- **Web界面支持**：提供基于Streamlit的友好Web界面，支持实时研究进展显示
- **可配置性强**：通过配置文件可以灵活设置模型、工具参数等

## 系统架构

DeepResearch主要由以下几个部分组成：

1. **代理模块(Agent)**：
   - 研究代理(ResearchAgent)：负责分析问题、调用工具、整合信息并提供答案
   - 批评代理(CriticAgent)：负责评估研究结果，提出更深入的问题
   - 总结代理(SummaryAgent)：负责对整个研究过程进行总结和归纳

2. **记忆模块(Memory)**：
   - DeepResearchMemory：管理对话历史、研究过程中的信息和代理间的消息传递

3. **工具模块(Tools)**：
   - 智谱AI网络搜索工具(WebSearchZhipuTool)：支持多关键词并行搜索，为每个关键词独立获取搜索结果

4. **模型客户端(Model Client)**：
   - 负责与大型语言模型的交互，支持多种模型平台

5. **前端界面(Frontend)**：
   - 基于Streamlit的Web界面，提供友好的用户交互体验
   - 支持实时研究进展显示和历史对话管理

## 安装指南

### 环境要求

- Python 3.8+
- 相关依赖包：
  - flask>=2.0.0
  - aiohttp>=3.8.0
  - streamlit>=1.28.0
  - markdown>=3.4.0
  - zhipuai (智谱AI SDK)
  - PyYAML

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

3. 配置API密钥
编辑 `src/DeepResearch/config/config.yaml` 文件，填入您的API密钥：
```yaml
tools:
  web_search_zhipu:
    api_key: "your_zhipu_api_key_here"

models:
  - models: ["deepseek-chat"]
    model_platform: "deepseek"
    platform_api_key: "your_deepseek_api_key_here"
```

## 配置说明

DeepResearch通过`src/DeepResearch/config/config.yaml`文件进行配置，主要配置项包括：

### 代理配置

```yaml
agents:
  critic_agent:
    model: "deepseek-chat"  # 批评代理使用的模型
  research_agent:
    model: "deepseek-chat"  # 研究代理使用的模型
    max_steps: 3  # 每次研究的最大步骤数
  summary_agent:
    model: "deepseek-chat"  # 总结代理使用的模型
```

### 工具配置

```yaml
tools:
  web_search_zhipu:
    api_key: ""  # 智谱AI搜索API密钥
    num_results: 5  # 每个关键词的搜索结果数量
```

#### 智谱AI网络搜索工具说明

- **多关键词搜索**：工具接受关键词列表作为输入，为每个关键词独立进行搜索
- **结果分组**：搜索结果按关键词分组显示，便于区分不同关键词的搜索内容
- **智能分配**：系统会根据关键词数量智能分配每个关键词的搜索结果数量
- **语义完整性**：建议确保每个关键词具有完整的语义，以获得更准确的搜索结果

### 模型配置

```yaml
models:
  - models: ["deepseek-chat"]
    model_platform: "deepseek"
    platform_api_key: ""  # 模型平台API密钥
    temperature: 0.7  # 生成参数
```

### 全局配置

系统支持通过外部配置文件覆盖默认配置。如果存在 `/Users/liubaoyang/Documents/YoungL/project/tmp_project/deep_research_config.yaml`，系统将优先使用该配置文件。

## 使用示例

### 方式一：Web界面（推荐）

启动Web界面：
```bash
python start_frontend.py
```

然后在浏览器中访问 `http://localhost:8501` 即可使用友好的Web界面进行研究。

### 方式二：命令行使用

```python
import asyncio
import sys
import os

# 添加项目路径
project_root = '/path/to/your/DeepResearch'
sys.path.append(project_root)

from src.DeepResearch.deep_research import DeepResearch

# 初始化DeepResearch实例
deep_research = DeepResearch()

async def main():
    query = "中国新能源行业在未来五年的发展趋势"
    history = []
    
    async for response in deep_research.execute(query=query, history=history):
        print(response, end="")

# 运行研究
asyncio.run(main())
```

### 网络搜索工具使用

智谱AI网络搜索工具现在支持多关键词搜索，系统会自动将复杂查询分解为多个关键词进行并行搜索：

```python
# 工具会自动处理多个相关关键词
# 例如查询"人工智能在医疗领域的应用"可能会被分解为：
# ["人工智能医疗应用", "AI医疗诊断", "机器学习医疗"]

# 每个关键词都会独立搜索，获得更全面的信息覆盖
```

**搜索结果特点**：
- 按关键词分组显示，结构清晰
- 每个关键词独立搜索，避免信息遗漏
- 支持语义完整的关键词，提高搜索准确性
- 自动去重和智能排序

## 研究流程

DeepResearch的研究流程如下：

1. **初始化**：用户输入研究问题
2. **研究循环**：
   - 🔍 **研究步骤** - 研究代理收集信息和分析
   - 🤔 **进一步思考** - 批评代理进行深度思考和质疑
   - 重复上述步骤直到达到最大步骤数或研究完成
3. **研究总结**：总结代理对整个研究过程进行归纳总结
4. **完成**：输出最终研究结果

## API文档

### DeepResearch类

主要类，用于初始化和执行深度研究。

```python
DeepResearch()
```

配置通过 `config.yaml` 文件进行，包括：
- `max_steps`: 最大研究步骤数，从配置文件读取，默认为5

方法:
- `execute(query, history)`: 执行研究，返回异步生成器
  - `query`: 研究问题（字符串）
  - `history`: 历史对话记录（列表）
  - 返回：异步生成器，实时输出研究进展



## 故障排除

### 常见问题

1. **导入错误**：确保项目路径正确添加到 `sys.path`
2. **API密钥错误**：检查配置文件中的API密钥是否正确设置
3. **依赖缺失**：运行 `pip install -r requirements.txt` 安装所有依赖
4. **配置文件不存在**：确保 `src/DeepResearch/config/config.yaml` 文件存在

### Web界面问题

如果Web界面无法启动：
1. 确保Streamlit已安装：`pip install streamlit>=1.28.0`
2. 检查端口8501是否被占用
3. 确保所有依赖都已正确安装