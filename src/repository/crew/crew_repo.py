from src.utils.db_client import get_db_connection, release_db_connection

def get_crew_list():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id,
                title
            FROM tb_project
        """
        cursor.execute(query)
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)