from typing import Dict, Any, List, Optional
from crewai_tools import SerperDevTool, YoutubeChannelSearchTool, GithubSearchTool
import os

TOOL_REGISTRY: Dict[str, type] = {
    'WebSearchTool': SerperDevTool,
    'YoutubeChannelTool': YoutubeChannelSearchTool,
    'GithubSearchTool': GithubSearchTool
}

TOOL_CONFIG: Dict[str, Dict[str, Any]] = {
    'WebSearchTool': {
        'country': 'kr',
        'locale': 'ko'
    },
    'GithubSearchTool': {
        'gh_token': os.getenv('GH_TOKEN'),
        'content_types': ['code', 'issue']
    }
}

def create_tool_instance(name: str) -> Optional[Any]:
    tool_class = TOOL_REGISTRY.get(name)
    if not tool_class:
        return None

    try:
        config = TOOL_CONFIG.get(name)

        tool_instance = tool_class(**config) if config else tool_class()
        return tool_instance
    except Exception as e:
        print(f"Failed to create {name}: {str(e)}")
        return None

def get_tool_instances(tool_configs: List[Dict[str, Any]]) -> List[Any]:
    tool_instances = []

    if not tool_configs:
        return tool_instances
    
    for tool_config in tool_configs:
        if not isinstance(tool_config, dict):
            print(f"Invalid tool config: {tool_config}")
            continue

        tool_name = tool_config.get('name')

        if not tool_name:
            print(f"Invalid tool name: {tool_config}")
            continue

        tool_instance = create_tool_instance(tool_name)

        if tool_instance:
            tool_instances.append(tool_instance)

    return tool_instances
