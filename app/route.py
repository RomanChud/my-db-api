from app import create_app
from flask import request, jsonify
import urllib.parse
import json
from flask_cors import CORS 

def route_run():
    app = create_app()
    CORS(app, origins="*")

    @app.route('/')
    def index():
        data = {
            'message': 'SQL Query API работает!',
            'endpoints': {
                'auth': '/auth (POST) - получить API ключ',
                'query': '/query?sql=QUERY&api_key=API_KEY - выполнить запрос'
            }
        }
        
        return Response(
            json.dumps(data, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    
    @app.route('/auth', methods=['POST'])
    def authenticate():
        try:
            data = request.get_json()
            if not data or 'user' not in data or 'password' not in data:
                return Response(
                    json.dumps({
                        'success': False,
                        'error': 'Необходимы параметры user и password'
                    }, ensure_ascii=False),
                    status=400,
                    mimetype='application/json; charset=utf-8'
                )
            
            api_key, expires_at = app.db_connector.create_api_key(
                data['user'], 
                data['password'],
                expires_hours=24
            )
            
            return Response(
                json.dumps({
                    'success': True,
                    'api_key': api_key,
                    'expires_at': expires_at.isoformat()
                }, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            )
            
        except Exception as e:
            return Response(
                json.dumps({
                    'success': False,
                    'error': str(e),
                }, ensure_ascii=False),
                status=401,
                mimetype='application/json; charset=utf-8'
            )
    
    @app.route('/query')
    def execute_sql():
        sql_query_encoded = request.args.get('sql')
        api_key = request.args.get('api_key')
        
        if not sql_query_encoded:
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Необходим параметр "sql"'
                }, ensure_ascii=False),
                status=400,
                mimetype='application/json; charset=utf-8'
            )
        
        if not api_key:
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Необходим параметр "api_key". Получите ключ через /auth'
                }, ensure_ascii=False),
                status=401,
                mimetype='application/json; charset=utf-8'
            )
        
        try:
            sql_query = urllib.parse.unquote(sql_query_encoded)
            result = app.db_connector.execute_sql_query(sql_query, api_key)
    
            return Response(
                json.dumps({
                    'success': True,
                    'query': sql_query,
                    'result': result,
                    'row_count': len(result)
                }, ensure_ascii=False),
                status=200,
                mimetype='application/json; charset=utf-8'
            )
            
        except Exception as e:
            return Response(
                json.dumps({
                    'success': False,
                    'error': str(e),
                    'query': sql_query_encoded
                }, ensure_ascii=False),
                status=500,
                mimetype='application/json; charset=utf-8'
            )
            
    app.run(debug=True, host='0.0.0.0', port=5000)
