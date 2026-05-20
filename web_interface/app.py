#!/usr/bin/env python3
"""
Interfaz web para MxForce Brutte
"""
from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import json
import os
import threading
from datetime import datetime

app = Flask(__name__)

# Directorio para resultados
RESULTS_DIR = 'web_results'
os.makedirs(RESULTS_DIR, exist_ok=True)

# Almacenar trabajos activos
active_jobs = {}

class AttackJob:
    def __init__(self, job_id, attack_type, target, options):
        self.job_id = job_id
        self.attack_type = attack_type
        self.target = target
        self.options = options
        self.status = 'queued'
        self.result = None
        self.start_time = datetime.now()
    
    def run(self):
        self.status = 'running'
        # Aquí se ejecutaría el ataque real
        # Por ahora simulamos
        import time
        time.sleep(5)
        self.status = 'completed'
        self.result = f"Ataque a {self.target} completado"

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/attack/start', methods=['POST'])
def start_attack():
    """Inicia un nuevo ataque"""
    data = request.json
    attack_type = data.get('type')
    target = data.get('target')
    options = data.get('options', {})
    
    # Generar ID único
    job_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Crear y ejecutar trabajo
    job = AttackJob(job_id, attack_type, target, options)
    active_jobs[job_id] = job
    
    # Ejecutar en hilo separado
    thread = threading.Thread(target=job.run)
    thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'started'})

@app.route('/api/attack/status/<job_id>')
def attack_status(job_id):
    """Consulta estado de un ataque"""
    job = active_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'status': job.status,
        'result': job.result,
        'start_time': job.start_time.isoformat()
    })

@app.route('/api/hash/crack', methods=['POST'])
def crack_hash():
    """API para crackear hashes"""
    data = request.json
    hash_value = data.get('hash')
    wordlist = data.get('wordlist')
    
    # Ejecutar mxforce.py en modo hash
    cmd = [
        'python3', 'mxforce.py',
        '-t', 'hash',
        '-H', hash_value,
        '-w', wordlist
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return jsonify({
        'output': result.stdout,
        'error': result.stderr
    })

@app.route('/api/http/brute', methods=['POST'])
def brute_http():
    """API para fuerza bruta HTTP"""
    data = request.json
    url = data.get('url')
    username = data.get('username')
    wordlist = data.get('wordlist')
    
    cmd = [
        'python3', 'mxforce.py',
        '-t', 'http',
        '-u', url,
        '-U', username,
        '-w', wordlist
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return jsonify({
        'output': result.stdout,
        'error': result.stderr
    })

@app.route('/api/download/<filename>')
def download_result(filename):
    """Descarga archivos de resultados"""
    filepath = os.path.join(RESULTS_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
