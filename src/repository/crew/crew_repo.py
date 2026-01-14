from src.utils.db_client import get_db_connection, release_db_connection
import json

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
            SELECT id, title
            FROM tb_project
        """
        cursor.execute(query)
        result = cursor.fetchall()

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
            SELECT id, model_id, role, goal, backstory, position, tools
            FROM tb_agent
            WHERE project_id=%s
        """
        cursor.execute(query, (project_id,))
        result = cursor.fetchall()

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
        cursor.execute(query, (project_id, role, goal, backstory, model_id, json.dumps(position)))
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
        cursor.execute(query, (role, goal, backstory, model_id, json.dumps(position), agent_id))
        
        conn.commit()
    
    finally:
        release_db_connection(conn)

def delete_agent(agent_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            DELETE FROM tb_agent WHERE id=%s
        """
        cursor.execute(query, (agent_id,))
        conn.commit()
    
    finally:
        release_db_connection(conn)

def get_tasks_info(project_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT id, agent_id, name, description, expected_output, position
            FROM tb_task
            WHERE project_id=%s
        """
        cursor.execute(query, (project_id,))
        result = cursor.fetchall()

        return result

    finally:
        release_db_connection(conn)

def insert_task(project_id, name, description, expected_output, position):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO tb_task (project_id, name, description, expected_output, position)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """
        cursor.execute(query, (project_id, name, description, expected_output, json.dumps(position)))
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
        
        query = """
            UPDATE tb_task
            SET name=%s, description=%s, expected_output=%s, position=%s
            WHERE id=%s
        """
        cursor.execute(query, (name, description, expected_output, json.dumps(position), task_id))
        
        conn.commit()

    finally:
        release_db_connection(conn)

def delete_task(task_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            DELETE FROM tb_task WHERE id=%s
        """
        cursor.execute(query, (task_id,))
        conn.commit()

    finally:
        release_db_connection(conn)

def get_edges_info(project_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT id, source_id, source_type, target_id, target_type, source_handle, target_handle
            FROM tb_edge
            WHERE project_id=%s
        """
        cursor.execute(query, (project_id,))
        result = cursor.fetchall()

        return result

    finally:
        release_db_connection(conn)

def insert_edge(project_id, source_type, source_id, target_type, target_id, source_handle, target_handle):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO tb_edge (project_id, source_type, source_id, target_type, target_id, source_handle, target_handle)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        cursor.execute(query, (project_id, source_type, source_id, target_type, target_id, source_handle, target_handle))
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
        
        query = """
            UPDATE tb_edge
            SET source_type=%s, source_id=%s, target_type=%s, target_id=%s, source_handle=%s, target_handle=%s
            WHERE id=%s
        """
        cursor.execute(query, (source_type, source_id, target_type, target_id, source_handle, target_handle, edge_id))
        
        conn.commit()
    
    finally:
        release_db_connection(conn)

def delete_edge(edge_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            DELETE FROM tb_edge WHERE id=%s
        """
        cursor.execute(query, (edge_id,))
        conn.commit()
    
    finally:
        release_db_connection(conn)

def create_execution(project_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO tb_execution (project_id, result, status)
            VALUES (%s, %s, false)
            RETURNING id, create_time
        """
        cursor.execute(query, (project_id, json.dumps({})))
        row = cursor.fetchone()
        
        conn.commit()
        return row['id']
    
    finally:
        release_db_connection(conn)

def get_execution_status(execution_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT id, project_id, result, status, create_time, update_time
            FROM tb_execution
            WHERE id=%s
        """
        cursor.execute(query, (execution_id,))
        row = cursor.fetchone()

        return row
    
    finally:
        release_db_connection(conn)

def update_execution_result(execution_id, result_data):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            UPDATE tb_execution
            SET result = %s,
                update_time = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (json.dumps(result_data), execution_id))
        conn.commit()
        
        return cursor.rowcount
    
    finally:
        release_db_connection(conn)

def update_execution_status(execution_id, status):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            UPDATE tb_execution
            SET status = %s,
                update_time = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (status, execution_id))
        conn.commit()
        
        return cursor.rowcount
    
    finally:
        release_db_connection(conn)

def update_execution_final(execution_id, status, final_result):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            UPDATE tb_execution
            SET result = %s,
                status = %s,
                update_time = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (json.dumps(final_result), status, execution_id))
        conn.commit()
        
        return cursor.rowcount
    
    finally:
        release_db_connection(conn)

def insert_task_execution(execution_id, task_id, task_name, execution_order, task_output):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO tb_task_execution 
            (execution_id, task_id, task_name, execution_order, task_output)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        cursor.execute(query, (
            execution_id, 
            str(task_id), 
            task_name, 
            execution_order, 
            json.dumps(task_output)
        ))
        row = cursor.fetchone()
        task_execution_id = row['id']
        
        conn.commit()
        return task_execution_id
    
    finally:
        release_db_connection(conn)

def update_task_execution(task_execution_id, task_output):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            UPDATE tb_task_execution 
            SET task_output = %s
            WHERE execution_id = %s
        """
        cursor.execute(query, (json.dumps(task_output), task_execution_id))
        conn.commit()
        
        return cursor.rowcount
    
    finally:
        release_db_connection(conn)