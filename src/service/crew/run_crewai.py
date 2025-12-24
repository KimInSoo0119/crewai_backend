from crewai import Agent, Task, Crew, LLM, Process
from src.repository.llm import llm_repo

def run_crewai_flow(nodes, edges, id_map):
    try:
        agents_obj = {}
        tasks_obj = {}
        task_dependencies = {}
        agent_tasks_map = {}  

        # Agent 생성
        for node in nodes:
            try:
                db_id = getattr(node, "dbId", None)
                node_id = getattr(node, "id", None)
                node_data = getattr(node, "data", {}) or {}
                node_type = getattr(node, "type", None)

                if node_type == 'agent':
                    if not db_id:
                        db_id = id_map.get(node_id)
                        if db_id is None:
                            raise ValueError(f"Unable to determine db_id for agent node: {node_id}")

                    role = node_data.get('role', '') 
                    goal = node_data.get('goal', '') 
                    backstory = node_data.get('backstory', '') 
                    model_id = node_data.get('model_id', None)

                    model_info = llm_repo.get_model_info(model_id)

                    model_name = model_info['name']
                    model_base_url = model_info['api_base_url']
                    model_api_key = model_info['api_key']

                    crew_llm = LLM( 
                        model=f"openai/{model_name}",
                        api_key=model_api_key,
                        base_url=model_base_url
                    )

                    agent = Agent(
                        role=role,
                        goal=goal,
                        backstory=backstory,
                        llm=crew_llm
                    )
                    agents_obj[db_id] = agent
                    agent_tasks_map[db_id] = []  
            except Exception as e:
                print(f"[Agent Creation Error] Node ID: {getattr(node, 'id', None)} - {str(e)}")

        # Task 생성
        for node in nodes:
            try:
                db_id = getattr(node, "dbId", None)
                node_id = getattr(node, "id", None)
                node_data = getattr(node, "data", {}) or {}
                node_type = getattr(node, "type", None)

                if node_type == 'task':
                    if not db_id:
                        db_id = id_map.get(node_id)
                        if db_id is None:
                            raise ValueError(f"Unable to determine db_id for task node: {node_id}")

                    name = node_data.get('name', '')
                    description = node_data.get('description', '') 
                    expected_output = node_data.get('expected_output', '') 

                    task = Task(
                        description=description,
                        expected_output=expected_output,
                        agent=None  
                    )
                    tasks_obj[db_id] = {
                        'task': task,
                        'name': name,
                        'description': description 
                    }
                    task_dependencies[db_id] = []
            except Exception as e:
                print(f"[Task Creation Error] Node ID: {getattr(node, 'id', None)} - {str(e)}")

        # Edge 처리
        for edge in edges:
            try:
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
                source_task_obj = tasks_obj.get(source_id)
                target_task_obj = tasks_obj.get(target_id)

                if source_agent and target_task_obj:
                    target_task_obj['task'].agent = source_agent
                    agent_tasks_map[source_id].append({
                        'id': target_id,
                        'name': target_task_obj['name'],
                        'description': target_task_obj['description']
                    })
                
                elif source_task_obj and target_task_obj:
                    if target_id in task_dependencies:
                        task_dependencies[target_id].append(source_id)
            except Exception as e:
                print(f"[Edge Connection Error] Source: {source}, Target: {target} - {str(e)}")

        tasks_without_agent = []
        for task_id, task_obj in list(tasks_obj.items()):
            if task_obj['task'].agent is None:
                tasks_without_agent.append(task_id)
                del tasks_obj[task_id]
                if task_id in task_dependencies:
                    del task_dependencies[task_id]
                for deps in task_dependencies.values():
                    if task_id in deps:
                        deps.remove(task_id)

        if tasks_without_agent:
            print(f"[Warning] {len(tasks_without_agent)} task(s) were skipped due to missing agent assignment.")
        if not tasks_obj:
            raise ValueError("No valid tasks found. All tasks must be connected to an agent.")

        # Context 설정
        for task_id, dependency_ids in task_dependencies.items():
            if dependency_ids and task_id in tasks_obj:
                context_tasks = [tasks_obj[dep_id]['task'] for dep_id in dependency_ids if dep_id in tasks_obj]
                if context_tasks:
                    tasks_obj[task_id]['task'].context = context_tasks

        # Edge 정보 기반으로 Task 순서 정렬
        def sort_tasks_by_dependencies(tasks_obj, task_dependencies):
            sorted_ids = []
            visited = set()
            visiting = set()
            
            def visit(task_id):
                if task_id in visited:
                    return
                if task_id in visiting:
                    raise ValueError(f"Circular dependency detected at task {task_id}")
                
                visiting.add(task_id)
                
                deps = task_dependencies.get(task_id, [])
                for dep_id in deps:
                    if dep_id in tasks_obj:
                        visit(dep_id)
                
                visiting.remove(task_id)
                visited.add(task_id)
                sorted_ids.append(task_id)
            
            for task_id in tasks_obj.keys():
                visit(task_id)
            
            return sorted_ids

        sorted_task_ids = sort_tasks_by_dependencies(tasks_obj, task_dependencies)
        tasks_list = [tasks_obj[task_id]['task'] for task_id in sorted_task_ids]
        agents_list = [agent for agent in agents_obj.values()]

        for task in tasks_list:
            if task.agent is None:
                raise ValueError(f"Task '{task.description[:50]}...' has no agent assigned")

        crew = Crew(
            agents=agents_list,
            tasks=tasks_list,
            process=Process.sequential,
            verbose=True
        )

        final_result = crew.kickoff() 
        
        agent_hierarchy = []
        for agent_id, agent in agents_obj.items():
            agent_hierarchy.append({
                "agent_id": str(agent_id),
                "agent_role": agent.role,
                "tasks": agent_tasks_map.get(agent_id, [])
            })

        workflow = []
        for task_id in sorted_task_ids:
            task = tasks_obj[task_id]['task']
            workflow.append({
                "id": str(task.id),
                "name": tasks_obj[task_id]['name'],
                "output": getattr(task.output, "__dict__", str(task.output))
            })

        return {
            "details": {
                "crew_id": str(crew.id),
                "agent_hierarchy": agent_hierarchy,  
                "workflow": workflow,
                "final_output": str(final_result)
            }
        }

    except Exception as e:
        print(f"[Crew Execution Error] {str(e)}")
        return {"status": "error", "message": str(e)}