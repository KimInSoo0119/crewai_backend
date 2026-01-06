"""
Crew AI CLI Runner
사용법: python cli/runner.py configs/crew_config.yaml
"""
import sys
import yaml
import os
import re
from pathlib import Path
from crewai import Agent, Task, Crew, LLM, Process

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.service.crew.tool_manager import get_tool_instances

# 환경변수 치환 및 YAML 파일로드
def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config_str = f.read()
    
    def replace_env(match):
        var = match.group(1)
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Environment variable '{var}' not found")
        return value
    
    config_str = re.sub(r'\$\{(\w+)\}', replace_env, config_str)
    return yaml.safe_load(config_str)

# Agent 실행
def create_agents(config):
    agents = {}
    
    for cfg in config['agents']:
        model_cfg = config['models'][cfg['model']]
        
        llm = LLM(
            model=f"openai/{model_cfg['name']}",
            api_key=model_cfg['api_key'],
            base_url=model_cfg.get('api_base_url')
        )
        
        tools = get_tool_instances(cfg.get('tools', []))
        
        agent = Agent(
            role=cfg['role'],
            goal=cfg['goal'],
            backstory=cfg['backstory'],
            llm=llm,
            tools=tools if tools else None
        )
        
        agents[cfg['id']] = agent
    
    return agents

# Task 생성 및 의존성 설정
def create_tasks(config, agents):
    tasks = {}
    dependencies = {}
    
    # Task 생성
    for cfg in config['tasks']:
        task = Task(
            description=cfg['description'],
            expected_output=cfg['expected_output'],
            agent=agents[cfg['agent']]
        )
        
        tasks[cfg['id']] = task
        dependencies[cfg['id']] = cfg.get('context', [])
    
    # Context 설정
    for task_id, context_ids in dependencies.items():
        if context_ids:
            tasks[task_id].context = [tasks[cid] for cid in context_ids]
    
    # 의존성 순서로 정렬
    sorted_ids = []
    visited = set()
    
    def visit(tid):
        if tid in visited:
            return
        visited.add(tid)
        for dep in dependencies.get(tid, []):
            visit(dep)
        sorted_ids.append(tid)
    
    for tid in tasks.keys():
        visit(tid)
    
    return tasks, sorted_ids

# crew 실행
def execute_crew(config, agents, tasks, sorted_ids):
    tasks_list = [tasks[tid] for tid in sorted_ids]
    
    process_map = {
        'sequential': Process.sequential,
        'hierarchical': Process.hierarchical
    }
    
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks_list,
        process=process_map.get(config['execution'].get('process', 'sequential')),
        verbose=config['execution'].get('verbose', True)
    )
    
    result = crew.kickoff()
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli/runner.py <config.yaml>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    if not Path(config_path).exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    try:
        print(f"\n Loading: {config_path}\n")
        
        config = load_config(config_path)
        agents = create_agents(config)
        tasks, sorted_ids = create_tasks(config, agents)
        
        print(f"Executing {len(sorted_ids)} tasks...\n")
        
        result = execute_crew(config, agents, tasks, sorted_ids)
        
        print(f"\n Result:\n{result}\n")
        
    except Exception as e:
        print(f"\n Error: {str(e)}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()