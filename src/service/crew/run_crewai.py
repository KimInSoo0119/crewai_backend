from crewai import Agent, Task, Crew
import requests

class InternalLLM:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def __call__(self, prompt, **kwargs):
        response = requests.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"prompt": prompt, **kwargs},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("text", "")


def run_crewai_flow(project_id, nodes, edges, id_map):
    API_KEY="14987239852394087234902287"
    LLM_SERVER_URL="http://gpurent.kogrobo.com:51089/v1"

    llm = InternalLLM(LLM_SERVER_URL, API_KEY)
    crew = Crew(project_id=project_id)

    agents_obj = {}
    for node in nodes:
        if node['type'] == 'agent':
            db_id = node.get('dbId') or id_map[node['id']]
            agent = Agent(
                id = db_id,
                llm = llm,
                role = node['data'].get('role', ''),
                goal = node['data'].get('goal', ''),
                backstory = node['data'].get('backstory', '')
            )
            agents_obj[db_id] = agent
            crew.add_agent(agent)

    tasks_obj = {}
    for node in nodes:
        if node['type'] == 'task':
            db_id = node.get('dbId') or id_map[node['id']]
            task = Task(
                id = db_id,
                name = node['data'].get('name', ''),
                description = node['data'].get('description', ''),
                expected_output = node['data'].get('expected_output', '')
            )
            tasks_obj[db_id] = task
            crew.add_task(task)

    for edge in edges:
        source = edge['source']
        target = edge['taget']

        if source in id_map:
            source_id = id_map[source]
        else:
            _, source_id = source.split("", 1)
            source_id = int(source_id)

        if target in id_map:
            target_id = id_map[target]
        else:
            _, target_id = target.split("", 1)
            target_id = int(target_id)

        source_agent = agents_obj.get(source_id)
        source_task = tasks_obj.get(source_id)
        target_task = tasks_obj.get(target_id)

        if source_agent and target_task:
            source_agent.add_task(target_task)
        elif source_task and target_task:
            source_task.add_next(target_task)

    print(crew.run())
    return {}