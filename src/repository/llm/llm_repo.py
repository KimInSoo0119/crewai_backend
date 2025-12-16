from src.utils.db_client import get_db_connection, release_db_connection

def connection_llm(llmInfo):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            INSERT INTO tb_model (name, provider, api_base_url, is_active)
            VALUES (%s, %s, %s, TRUE)
            RETURNING id
        """
        cursor.execute(query, (llmInfo.name, llmInfo.provider, llmInfo.api_base))
        result = cursor.fetchone()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def get_llm_list():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id,
                name
            FROM tb_model
        """
        cursor.execute(query)
        result = cursor.fetchone()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)

def get_provider_list():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id,
                label
            FROM tb_provider
        """
        cursor.execute(query)
        result = cursor.fetchone()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)