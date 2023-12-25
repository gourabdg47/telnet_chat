from app import app, chat_server
from flask import render_template, request
import sys
import asyncio
import threading

ChatServerObj = chat_server.ChatServer()
event_loop = None  # Store the event loop globally

def run_event_loop():
    global event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    
    try:
        if sys.version_info >= (3, 7):
            event_loop.run_until_complete(ChatServerObj.run_server())
        else:
            event_loop.run_until_complete(ChatServerObj.run_server())
    finally:
        event_loop.close()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/start_server', methods=['POST'])
def start_server():
    if ChatServerObj.server is None:
        thread = threading.Thread(target=run_event_loop)
        thread.start()
        return "Server started!"
    return "Server is already running."

@app.route('/stop_server', methods=['POST'])
def stop_server():
    global event_loop
    if ChatServerObj.server is not None and event_loop is not None:
        event_loop.call_soon_threadsafe(event_loop.stop)  # Stop the event loop
        return "Server stopping."
    return "Server is not running."

