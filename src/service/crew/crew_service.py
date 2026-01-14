from src.repository.crew import crew_repo
from .run_crewai import run_crewai_flow
from threading import Thread
import json

def create_crew(crewData):
    try:
        project_id = crew_repo.create_crew(crewData)
        return project_id
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}") 

def get_crew_list():
    try:
        response = crew_repo.get_crew_list()
        return response
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")
    
def delete_crew(project_id):
    try:
        response = crew_repo.delete_crew(project_id)
        return response
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")
    
def get_crew_flow(project_id):
    try:
        agents = crew_repo.get_agents_info(project_id) or []
        tasks = crew_repo.get_tasks_info(project_id) or []
        edges_db = crew_repo.get_edges_info(project_id) or []

        nodes = [] 
        for agent in agents:
            nodes.append({
                "id": f"agent-{agent['id']}",
                "dbId": agent['id'],
                "type": "agent",
                "position": agent.get('position', {'x':100, 'y':100}),  
                "data": {
                    "id": agent['id'],
                    "label": f"Agent {agent['id']}",
                    "model_id": agent['model_id'],
                    "role": agent['role'],
                    "goal": agent['goal'],
                    "backstory": agent['backstory'],
                    "tools": agent['tools']
                }
            })

        for task in tasks:
            nodes.append({
                "id": f"task-{task['id']}",
                "dbId": task['id'],
                "type": "task",
                "position": task.get('position', {'x':400, 'y':100}),
                "data": {
                    "id": task['id'],
                    "name": task['name'],
                    "description": task['description'],
                    "expected_output": task['expected_output'],
                    "agent_id": task['agent_id']
                }
            })

        edges = []
        for edge in edges_db:
            edges.append({
                "id": f"edge-{edge['id']}",
                "dbId": edge['id'],
                "source": f"{edge['source_type']}-{edge['source_id']}",
                "target": f"{edge['target_type']}-{edge['target_id']}",
                "sourceHandle": edge['source_handle'],  
                "targetHandle": edge['target_handle'],
            })

        return {"nodes": nodes, "edges": edges}

    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")

def execute_flow(project_id, nodes, edges):
    try:
        existing_agents = {a["id"] for a in crew_repo.get_agents_info(project_id)}
        existing_tasks = {t["id"] for t in crew_repo.get_tasks_info(project_id)}
        existing_edges = {e["id"] for e in crew_repo.get_edges_info(project_id)}

        request_agents = set()
        request_tasks = set()
        request_edges = set()

        id_map = {}

        # Agent/Task
        for node in nodes:
            db_id = getattr(node, "dbId", None)
            node_id = getattr(node, "id", None)
            node_data = getattr(node, "data", {}) or {}
            node_type = getattr(node, "type", None)
            node_pos = getattr(node, "position", None)

            if node_type == "agent":
                model_id = node_data.get("model_id", None)
                role = node_data.get("role", "")
                goal = node_data.get("goal", "")
                backstory = node_data.get("backstory", "")

                if not model_id:
                    raise ValueError(f"Agent '{role}' must have a model_id")

                if db_id:
                    crew_repo.update_agent(db_id, role, goal, backstory, model_id, node_pos)
                    request_agents.add(db_id)
                    id_map[f"agent-{db_id}"] = db_id
                else:
                    new_id = crew_repo.insert_agent(project_id, role, goal, backstory, model_id, node_pos)
                    request_agents.add(new_id)
                    id_map[node_id] = new_id

            elif node_type == "task":
                name = node_data.get("name", "")
                description = node_data.get("description", "")
                expected_output = node_data.get("expected_output", "")

                if db_id:
                    crew_repo.update_task(db_id, name, description, expected_output, node_pos)
                    request_tasks.add(db_id)
                    id_map[f"task-{db_id}"] = db_id
                else:
                    new_id = crew_repo.insert_task(project_id, name, description, expected_output, node_pos)
                    request_tasks.add(new_id)
                    id_map[node_id] = new_id

        # 삭제된 노드 처리
        for agent_id in existing_agents - request_agents:
            crew_repo.delete_agent(agent_id)
        for task_id in existing_tasks - request_tasks:
            crew_repo.delete_task(task_id)

        # Edge 
        for edge in edges:
            db_id = getattr(edge, "dbId", None)
            source = getattr(edge, "source", "")
            target = getattr(edge, "target", "")
            source_handle = getattr(edge, "sourceHandle", "")
            target_handle = getattr(edge, "targetHandle", "")

            source_type = source_handle.split("-")[0] if source_handle and "-" in source_handle else None
            target_type = target_handle.split("-")[0] if target_handle and "-" in target_handle else None
    
            if not source_type or not target_type:
                print(f"[Edge Warning] Missing handle types - source: {source_handle}, target: {target_handle}")
                continue

            # Source ID 파싱
            if source in id_map:
                source_id = id_map[source]
            else:
                if "-" in source:
                    parts = source.split("-", 1)
                    if len(parts) == 2:
                        source_id = int(parts[1])
                    else:
                        print(f"[Edge Error] Invalid source format: {source}")
                        continue
                else:
                    try:
                        source_id = int(source)
                    except ValueError:
                        print(f"[Edge Error] Cannot parse source ID: {source}")
                        continue

            # Target ID 파싱 
            if target in id_map:
                target_id = id_map[target]
            else:
                if "-" in target:
                    parts = target.split("-", 1)
                    if len(parts) == 2:
                        target_id = int(parts[1])
                    else:
                        print(f"[Edge Error] Invalid target format: {target}")
                        continue
                else:
                    try:
                        target_id = int(target)
                    except ValueError:
                        print(f"[Edge Error] Cannot parse target ID: {target}")
                        continue

            try:
                if db_id:
                    crew_repo.update_edge(db_id, source_type, source_id, target_type, target_id, source_handle, target_handle)
                    request_edges.add(db_id)
                else:
                    new_id = crew_repo.insert_edge(project_id, source_type, source_id, target_type, target_id, source_handle, target_handle)
                    request_edges.add(new_id)
            except Exception as e:
                print(f"[Edge Error] Failed to save edge: source={source}, target={target}, error={e}")
                continue

        for edge_id in existing_edges - request_edges:
            crew_repo.delete_edge(edge_id)

        # Execution 생성
        execution_id = crew_repo.create_execution(project_id=project_id)

        # 초기 상태 저장 
        initial_result = {
            "crew_id": None,
            "agent_hierarchy": [],
            "status": "initializing"
        }
        crew_repo.update_execution_result(execution_id, initial_result)

        def run_async():
            try:
                print(f"[Async Thread Started] Execution ID: {execution_id}")
                
                result = run_crewai_flow(nodes, edges, id_map, execution_id, crew_repo)
                
                print(f"[Async Thread Completed] Result: {result.get('status', 'unknown')}")
                
            except Exception as e:
                error_msg = f"Async execution error: {str(e)}"
                print(f"[Async Thread Error] {error_msg}")
                
                import traceback
                traceback.print_exc()
                
                # 에러 발생 시 상태 업데이트
                error_result = {
                    "crew_id": None,
                    "agent_hierarchy": [],
                    "error": error_msg,
                    "status": "failed"
                }
                
                crew_repo.update_execution_final(
                    execution_id=execution_id,
                    status=False,
                    final_result=error_result
                )
        
        thread = Thread(target=run_async)
        thread.daemon = False  
        thread.start()

        return {"execution_id": execution_id}

    except Exception as e:
        print(f"[Execute Flow Error] {str(e)}")
        raise RuntimeError(f"Execute flow error: {str(e)}")

def get_execution_status(execution_id):
    try:
        result = crew_repo.get_execution_status(execution_id)
        return result
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}") 
