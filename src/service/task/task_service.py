from src.repository.task import task_repo

def save_task(task):
    try:
        if task.id is None:
            return task_repo.create_task(task)
        else:
            return task_repo.update_task(task)
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")