from crewai import Agent, Task, Crew, LLM
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

def run_crewai_flow(project_id, nodes, edges, id_map):
    load_dotenv()

    API_KEY = os.getenv("HOSTED_VLLM_API_KEY")
    LLM_SERVER_URL = os.getenv("HOSTED_VLLM_API_BASE")  
    MODEL_NAME = os.getenv("HOSTED_VLLM_MODEL_NAME")

    llm = ChatOpenAI(
        api_key=API_KEY,
        base_url=LLM_SERVER_URL,
        model=MODEL_NAME,
        temperature=0.2,
        max_tokens=2000,
    )

    agents_obj = {}
    tasks_obj = {}
    
    for node in nodes:
        db_id = getattr(node, "dbId", None)
        node_id = getattr(node, "id", None)
        node_data = getattr(node, "data", {}) or {}
        node_type = getattr(node, "type", None)
        
        if node_type == 'agent':
            if db_id:
                pass  
            else:
                db_id = id_map.get(node_id)
                if db_id is None:
                    raise ValueError(f"Unable to determine db_id for agent node: {node_id}")
            
            role = node_data.get('role', '') or 'Agent'
            goal = node_data.get('goal', '') or 'Complete assigned tasks'
            backstory = node_data.get('backstory', '') or 'You are a helpful assistant'
            
            try:
                agent = Agent(
                    role = role,
                    goal = goal,
                    backstory = backstory,
                    llm = llm
                )
                agents_obj[db_id] = agent
            except Exception as e:
                raise ValueError(f"Failed to create agent with db_id {db_id}: {str(e)}")

    for node in nodes:
        db_id = getattr(node, "dbId", None)
        node_id = getattr(node, "id", None)
        node_data = getattr(node, "data", {}) or {}
        node_type = getattr(node, "type", None)
        
        if node_type == 'task':
            if db_id:
                pass  
            else:
                db_id = id_map.get(node_id)
                if db_id is None:
                    raise ValueError(f"Unable to determine db_id for task node: {node_id}")
            
            description = node_data.get('description', '') or 'Complete the task'
            expected_output = node_data.get('expected_output', '') or 'Task completed'
            
            try:
                task = Task(
                    description = description,
                    expected_output = expected_output,
                    agent = None  
                )
                tasks_obj[db_id] = task
            except Exception as e:
                raise ValueError(f"Failed to create task with db_id {db_id}: {str(e)}")

    for edge in edges:
        source = getattr(edge, "source", None)
        target = getattr(edge, "target", None)

        if source in id_map:
            source_id = id_map[source]
        else:
            _, source_id = source.split("-", 1)  
            source_id = int(source_id)

        if target in id_map:
            target_id = id_map[target]
        else:
            _, target_id = target.split("-", 1)  
            target_id = int(target_id)

        source_agent = agents_obj.get(source_id)
        source_task = tasks_obj.get(source_id)
        target_task = tasks_obj.get(target_id)
        target_agent = agents_obj.get(target_id)

        if source_agent and target_task:
            target_task.agent = source_agent
        elif source_task and target_task:
            source_task.add_next(target_task)

    agents_list = list(agents_obj.values())
    tasks_list = list(tasks_obj.values())

    try:
        crew = Crew(
            agents=agents_list,
            tasks=tasks_list,
            verbose=True
        )
    except Exception as e:
        raise ValueError(f"Failed to create Crew: {str(e)}")

    try:
        result = crew.kickoff()
        print(f"Crew execution completed. Result: {result}")
        return {"status": "success", "result": str(result)}
    except Exception as e:
        error_msg = f"Crew execution failed: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        raise RuntimeError(error_msg)