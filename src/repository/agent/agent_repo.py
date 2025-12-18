from src.utils.db_client import get_db_connection, release_db_connection

def create_agent(agent):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            INSERT INTO tb_agent (project_id, role, goal, backstory, model_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, project_id, role, goal, backstory, model_id, create_time, update_time
        """
        cursor.execute(query, (agent.project_id, agent.role, agent.goal, agent.backstory, agent.model_id))
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def update_agent(agent):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            UPDATE tb_agent
            SET role=%s,
                goal=%s,
                backstory=%s,
                model_id=%s,
                update_time=NOW()
            WHERE id=%s
            RETURNING id, project_id, role, goal, backstory, model_id, create_time, update_time
        """
        cursor.execute(query, (agent.role, agent.goal, agent.backstory, agent.model_id, agent.id))
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def find_one(project_id: int, agent_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                a.id,
                a.project_id,
                a.role,
                a.goal,
                a.backstory,
                m.id as model_id,
                m.name as model_name
            FROM tb_agent a
            LEFT JOIN tb_model m
                ON a.model_id = m.id
            WHERE a.project_id = %s
                AND a.id = %s
        """
        cursor.execute(query, (project_id, agent_id))
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

