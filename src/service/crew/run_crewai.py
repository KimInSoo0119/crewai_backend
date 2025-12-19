from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

def run_crewai_flow(nodes, edges, id_map):
    try:
        load_dotenv()

        API_KEY = os.getenv("HOSTED_VLLM_API_KEY")
        LLM_SERVER_URL = os.getenv("HOSTED_VLLM_API_BASE")  
        MODEL_NAME = os.getenv("HOSTED_VLLM_MODEL_NAME")

        crew_llm = LLM(
                    model=f"openai/{MODEL_NAME}",
                    api_key=API_KEY,
                    base_url=LLM_SERVER_URL
                )

        agents_obj = {}
        tasks_obj = {}

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

                    agent = Agent(
                        role=role,
                        goal=goal,
                        backstory=backstory,
                        llm=crew_llm
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

                    description = node_data.get('description', '') 
                    expected_output = node_data.get('expected_output', '') 

                    task = Task(
                        description=description,
                        expected_output=expected_output,
                        agent=None
                    )
                    tasks_obj[db_id] = task
            except Exception as e:
                print(f"[Task Creation Error] Node ID: {getattr(node, 'id', None)} - {str(e)}")

        # Edge 
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
                source_task = tasks_obj.get(source_id)
                target_task = tasks_obj.get(target_id)
                target_agent = agents_obj.get(target_id)

                if source_agent and target_task:
                    target_task.agent = source_agent
                elif source_task and target_task:
                    source_task.add_next(target_task)
            except Exception as e:
                print(f"[Edge Connection Error] Source: {source}, Target: {target} - {str(e)}")

        agents_list = list(agents_obj.values())
        tasks_list = list(tasks_obj.values())

        crew = Crew(
            agents=agents_list,
            tasks=tasks_list,
            verbose=True
        )

        result = crew.kickoff()
        print(f"Crew execution completed. Result: {result}")
        # return {"status": "success", "result": str(result)}

    except Exception as e:
        print(f"CrewAI execution Error. Result: {str(e)}")
        # return {"status": "error", "message": str(e)}
