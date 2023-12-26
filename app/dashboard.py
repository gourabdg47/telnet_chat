from app import app, chat_server
from flask import render_template, request
import sys
import asyncio
import threading

ChatServerObj = chat_server.ChatServer()
event_loop = None  # Store the event loop globally
server_thread = None  # Store the server thread globally

def run_event_loop_start():
    global event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    
    try:

        event_loop.run_until_complete(ChatServerObj.run_server())
    finally:
        event_loop.close()
        
def run_event_loop_stop():
    global event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    
    try:
         event_loop.run_until_complete(ChatServerObj.stop_server())
    finally:
        event_loop.close()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/start_server', methods=['POST'])
def start_server():
    global server_thread
    if ChatServerObj.server is None:
        server_thread = threading.Thread(target=run_event_loop_start)
        server_thread.start()
        return "Server started!"
    return "Server is already running."

@app.route('/stop_server', methods=['POST'])
def stop_server():
    global server_thread
    print("ChatServerObj.server: ----> ", ChatServerObj.server)
    if ChatServerObj.server is not None:
        server_thread = threading.Thread(target=run_event_loop_stop)
        server_thread.start()
        return "Server stopping."
    return "Server is not running. "
