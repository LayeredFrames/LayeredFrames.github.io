from flask import Flask, request
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/edit', methods=['GET'])
def edit_file():
    file_path = request.args.get('file')
    # full_path = os.path.join(BASE_PATH, file_path)

    if not file_path or not os.path.exists(file_path):
        return "File not found", 404

    try:
        # Open the file using the default editor (macOS-specific)
        subprocess.run(["code", "-n", file_path], check=True)
        return f"Opened {file_path} for editing", 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(port=4001)