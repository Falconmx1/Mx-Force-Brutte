#!/usr/bin/env python3
"""
Modo distribuido - Coordina ataques entre múltiples nodos
"""
import socket
import threading
import jsonimport pickle
from concurrent.futures import ThreadPoolExecutor

class DistributedMaster:
    """Servidor maestro que coordina el ataque"""
    
    def __init__(self, port=5555):
        self.port = port
        self.workers = []
        self.task_queue = []
        self.results = []
        
    def start_server(self):
        """Inicia servidor para aceptar workers"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(10)
        
        print(f"🎯 Master escuchando en puerto {self.port}")
        
        while True:
            client, addr = server.accept()
            print(f"✅ Worker conectado desde {addr}")
            worker_thread = threading.Thread(target=self.handle_worker, args=(client, addr))
            worker_thread.start()
    
    def handle_worker(self, client, addr):
        """Maneja conexión con un worker"""
        self.workers.append(client)
        
        while True:
            # Enviar tareas cuando estén disponibles
            if self.task_queue:
                task = self.task_queue.pop(0)
                client.send(pickle.dumps(task))
                
                # Recibir resultado
                result = pickle.loads(client.recv(4096))
                self.results.append(result)
                print(f"📥 Resultado recibido de {addr}: {result}")
    
    def add_task(self, task_type, target, wordlist_chunk):
        """Agrega una tarea a la cola"""
        task = {
            'type': task_type,
            'target': target,
            'wordlist': wordlist_chunk
        }
        self.task_queue.append(task)
        print(f"📤 Tarea agregada: {task_type}")

class DistributedWorker:
    """Worker que ejecuta ataques y reporta al master"""
    
    def __init__(self, master_host, master_port=5555):
        self.master_host = master_host
        self.master_port = master_port
        
    def connect(self):
        """Conecta al master"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.master_host, self.master_port))
        print(f"✅ Conectado al master {self.master_host}:{self.master_port}")
        
        while True:
            # Recibir tarea
            data = self.socket.recv(4096)
            if not data:
                break
            
            task = pickle.loads(data)
            print(f"📥 Tarea recibida: {task['type']}")
            
            # Ejecutar tarea (simulado)
            result = self.execute_task(task)
            
            # Enviar resultado
            self.socket.send(pickle.dumps(result))
    
    def execute_task(self, task):
        """Ejecuta la tarea asignada"""
        if task['type'] == 'hash':
            # Aquí iría la lógica de crackeo
            return {'status': 'completed', 'result': 'password_found'}
        elif task['type'] == 'http':
            return {'status': 'completed', 'result': 'login_found'}
        else:
            return {'status': 'failed', 'result': 'unknown_task'}

# Ejemplo de uso
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'master':
        master = DistributedMaster()
        master.start_server()
    elif len(sys.argv) > 1 and sys.argv[1] == 'worker':
        worker = DistributedWorker('localhost')
        worker.connect()
    else:
        print("Uso: python distributed_attack.py master|worker")
