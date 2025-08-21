import requests
import uuid
import json
import sys
import os
from zhipuai import ZhipuAI
from typing import Dict, Any, Iterator, Union
from .base_tool import Tool

# 添加src目录到系统路径以导入load_local_api_keys模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class WebSearchZhipuTool(Tool):
    """智谱AI网络搜索工具"""
    
    name = "web_search_zhipu"  # 工具名称
    description = "使用智谱AI搜索引擎进行网页搜索"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "keyword": {
            "type": "list",
            "description": "搜索列表，如['keyword1','keyword2',……]，每个关键词会单独进行搜索，请确保关键词的语义完整性",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "search_results": {
            "type": "string",
            "description": "搜索结果"
        }
    }
    
    # 工具属性
    properties = {}

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("api_key", "")
        if not self.api_key:
            raise ValueError("API key for Zhipu AI is required")
        self.search_num = config.get("num_results", 5)
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any] = {}) -> Iterator[Dict[str, Any]]:
        # 从输入中提取参数
        keywords = inputs.get("keyword", [])
        
        # 参数校验
        if not keywords or not isinstance(keywords, list):
            raise Exception("搜索关键词列表不能为空且必须是列表格式")
            
        try:
            client = ZhipuAI(api_key=self.api_key)  # 填写您自己的APIKey
            
            all_result = []
            total_result_count = 0
            
            # 为每个关键词进行搜索
            for keyword_index, keyword in enumerate(keywords):
                if not keyword.strip():
                    continue
                    
                response = client.web_search.web_search(
                        search_engine="search_std",
                        search_query=keyword.strip(),
                        count=self.search_num // len(keywords) + 1,   # 返回结果的条数，范围1-50，默认10
                        search_domain_filter="www.sohu.com",  # 只访问指定域名的内容
                        search_recency_filter="noLimit",  # 搜索指定日期范围内的内容
                        content_size="high"  # 控制网页摘要的字数，默认medium
                    )
                
                # 添加关键词分组标题
                all_result.append(f"### 关键词 '{keyword}' 的搜索结果:")
                
                # 处理当前关键词的搜索结果
                for index, item in enumerate(response.search_result):
                    try:  
                        total_result_count += 1
                        cur_result = f"#### 第{total_result_count}条搜索结果 (关键词: {keyword}):\n"
                        cur_result += f"##### 标题: {item.title}\n"
                        cur_result += f"##### 链接: {item.link}\n"
                        cur_result += f"##### 摘要: {item.content}\n"
                        all_result.append(cur_result)
                    except:
                        continue
                        
                # 在关键词结果之间添加分隔符
                if keyword_index < len(keywords) - 1:
                    all_result.append("\n" + "="*50 + "\n")
                    
            return "\n\n".join(all_result)
            
        except Exception as e:
            raise Exception(f"智谱AI搜索失败: {str(e)}") 
