"""Configuration loader for DeepResearch agents and tools.

This module dynamically loads configuration from config.yaml file
and makes it available as a Python dictionary.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Returns:
        Dict[str, Any]: Parsed configuration dictionary
        
    Raises:
        FileNotFoundError: If config.yaml doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    if os.path.exists("/Users/liubaoyang/Documents/YoungL/project/tmp_project/deep_research_config.yaml"):
        config_path = "/Users/liubaoyang/Documents/YoungL/project/tmp_project/deep_research_config.yaml"
    else:
        config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Global configuration loaded from YAML
CONFIG = load_config()
print(CONFIG)
"""
{
    "agents": {
        "critic_agent": {
            "model": "deepseek-v3"
        },
        "research_agent": {
            "model": "deepseek-v3"
        }
    },
    "tools": {
        "web_search_zhipu": {
            "api_key": "your_serpapi_api_key_here",
            "num_results": 2
        }
    },
    "models": [
        {
            "model": [
                "gpt-4-turbo"
            ],
            "model_platform": "openai",
            "platform_api_key": "your_openai_api_key_here",
            "temperature": 0.7
        },
        {
            "model": [
                "deepseek-v3"
            ],
            "model_platform": "deepseek",
            "platform_api_key": "your_openai_api_key_here",
            "temperature": 0.7
        }
    ]
}
"""