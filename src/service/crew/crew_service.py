from src.repository.crew import crew_repo

def get_crew_list():
    try:
        response = crew_repo.get_crew_list()
        return response
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")