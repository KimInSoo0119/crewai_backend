from src.utils.db_client import get_db_connection, release_db_connection
from psycopg2.extras import Json

def create_crew(crewData):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            INSERT INTO tb_project (title)
            VALUES (%s)
            RETURNING id
        """
        cursor.execute(query, (crewData.title,))
        row = cursor.fetchone()
        project_id = row['id']

        conn.commit()
        return project_id

    finally:
        release_db_connection(conn)

def get_crew_list():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id,title
            FROM tb_project
        """
        cursor.execute(query)
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def delete_crew(project_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            DELETE FROM tb_project WHERE id = %s
            RETURNING id
        """
        cursor.execute(query, (project_id,))
        row = cursor.fetchone()
        project_id = row['id']

        conn.commit()
        return project_id

    finally:
        release_db_connection(conn)

def get_agents_info(project_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id, model_id, role, goal, backstory, position
            FROM tb_agent
            WHERE project_id=%s
        """
        cursor.execute(query, (project_id,))
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def get_tasks_info(project_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id, agent_id, name, description, expected_output, position
            FROM tb_task
            WHERE project_id=%s
        """
        cursor.execute(query, (project_id,))
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def get_edges_info(project_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id, source_id, source_type, target_id, target_type, source_handle, target_handle
            FROM tb_edge
            WHERE project_id=%s
        """
        cursor.execute(query, (project_id,))
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def insert_agent(project_id, role, goal, backstory, model_id, position):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            INSERT INTO tb_agent (project_id, role, goal, backstory, model_id, position)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        cursor.execute(query, (project_id, role, goal, backstory, model_id, Json(position)))
        row = cursor.fetchone()
        agent_id = row['id']

        conn.commit()
        return agent_id

    finally:
        release_db_connection(conn)

def update_agent(agent_id, role, goal, backstory, model_id, position):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            UPDATE tb_agent
            SET role=%s, goal=%s, backstory=%s, model_id=%s, position=%s
            WHERE id=%s
        """
        cursor.execute(query, (role, goal, backstory, model_id, Json(position), agent_id))
        
        conn.commit()
    
    finally:
        release_db_connection(conn)

def delete_agent(agent_id,):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tb_agent WHERE id=%s", (agent_id,))
        conn.commit()
    
    finally:
        release_db_connection(conn)

def insert_task(project_id, name, description, expected_output, position):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tb_task (project_id, name, description, expected_output, position)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (project_id, name, description, expected_output, Json(position)))
        row = cursor.fetchone()
        task_id = row['id']
        
        conn.commit()
        return task_id
    
    finally:
        release_db_connection(conn)

def update_task(task_id, name, description, expected_output, position):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tb_task
            SET name=%s, description=%s, expected_output=%s, position=%s
            WHERE id=%s
        """, (name, description, expected_output, Json(position), task_id))
        
        conn.commit()

    finally:
        release_db_connection(conn)

def delete_task(task_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tb_task WHERE id=%s", (task_id,))
        conn.commit()

    finally:
        release_db_connection(conn)

def insert_edge(project_id, source_type, source_id, target_type, target_id, source_handle, target_handle):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tb_edge (project_id, source_type, source_id, target_type, target_id, source_handle, target_handle)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (project_id, source_type, source_id, target_type, target_id, source_handle, target_handle))
        row = cursor.fetchone()
        edge_id = row['id']
        
        conn.commit()
        return edge_id
    
    finally:
        release_db_connection(conn)

def update_edge(edge_id, source_type, source_id, target_type, target_id, source_handle, target_handle):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tb_edge
            SET source_type=%s, source_id=%s, target_type=%s, target_id=%s, source_handle=%s, target_handle=%s
            WHERE id=%s
        """, (source_type, source_id, target_type, target_id, source_handle, target_handle, edge_id))
        
        conn.commit()
    
    finally:
        release_db_connection(conn)

def delete_edge(edge_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tb_edge WHERE id=%s", (edge_id,))
        conn.commit()
    
    finally:
        release_db_connection(conn)

def create_execution(project_id, status):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tb_execution (project_id, status, create_time)
            VALUES (%s, %s, NOW()) RETURNING id
        """, (project_id, status))
        row = cursor.fetchone()
        execution_id = row['id']
        
        conn.commit()
        return execution_id
    
    finally:
        release_db_connection(conn)

def update_execution(status, result, execution_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tb_execution
            SET status=%s, result=%s, update_time=NOW()
            WHERE id=%s
        """, (status, result, execution_id))
        
        conn.commit()
    
    finally:
        release_db_connection(conn)

def get_execution_status(execution_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id, status, result
            FROM tb_execution
            WHERE id=%s
        """
        cursor.execute(query, (execution_id,))
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)