from app import app, chat_server
from flask import render_template, request

import asyncio

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/start_server', methods=['POST'])
def start_server():
    if chat_server.server is None:
        asyncio.create_task(chat_server.run_server())
        return "Server started!"
    return "Server is already running."

@app.route('/stop_server', methods=['POST'])
def stop_server():
    if chat_server.server is not None:
        asyncio.create_task(chat_server.stop_server())
        return "Server stopped."
    return "Server is not running."
