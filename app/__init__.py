from flask import Flask, render_template, request, jsonify
import mysql.connector
import os
from datetime import datetime

def create_app():
    app = Flask(__name__)
    
    def get_db_connection():
        return mysql.connector.connect(
            host=os.environ.get('MYSQL_HOST', 'db'),
            user=os.environ.get('MYSQL_USER', 'notes_user'),
            password=os.environ.get('MYSQL_PASSWORD', 'user_password_123'),
            database=os.environ.get('MYSQL_DATABASE', 'notes_db'),
            port=int(os.environ.get('MYSQL_PORT', 3306))
        )
    
    @app.route('/')
    def index():
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
            notes = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('index.html', notes=notes)
        except Exception as e:
            return f"Database error: {str(e)}", 500
    
    @app.route('/notes', methods=['POST'])
    def create_note():
        content = request.form.get('content') or request.json.get('content')
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
            conn.commit()
            cursor.close()
            conn.close()
            
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'message': 'Note created successfully'}), 201
            else:
                return '', 204
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/notes', methods=['GET'])
    def get_notes():
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
            notes = cursor.fetchall()
            cursor.close()
            conn.close()
            
            for note in notes:
                if note['created_at']:
                    note['created_at'] = note['created_at'].isoformat()
            
            return jsonify(notes)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/notes/<int:note_id>', methods=['PUT'])
    def update_note(note_id):
        content = request.json.get('content')
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE notes SET content = %s WHERE id = %s", (content, note_id))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Note updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/notes/<int:note_id>', methods=['DELETE'])
    def delete_note(note_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Note deleted successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/healthz')
    def health_check():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 500
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
