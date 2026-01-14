import json
from src.utils.db_client import get_db_connection, release_db_connection

def create_task(task):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            INSERT INTO tb_task (project_id, name, description, expected_output, position)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, project_id, agent_id, name, description, expected_output, position, create_time, update_time
        """
        cursor.execute(query, (task.project_id, task.name, task.description, task.expected_output, json.dumps(task.position)))
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def update_task(task):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            UPDATE tb_task
            SET name=%s,
                description=%s,
                expected_output=%s,
                position=%s,
                update_time=NOW()
            WHERE id=%s
            RETURNING id, project_id, agent_id, name, description, expected_output, position, create_time, update_time
        """
        cursor.execute(query, (task.name, task.description, task.expected_output, json.dumps(task.position), task.id))
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def find_one(project_id: int, task_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id, project_id, agent_id, name, description, expected_output
            FROM tb_task
            WHERE project_id = %s
            AND id = %s
        """
        cursor.execute(query, (project_id, task_id))
        result = cursor.fetchall()

        return result

    finally:
        release_db_connection(conn)

def get_task_executions_by_execution_id(execution_id):
    """특정 execution의 모든 task 결과 조회 (프론트용)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                id,
                execution_id,
                task_id,
                task_name,
                execution_order,
                task_output,
                create_time
            FROM tb_task_execution
            WHERE execution_id = %s
            ORDER BY execution_order NULLS LAST, create_time
        """
        cursor.execute(query, (execution_id,))
        result = cursor.fetchall()
        
        return result
    
    finally:
        release_db_connection(conn)

def get_execution_status(execution_id):
    """Execution 조회"""
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