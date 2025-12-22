from src.utils.db_client import get_db_connection, release_db_connection
from cryptography.fernet import Fernet
import os

APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY").encode()
fernet = Fernet(APP_SECRET_KEY)

def encrypt_api_key(api_key: str) -> str:
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()  

def decrypt_api_key(encrypted_key: str) -> str:
    decrypted = fernet.decrypt(encrypted_key.encode())
    return decrypted.decode()

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
        row = cursor.fetchone()
        model_id = row['id']

        secret_key = encrypt_api_key(llmInfo.api_key)

        query_ = """
            INSERT INTO tb_model_secret (model_id, api_key_encrypted)
            VALUES (%s, %s)
        """
        cursor.execute(query_, (model_id, secret_key))

        conn.commit()
        return model_id

    finally:
        release_db_connection(conn)

def get_model_info(model_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT 
                id, name, tm.api_base_url, tms.api_key_encrypted
            FROM tb_model tm
            INNER JOIN tb_model_secret tms
            ON tm.id = tms.model_id
            where tm.id = %s
        """
        cursor.execute(query, (model_id,))
        result = cursor.fetchone()

        decrypted_api_key = decrypt_api_key(result['api_key_encrypted'])

        model_info = {
            "id": result['id'],
            "name": result['name'],
            "api_base_url": result['api_base_url'],
            "api_key": decrypted_api_key
        }
        
        conn.commit()
        return model_info

    finally:
        release_db_connection(conn)

def get_llm_list():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                id, name
            FROM tb_model
        """
        cursor.execute(query)
        result = cursor.fetchall()

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
                id, label
            FROM tb_provider
        """
        cursor.execute(query)
        result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        release_db_connection(conn)