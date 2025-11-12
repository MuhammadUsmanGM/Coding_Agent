"""
Database Tool (Local SQLite)
Runs SQL queries only on a local SQLite file.
"""
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'data.db'  # Default path, can be overridden

@app.route('/query', methods=['POST'])
def query():
    sql = request.json.get('sql', '')
    db_path = request.json.get('db_path', DB_PATH)
    
    # Validate that the DB path is within the current directory
    if not os.path.abspath(db_path).startswith(os.getcwd()):
        return jsonify({'error': 'Database path outside allowed directory'}), 400
    
    # Basic SQL validation to prevent dangerous operations
    sql_lower = sql.strip().lower()
    dangerous_ops = ['drop', 'delete', 'insert', 'update', 'alter', 'create']  # Could be expanded
    if any(op in sql_lower for op in dangerous_ops[:2]):  # Only blocking drop and delete for now
        if not request.json.get('confirm_dangerous', False):
            return jsonify({'error': 'Dangerous SQL operation requires confirmation'}), 400
    
    try:
        with sqlite3.connect(db_path) as db:
            cur = db.execute(sql)
            rows = cur.fetchall()
            
            # Get column names
            columns = [description[0] for description in cur.description] if cur.description else []
            
            return jsonify({'columns': columns, 'rows': rows})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=9700)