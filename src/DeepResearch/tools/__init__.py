from .web_search import WebSearchZhipuTool
from .get_url_content import JinaReadUrlsTool

TOOLS_MAPPING = {
    "web_search_zhipu": WebSearchZhipuTool,
    "jina_read_urls": JinaReadUrlsTool
}