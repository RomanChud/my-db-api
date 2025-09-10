from app import create_app
from flask import request, jsonify
import urllib.parse
import json
from flask_cors import CORS 

app = create_app()
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"])

@app.route('/')
def index():
    return jsonify({
        'message': 'SQL Query API работает!',
        'endpoints': {
            'auth': '/auth (POST) - получить API ключ',
            'query': '/query?sql=QUERY&api_key=API_KEY - выполнить запрос'
        }
    })

@app.route('/auth', methods=['POST'])
def authenticate():
    try:
        data = request.get_json()
        if not data or 'user' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Необходимы параметры user и password'
            }), 400
        
        api_key, expires_at = app.db_connector.create_api_key(
            data['user'], 
            data['password'],
            expires_hours=24
        )
        
        return jsonify({
            'success': True,
            'api_key': api_key,
            'expires_at': expires_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 401

@app.route('/query')
def execute_sql():
    sql_query_encoded = request.args.get('sql')
    api_key = request.args.get('api_key')
    
    if not sql_query_encoded:
        return jsonify({
            'success': False,
            'error': 'Необходим параметр "sql"'
        }), 400
    
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'Необходим параметр "api_key". Получите ключ через /auth'
        }), 401
    
    try:
        sql_query = urllib.parse.unquote(sql_query_encoded)
        result = app.db_connector.execute_sql_query(sql_query, api_key)

        response = app.response_class(
            response=json.dumps({
                'success': True,
                'query': sql_query,
                'result': result,
                'row_count': len(result)
            }, ensure_ascii=False, indent=2),
            status=200,
            mimetype='application/json; charset=utf-8'
        )
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'query': sql_query_encoded
        }), 500

