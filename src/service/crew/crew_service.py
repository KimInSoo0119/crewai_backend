from src.repository.crew import crew_repo

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
    
def get_crew_flow(project_id):
    try:
        agents = crew_repo.get_agents_info(project_id)
        tasks = crew_repo.get_tasks_info(project_id)
        edges_db = crew_repo.get_edges_info(project_id)

        nodes = []
        for agent in agents:
            nodes.append({
                "id": f"agent-{agent['id']}",
                "dbId": agent['id'],
                "type": "agent",
                "position": agent.get('position', {'x':100, 'y':100}),  
                "data": {
                    "label": f"Agent {agent['id']}",
                    "role": agent['role'],
                    "goal": agent['goal'],
                    "backstory": agent['backstory']
                }
            })

        for task in tasks:
            nodes.append({
                "id": f"task-{task['id']}",
                "dbId": task['id'],
                "type": "task",
                "position": task.get('position', {'x':400, 'y':100}),
                "data": {
                    "label": task['name'],
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
                "target": f"{edge['target_type']}-{edge['target_id']}"
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

        # NODES
        for node in nodes:
            db_id = getattr(node, "dbId", None)
            node_data = getattr(node, "data", {}) or {}
            node_type = getattr(node, "type", None)
            node_pos = getattr(node, "position", None)

            if node_type == "agent":
                role = node_data.get("role", "")
                goal = node_data.get("goal", "")
                backstory = node_data.get("backstory", "")

                if db_id:
                    crew_repo.update_agent(db_id, role, goal, backstory, node_pos)
                    request_agents.add(db_id)
                else:
                    new_id = crew_repo.insert_agent(project_id, role, goal, backstory, node_pos)
                    request_agents.add(new_id)

            elif node_type == "task":
                name = node_data.get("name", "")
                description = node_data.get("description", "")
                expected_output = node_data.get("expected_output", "")

                if db_id:
                    crew_repo.update_task(db_id, name, description, expected_output, node_pos)
                    request_tasks.add(db_id)
                else:
                    new_id = crew_repo.insert_task(project_id, name, description, expected_output, node_pos)
                    request_tasks.add(new_id)

        # DELETE REMOVED NODES
        for agent_id in existing_agents - request_agents:
            crew_repo.delete_agent(agent_id)
        for task_id in existing_tasks - request_tasks:
            crew_repo.delete_task(task_id)

        # EDGES
        for edge in edges:
            db_id = getattr(edge, "dbId", None)
            source, target = getattr(edge, "source", ""), getattr(edge, "target", "")

            if "-" not in source or "-" not in target:
                continue  

            source_type, source_id = source.split("-")
            target_type, target_id = target.split("-")

            source_id = int(source_id)
            target_id = int(target_id)

            if db_id:
                crew_repo.update_edge(db_id, source_type, source_id, target_type, target_id)
                request_edges.add(db_id)
            else:
                new_id = crew_repo.insert_edge(project_id, source_type, source_id, target_type, target_id)
                request_edges.add(new_id)

        # DELETE REMOVED EDGES
        for edge_id in existing_edges - request_edges:
            crew_repo.delete_edge(edge_id)

    except Exception as e:
        raise RuntimeError(f"execute_flow error: {str(e)}")

