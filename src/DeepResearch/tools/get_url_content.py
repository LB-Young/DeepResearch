import aiohttp
import asyncio
import os
import hashlib
import json
import sys
from datetime import datetime
from typing import Dict, Any, Iterator, Union, List, Optional
from .base_tool import Tool

# 添加src目录到系统路径以导入load_local_api_keys模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class JinaReadUrlsTool(Tool):
    """Jina URL读取工具"""
    
    name = "jina_read_urls"  # 工具名称
    description = "使用Jina Reader API获取网页内容"  # 工具描述
    
    # 工具输入参数定义
    inputs = {
        "urls": {
            "type": "list",
            "description": "待读取的URL列表，如['url1','url2',……]，每个URL会单独进行内容获取",
            "required": True
        }
    }
    
    # 工具输出定义
    outputs = {
        "url_contents": {
            "type": "string",
            "description": "URL内容结果"
        }
    }
    
    # 工具属性
    properties = {}
    
    # 定义缓存目录
    CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("api_key", "")
        self.cache_hours = config.get("cache_hours", 24)  # 缓存有效期，默认24小时
        # 确保缓存目录存在
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    async def arun(self, inputs: Dict[str, Any], properties: Dict[str, Any] = {}) -> Iterator[Dict[str, Any]]:
        # 从输入中提取参数
        urls = inputs.get("urls", [])
        
        # 参数校验
        if not urls or not isinstance(urls, list):
            raise Exception("URL列表不能为空且必须是列表格式")
        
        try:
            all_result = []
            total_result_count = 0
            
            # 并行处理所有URL
            tasks = [self._fetch_web_content(url, self.api_key) for url in urls]
            contents = await asyncio.gather(*tasks)
            
            # 为每个URL处理结果
            for url_index, (url, content) in enumerate(zip(urls, contents)):
                if not url.strip():
                    continue
                
                # 添加URL分组标题
                all_result.append(f"### URL '{url}' 的内容:")
                
                try:
                    total_result_count += 1
                    cur_result = f"#### 第{total_result_count}条URL内容 (URL: {url}):\n"
                    cur_result += f"##### 链接: {url}\n"
                    cur_result += f"##### 内容: {content}\n"
                    all_result.append(cur_result)
                except:
                    continue
                
                # 在URL结果之间添加分隔符
                if url_index < len(urls) - 1:
                    all_result.append("\n" + "="*50 + "\n")
            
            return "\n\n".join(all_result)
            
        except Exception as e:
            raise Exception(f"Jina URL读取失败: {str(e)}")
    
    def _get_cache_path(self, url: str) -> str:
        """根据URL生成缓存文件路径"""
        # 使用URL的MD5哈希作为文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.CACHE_DIR, f"{url_hash}.json")
    
    async def _read_cache(self, url: str) -> Optional[str]:
        """从缓存中读取内容，如果缓存文件超过24小时则返回None"""
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # 检查缓存是否过期（24小时）
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    current_time = datetime.now()
                    time_diff = current_time - cache_time
                    
                    # 如果缓存未过期，返回内容
                    if time_diff.total_seconds() < self.cache_hours * 3600:  # 使用配置的缓存时间
                        return cache_data['content']
                    else:
                        print(f"缓存已过期: {url}")
            except Exception as e:
                print(f"读取缓存失败: {str(e)}")
        return None
    
    async def _write_cache(self, url: str, content: str) -> None:
        """将内容写入缓存"""
        cache_path = self._get_cache_path(url)
        try:
            cache_data = {
                'url': url,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入缓存失败: {str(e)}")
    
    async def _fetch_web_content(self, url: str, api_key: Optional[str] = None) -> str:
        """使用Jina Reader API获取网页内容"""
        # 首先尝试从缓存读取
        cached_content = await self._read_cache(url)
        if cached_content is not None:
            return cached_content
    
        # 缓存不存在，从Jina API获取
        jina_url = f"https://r.jina.ai/{url}"
        headers = {}
        if api_key:
            headers["X-API-KEY"] = api_key
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(jina_url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        # 将内容保存到缓存
                        await self._write_cache(url, content)
                        return content
                    else:
                        error_msg = f"获取网页内容失败，状态码: {response.status}"
                        try:
                            error_json = await response.json()
                            error_msg += f", 错误信息: {json.dumps(error_json)}"
                        except:
                            pass
                        return error_msg
            except Exception as e:
                return f"获取网页内容时发生错误: {str(e)}" 