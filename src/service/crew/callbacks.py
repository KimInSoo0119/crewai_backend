def create_step_callback(execution_id, crew_repo, crew_id_container, step_counter):
    def step_callback(step_output):
        try:
            # Crew ID 확보
            if crew_id_container['id'] is None:
                if hasattr(step_output, 'crew') and hasattr(step_output.crew, 'id'):
                    crew_id_container['id'] = str(step_output.crew.id)
            
            step_counter['count'] += 1
            
            # Agent 정보
            agent_role = "Unknown"
            if hasattr(step_output, 'agent') and step_output.agent:
                agent_role = step_output.agent.role
            
            # Output 정보
            content = "Processing"
            if hasattr(step_output, 'output') and step_output.output:
                output = step_output.output
                if hasattr(output, 'raw'):
                    content = output.raw[:100]
                else:
                    content = str(output)[:100]
            
            # Tool 사용 정보
            tool = None
            if hasattr(step_output, 'tool') and step_output.tool:
                tool = str(step_output.tool)
            
            # 로그 출력
            tool_info = f" [Tool: {tool}]" if tool else ""
            print(f"[Step {step_counter['count']}] {agent_role}{tool_info} - {content}")
            
        except Exception as e:
            print(f"[Step Callback Error] {str(e)}")
    
    return step_callback


def create_task_callback(execution_id, crew_repo, agent_hierarchy, tasks_obj, sorted_task_ids, 
                        crew_id_container, task_execution_map):
    def task_callback(task_output):
        try:
            # Crew ID 확보 및 초기 result 업데이트
            if crew_id_container['id'] is None:
                if hasattr(task_output, 'crew') and hasattr(task_output.crew, 'id'):
                    crew_id_container['id'] = str(task_output.crew.id)
                    
                    # 첫 crew_id 확보 시 tb_execution.result 업데이트
                    initial_result = {
                        "crew_id": crew_id_container['id'],
                        "agent_hierarchy": agent_hierarchy,
                        "status": "running"
                    }
                    crew_repo.update_execution_result(execution_id, initial_result)
            
            # Task ID 찾기
            task_id = None
            task_name = "Unknown"
            
            # 1순위: task_id로 매칭
            if hasattr(task_output, 'task_id'):
                for tid, task_obj in tasks_obj.items():
                    if str(task_obj['task'].id) == str(task_output.task_id):
                        task_id = tid
                        task_name = task_obj['name']
                        break
            
            # 2순위: description으로 매칭
            if task_id is None and hasattr(task_output, 'description'):
                for tid, task_obj in tasks_obj.items():
                    if task_obj['task'].description == task_output.description:
                        task_id = tid
                        task_name = task_obj['name']
                        break
            
            if task_id is None:
                print(f"[Warning] Could not match task_output to any task")
                return
            
            # Output 파싱
            output_dict = parse_task_output(task_output)
            
            # execution_order 계산
            execution_order = sorted_task_ids.index(task_id) if task_id in sorted_task_ids else -1
            
            # tb_task_execution에 저장 또는 업데이트
            task_id_str = str(task_id)
            
            if task_id_str in task_execution_map:
                # 이미 생성된 경우 업데이트
                crew_repo.update_task_execution(
                    task_execution_id=task_execution_map[task_id_str],
                    task_output=output_dict
                )
                print(f"[Task Updated] {task_name} (order: {execution_order})")
            else:
                # 새로 생성
                task_exec_id = crew_repo.insert_task_execution(
                    execution_id=execution_id,
                    task_id=task_id_str,
                    task_name=task_name,
                    execution_order=execution_order,
                    task_output=output_dict
                )
                task_execution_map[task_id_str] = task_exec_id
                print(f"[Task Completed] {task_name} (order: {execution_order})")
            
        except Exception as e:
            print(f"[Task Callback Error] {str(e)}")
    
    return task_callback


def parse_task_output(task_output):
    output_dict = {}
    
    try:
        if hasattr(task_output, 'raw'):
            output_dict = {
                'raw': task_output.raw,
                'pydantic': str(getattr(task_output, 'pydantic', None)) if getattr(task_output, 'pydantic', None) else None,
                'json_dict': getattr(task_output, 'json_dict', None),
                'agent': str(getattr(task_output, 'agent', '')) if getattr(task_output, 'agent', None) else None,
                'summary': getattr(task_output, 'summary', '')
            }
        elif hasattr(task_output, '__dict__'):
            output_dict = {}
            for k, v in task_output.__dict__.items():
                try:
                    if isinstance(v, (dict, list, str, int, float, bool, type(None))):
                        output_dict[k] = v
                    else:
                        output_dict[k] = str(v)
                except:
                    output_dict[k] = "<non-serializable>"
        else:
            output_dict = {'raw': str(task_output)}
    except Exception as e:
        output_dict = {'raw': str(task_output), 'parse_error': str(e)}
    
    return output_dict