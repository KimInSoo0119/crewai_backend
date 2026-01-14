from src.repository.task import task_repo

def save_task(task):
    try:
        if task.id is None:
            return task_repo.create_task(task)
        else:
            return task_repo.update_task(task)
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")
    
def get_task(project_id: int, task_id: int):
    return task_repo.find_one(project_id, task_id)

def get_task_executions(execution_id: int):
    try:
        execution = task_repo.get_execution_status(execution_id)
        
        if not execution:
            raise RuntimeError(f"Execution {execution_id} not found")
        
        task_executions = task_repo.get_task_executions_by_execution_id(execution_id)
        
        formatted_tasks = []
        for te in task_executions:
            formatted_tasks.append({
                "id": te['id'],
                "task_id": te['task_id'],
                "task_name": te['task_name'],
                "execution_order": te['execution_order'],
                "task_output": te['task_output'],  
                "create_time": te['create_time'].isoformat() if te.get('create_time') else None
            })
        
        return {
            "id": execution['id'],
            "project_id": execution['project_id'],
            "status": execution['status'],
            "result": execution['result'],
            "task_executions": formatted_tasks,
            "create_time": execution['create_time'].isoformat() if execution.get('create_time') else None,
            "update_time": execution['update_time'].isoformat() if execution.get('update_time') else None
        }

    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")