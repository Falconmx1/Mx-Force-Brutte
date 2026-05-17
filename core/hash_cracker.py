#!/usr/bin/env python3
import hashlib
import bcrypt
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class HashCracker:
    def __init__(self, wordlist, threads=4):
        self.wordlist = wordlist
        self.threads = threads
        self.found = False
        self.result = None
    
    def detect_hash_type(self, hash_str):
        """Detecta tipo de hash por su longitud/formato"""
        hash_len = len(hash_str)
        
        if hash_len == 32:
            return 'md5'
        elif hash_len == 40:
            return 'sha1'
        elif hash_len == 64:
            return 'sha256'
        elif hash_str.startswith('$2b$') or hash_str.startswith('$2a$'):
            return 'bcrypt'
        else:
            return 'unknown'
    
    def try_password(self, password, target_hash, hash_type):
        """Prueba una contraseña contra el hash"""
        try:
            if hash_type == 'md5':
                hashed = hashlib.md5(password.encode()).hexdigest()
            elif hash_type == 'sha1':
                hashed = hashlib.sha1(password.encode()).hexdigest()
            elif hash_type == 'sha256':
                hashed = hashlib.sha256(password.encode()).hexdigest()
            elif hash_type == 'bcrypt':
                try:
                    return bcrypt.checkpw(password.encode(), target_hash.encode())
                except:
                    return False
            else:
                return False
            
            return hashed == target_hash
        except:
            return False
    
    def crack_single(self, target_hash):
        """Crackea un solo hash"""
        hash_type = self.detect_hash_type(target_hash)
        print(f"🎯 Hash objetivo: {target_hash}")
        print(f"🔍 Tipo detectado: {hash_type.upper()}")
        print(f"📖 Cargando wordlist: {self.wordlist}")
        
        # Contar líneas
        with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            total_lines = sum(1 for _ in f)
        
        print(f"🔧 Usando {self.threads} hilos")
        print(f"📊 Total de contraseñas a probar: {total_lines:,}\n")
        
        with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f]
        
        with tqdm(total=total_lines, desc="Probando contraseñas", unit="pass") as pbar:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self.try_password, pwd, target_hash, hash_type): pwd 
                          for pwd in passwords}
                
                for future in as_completed(futures):
                    if future.result():
                        password = futures[future]
                        print(f"\n✅ ¡CRACKED! 🎉")
                        print(f"📝 Contraseña encontrada: {password}")
                        self.found = True
                        executor.shutdown(wait=False)
                        break
                    pbar.update(1)
        
        if not self.found:
            print("\n❌ No se encontró la contraseña en el wordlist")
    
    def crack_file(self, hash_file):
        """Crackea múltiples hashes de un archivo"""
        print("📝 Modo multi-hash - Próximamente")
        # TODO: Implementar
