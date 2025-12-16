from src.repository.agent import agent_repo

def save_agent(agent):
    try:
        if agent.id is None:
            return agent_repo.create_agent(agent)
        else:
            return agent_repo.update_agent(agent)
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")
    
def get_agent(project_id: int, agent_id: int):
    return agent_repo.find_one(project_id, agent_id)
