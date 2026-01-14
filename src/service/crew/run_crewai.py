from crewai import Agent, Task, Crew, LLM, Process
from src.repository.llm import llm_repo
from .tool_manager import get_tool_instances
from .callbacks import create_step_callback, create_task_callback, parse_task_output

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
                        function_calling_llm=crew_llm,
                        respect_context_window=True,
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
                            print(f"[Edge Error] Invalid source format: {source}")
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
                            print(f"[Edge Error] Invalid target format: {target}")
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

                # agent → task 연결
                if source_agent and target_task_obj:
                    if target_task_obj['task'].agent is not None:
                        print(f"[Warning] Task {target_id} already has an agent. Skipping.")
                    else:
                        target_task_obj['task'].agent = source_agent

                # task → task 의존성
                elif source_task_obj and target_task_obj:
                    if target_id in task_dependencies:
                        task_dependencies[target_id].append(source_id)
            except Exception as e:
                print(f"[Edge Connection Error] Source: {source}, Target: {target} - {str(e)}")

        # Agent 없는 Task 제거
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
            print(f"[Warning] {len(tasks_without_agent)} task(s) skipped (no agent).")
        if not tasks_obj:
            raise ValueError("No valid tasks found.")

        # Context 설정 
        for task_id, dependency_ids in task_dependencies.items():
            if dependency_ids and task_id in tasks_obj:
                context_tasks = [tasks_obj[dep_id]['task'] for dep_id in dependency_ids if dep_id in tasks_obj]
                if context_tasks:
                    tasks_obj[task_id]['task'].context = context_tasks

        # Task 순서 정렬 
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
        agents_list = list(agents_obj.values())

        for task in tasks_list:
            if task.agent is None:
                raise ValueError(f"Task '{task.description[:50]}...' has no agent assigned")

        # Agent Hierarchy 구성
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

        # 초기 상태 저장
        initial_result = {
            "crew_id": None,
            "agent_hierarchy": agent_hierarchy,
            "status": "initializing"
        }
        crew_repo.update_execution_result(execution_id, initial_result)

        # Callback 변수 초기화
        crew_id_container = {'id': None}
        step_counter = {'count': 0}
        task_execution_map = {}  

        step_callback_fn = create_step_callback(
            execution_id=execution_id,
            crew_repo=crew_repo,
            crew_id_container=crew_id_container,
            step_counter=step_counter
        )

        task_callback_fn = create_task_callback(
            execution_id=execution_id,
            crew_repo=crew_repo,
            agent_hierarchy=agent_hierarchy,
            tasks_obj=tasks_obj,
            sorted_task_ids=sorted_task_ids,
            crew_id_container=crew_id_container,
            task_execution_map=task_execution_map
        )

        crew = Crew(
            agents=agents_list,
            tasks=tasks_list,
            process=Process.sequential,
            verbose=True,
            step_callback=step_callback_fn,
            task_callback=task_callback_fn
        )

        print(f"[Crew Starting] {len(agents_list)} agents, {len(tasks_list)} tasks")
        final_result = crew.kickoff()

        crew_id_str = crew_id_container['id']
        if crew_id_str is None and hasattr(crew, 'id'):
            crew_id_str = str(crew.id)

        # 누락된 Task 결과 보완
        for task_id in sorted_task_ids:
            task = tasks_obj[task_id]['task']
            task_id_str = str(task_id)

            # callback에서 저장되지 않은 경우
            if task_id_str not in task_execution_map and hasattr(task, 'output') and task.output:
                output_dict = parse_task_output(task.output)
                execution_order = sorted_task_ids.index(task_id)

                task_exec_id = crew_repo.insert_task_execution(
                    execution_id=execution_id,
                    task_id=task_id_str,
                    task_name=tasks_obj[task_id]['name'],
                    execution_order=execution_order,
                    task_output=output_dict
                )
                task_execution_map[task_id_str] = task_exec_id
                print(f"[Task Added Post-Execution] {tasks_obj[task_id]['name']}")

        # Final Output 파싱
        final_output_str = None
        if hasattr(final_result, 'raw'):
            final_output_str = final_result.raw
        elif hasattr(final_result, 'result'):
            final_output_str = final_result.result
        else:
            final_output_str = str(final_result)

        final_result_data = {
            "crew_id": crew_id_str,
            "agent_hierarchy": agent_hierarchy,
            "final_output": final_output_str,
            "status": "completed"
        }

        crew_repo.update_execution_final(
            execution_id=execution_id,
            status=True,
            final_result=final_result_data
        )

        return {
            "status": "success",
            "execution_id": execution_id,
            "crew_id": crew_id_str,
            "final_output": final_output_str
        }

    except Exception as e:
        print(f"[Crew Execution Error] {str(e)}")

        # 에러 발생 시 상태 저장
        error_result = {
            "crew_id": crew_id_container['id'] if 'crew_id_container' in locals() else None,
            "agent_hierarchy": agent_hierarchy if 'agent_hierarchy' in locals() else [],
            "error": str(e),
            "status": "failed"
        }

        crew_repo.update_execution_final(
            execution_id=execution_id,
            status=False,
            final_result=error_result
        )

        return {
            "status": "error",
            "message": str(e)
        }