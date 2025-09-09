from dotenv import load_dotenv
import pyodbc
import hashlib
import secrets
from datetime import datetime, timedelta

class dbConnector():
    def __init__(self, server, db_name):
        self._server = server
        self._db_name = db_name
        self._connection = None
        self._active_connections = {}

    def _connect(self, user, password) -> None:
        conn_str = f'DRIVER={{SQL Server}};SERVER={self._server};DATABASE={self._db_name};UID={user};PWD={password}'
        try:
            self._connection = pyodbc.connect(conn_str)
            self._connection.setdecoding(pyodbc.SQL_CHAR, encoding='cp1251')
            self._connection.setdecoding(pyodbc.SQL_WCHAR, encoding='cp1251')
            self._connection.setencoding(encoding='cp1251')
            print('connection succesfull')
        except Exception as ex:
            print('Connection refused')
            print(ex)
            raise Exception(f"Database connection failed: {str(ex)}")
        
    def create_api_key(self, user, password, expires_hours=24):
        try:
            test_conn = pyodbc.connect(
                f'DRIVER={{SQL Server}};SERVER={self._server};DATABASE={self._db_name};UID={user};PWD={password}'
            )
            test_conn.close()
        except:
            raise Exception("Invalid database credentials")
        api_key = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        self._active_connections[api_key] = {
            'user': user,
            'password': password,
            'expires_at': expires_at
        }
        return api_key, expires_at
    
    def validate_api_key(self, api_key):
        if api_key not in self._active_connections:
            return False
        connection_data = self._active_connections[api_key]
        if datetime.now() > connection_data['expires_at']:
            del self._active_connections[api_key]
            return False
        return connection_data

    @staticmethod
    def validate_sql_query(query):
        upper_query = query.upper().strip()
        forbidden_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 
        'EXEC', 'EXECUTE', 'CREATE', 'ALTER', 'GRANT', 'REVOKE'
        ]
        for keyword in forbidden_keywords:
            if keyword in upper_query:
                return False, f"Запрещенная операция: {keyword}"
        if not upper_query.startswith('SELECT'):
            return False, "Разрешены только SELECT запросы"
        if ';' in upper_query:
            return False, "Запрос не должен содержать точку с запятой"
        return True, "OK"
    
    def execute_sql_query(self, query, api_key):
        connection_data = self.validate_api_key(api_key)
        if not connection_data:
            raise Exception("Invalid or expired API key")
        self._connect(connection_data['user'], connection_data['password'])
        result = []
        if self._connection is not None:
            cursor = self._connection.cursor()
            is_valid, error_msg = self.validate_sql_query(query)
            if not is_valid:
                raise Exception(error_msg)
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                result.append(dict(zip(columns, row)))
            cursor.close()
            self._connection.close()
        return result
    
