from crewai import Agent, Task, Crew, LLM, Process
from src.repository.llm import llm_repo
from .tool_manager import get_tool_instances
import json

def run_crewai_flow(nodes, edges, id_map, execution_id, crew_repo):
    try:
        agents_obj = {}
        tasks_obj = {}
        task_dependencies = {}

        # Agent 
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
                    tools_config = node_data.get('tools', [])

                    model_info = llm_repo.get_model_info(model_id)

                    model_name = model_info['name']
                    model_base_url = model_info['api_base_url']
                    model_api_key = model_info['api_key']

                    crew_llm = LLM( 
                        model=f"openai/{model_name}",
                        api_key=model_api_key,
                        base_url=model_base_url,
                        temperature=0.1
                    )

                    tool_instances = get_tool_instances(tools_config)

                    agent = Agent(
                        role=role,
                        goal=goal,
                        backstory=backstory,
                        llm=crew_llm,
                        tools=tool_instances if tool_instances else None
                    )
                    agents_obj[db_id] = agent
            except Exception as e:
                print(f"[Agent Creation Error] Node ID: {getattr(node, 'id', None)} - {str(e)}")

        # Task 
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

        # Edge
        for edge in edges:
            try:
                source = getattr(edge, "source", None)
                target = getattr(edge, "target", None)

                # Source ID 파싱
                if source in id_map:
                    source_id = id_map[source]
                else:
                    if "-" in str(source):
                        parts = str(source).split("-", 1)
                        if len(parts) == 2:
                            source_id = int(parts[1])
                        else:
                            print(f"[Edge Error] Invalid source format after split: {source}")
                            continue
                    else:
                        try:
                            source_id = int(source)
                        except (ValueError, TypeError):
                            print(f"[Edge Error] Cannot parse source ID: {source}")
                            continue

                # Target ID 파싱
                if target in id_map:
                    target_id = id_map[target]
                else:
                    if "-" in str(target):
                        parts = str(target).split("-", 1)
                        if len(parts) == 2:
                            target_id = int(parts[1])
                        else:
                            print(f"[Edge Error] Invalid target format after split: {target}")
                            continue
                    else:
                        try:
                            target_id = int(target)
                        except (ValueError, TypeError):
                            print(f"[Edge Error] Cannot parse target ID: {target}")
                            continue

                source_agent = agents_obj.get(source_id)
                source_task_obj = tasks_obj.get(source_id)
                target_task_obj = tasks_obj.get(target_id)

                # agent → task 연결 (중복 할당 방지)
                if source_agent and target_task_obj:
                    if target_task_obj['task'].agent is not None:
                        print(f"[Warning] Task {target_id} already has an agent assigned. Skipping duplicate assignment.")
                    else:
                        target_task_obj['task'].agent = source_agent
                
                # task → task 의존성 연결
                elif source_task_obj and target_task_obj:
                    if target_id in task_dependencies:
                        task_dependencies[target_id].append(source_id)
            except Exception as e:
                print(f"[Edge Connection Error] Source: {source}, Target: {target} - {str(e)}")
                import traceback
                traceback.print_exc()

        # agent가 없는 task 제거
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

        # Task 순서 정렬 (Edge 기반 dependency)
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

        agent_hierarchy = []
        processed_agents = set()

        for task_id in sorted_task_ids:
            task_obj = tasks_obj[task_id]
            agent = task_obj['task'].agent
            
            agent_id = None
            for aid, ag in agents_obj.items():
                if ag == agent:
                    agent_id = aid
                    break
            
            if agent_id in processed_agents:
                continue
            
            processed_agents.add(agent_id)
            
            assigned_tasks = []
            for tid in sorted_task_ids:  
                if tasks_obj[tid]['task'].agent == agent:
                    assigned_tasks.append({
                        "id": tid,
                        "name": tasks_obj[tid]['name'],
                        "description": tasks_obj[tid]['description'],
                        "execution_order": sorted_task_ids.index(tid)  
                    })
            
            agent_hierarchy.append({
                "agent_id": str(agent_id),
                "agent_role": agent.role,
                "tasks": assigned_tasks
            })

        initial_result = {
            "crew_id": None,
            "agent_hierarchy": agent_hierarchy,
            "workflow": [],
            "final_output": None
        }
        
        crew_repo.update_execution_partial(execution_id, {
            "status": False,
            "result": json.dumps(initial_result)
        })

        crew = Crew(
            agents=agents_list,
            tasks=tasks_list,
            process=Process.sequential,
            verbose=True
        )

        workflow = []
        crew_id_str = None

        for idx, task_id in enumerate(sorted_task_ids):
            task = tasks_obj[task_id]['task']
            
            def create_callback(current_task_id, current_idx):
                """클로저로 task_id와 idx를 캡처"""
                def callback(output):
                    nonlocal crew_id_str
                    try:
                        if crew_id_str is None and hasattr(crew, 'id'):
                            crew_id_str = str(crew.id)
                        
                        output_content = None
                        output_dict = {}
                        
                        if hasattr(output, 'raw'):
                            output_content = output.raw
                            output_dict = {
                                'raw': output.raw,
                                'pydantic': getattr(output, 'pydantic', None),
                                'json_dict': getattr(output, 'json_dict', None),
                                'agent': getattr(output, 'agent', ''),
                                'summary': getattr(output, 'summary', '')
                            }
                        elif hasattr(output, 'result'):
                            output_content = output.result
                            output_dict = {'result': output.result}
                        elif hasattr(output, 'output'):
                            output_content = output.output
                            output_dict = {'output': output.output}
                        elif hasattr(output, '__dict__'):
                            output_dict = output.__dict__
                            output_content = str(output)
                        else:
                            output_content = str(output)
                            output_dict = {'raw': str(output)}
                        
                        task_result = {
                            "id": str(tasks_obj[current_task_id]['task'].id),
                            "task_id": str(current_task_id),
                            "name": tasks_obj[current_task_id]['name'],
                            "output": output_dict,
                            "execution_order": sorted_task_ids.index(current_task_id)
                        }
                        
                        workflow.append(task_result)

                        current_result = {
                            "crew_id": crew_id_str,
                            "agent_hierarchy": agent_hierarchy,
                            "workflow": list(workflow),
                            "final_output": None
                        }
                        
                        crew_repo.update_execution_partial(execution_id, {
                            "status": False,
                            "result": json.dumps(current_result)
                        })
                        
                        print(f"[Task Completed] {current_idx + 1}/{len(sorted_task_ids)}: {tasks_obj[current_task_id]['name']}")
                        preview = str(output_content)[:200] if output_content else "No content"
                        print(f"[Task Output Preview] {preview}...")
                        
                    except Exception as e:
                        print(f"[Callback Error] Task {current_task_id}: {str(e)}")
                
                return callback
            
            task.callback = create_callback(task_id, idx)

        final_result = crew.kickoff()
        
        if crew_id_str is None and hasattr(crew, 'id'):
            crew_id_str = str(crew.id)
        
        for task_id in sorted_task_ids:
            task = tasks_obj[task_id]['task']
            already_added = any(w.get('task_id') == str(task_id) for w in workflow)
            
            if not already_added and task.output:
                output_dict = {}
                if hasattr(task.output, 'raw'):
                    output_dict = {
                        'raw': task.output.raw,
                        'pydantic': getattr(task.output, 'pydantic', None),
                        'json_dict': getattr(task.output, 'json_dict', None),
                        'agent': getattr(task.output, 'agent', ''),
                        'summary': getattr(task.output, 'summary', '')
                    }
                elif hasattr(task.output, '__dict__'):
                    output_dict = task.output.__dict__
                else:
                    output_dict = {'raw': str(task.output)}
                
                task_output = {
                    "id": str(task.id),
                    "task_id": str(task_id),
                    "name": tasks_obj[task_id]['name'],
                    "output": output_dict,
                    "execution_order": sorted_task_ids.index(task_id)
                }
                workflow.append(task_output)
                print(f"[Task Added Post-Execution] {tasks_obj[task_id]['name']}")

        final_output_str = None
        if hasattr(final_result, 'raw'):
            final_output_str = final_result.raw
        elif hasattr(final_result, 'result'):
            final_output_str = final_result.result
        elif hasattr(final_result, '__str__'):
            final_output_str = str(final_result)
        else:
            final_output_str = str(final_result)

        result_details = {
            "crew_id": crew_id_str,
            "agent_hierarchy": agent_hierarchy,
            "workflow": workflow,
            "final_output": final_output_str
        }

        crew_repo.update_execution_final(
            execution_id=execution_id,
            status=True,
            final_result=result_details
        )

        return {
            "details": result_details
        }

    except Exception as e:
        print(f"[Crew Execution Error] {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}