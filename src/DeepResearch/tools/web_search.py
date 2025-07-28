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
            "type": "string",
            "description": "搜索关键词",
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
        keyword = inputs.get("keyword", "")
        
        # 参数校验
        if not keyword:
            raise Exception("搜索关键词不能为空")
            
        try:
            client = ZhipuAI(api_key=self.api_key)  # 填写您自己的APIKey
            
            response = client.web_search.web_search(
                    search_engine="search_std",
                    search_query=keyword,
                    count=3,  # 返回结果的条数，范围1-50，默认10
                    search_domain_filter="www.sohu.com",  # 只访问指定域名的内容
                    search_recency_filter="noLimit",  # 搜索指定日期范围内的内容
                    content_size="high"  # 控制网页摘要的字数，默认medium
                )
            
            all_result = []

            for index, item in enumerate(response.search_result):
                try:  
                    cur_result = f"## 第{index+1}条搜索结果:\n"
                    cur_result += f"### 标题: {item.title}\n"
                    cur_result += f"### 链接: {item.link}\n"
                    cur_result += f"### 内容: {item.content}\n"
                    all_result.append(cur_result)
                except:
                    continue
                    
            return "\n\n".join(all_result)
            
        except Exception as e:
            raise Exception(f"智谱AI搜索失败: {str(e)}") 
