from app import app
import psutil
from flask import render_template

@app.route('/monitor')
def monitor():
    uptime = psutil.cpu_times()
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent()
    cache_info = psutil.disk_usage('/')

    return render_template('monitor.html', uptime=uptime, memory=memory, cpu_percent=cpu_percent, cache_info=cache_info)
