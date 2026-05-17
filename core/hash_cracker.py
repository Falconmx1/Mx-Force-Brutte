#!/usr/bin/env python3
import hashlib
import bcrypt
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import random

class HashCracker:
    def __init__(self, wordlist, threads=4, delay=0, proxy=None, output=None):
        self.wordlist = wordlist
        self.threads = threads
        self.delay = delay  # Modo evasión
        self.proxy = proxy
        self.output = output
        self.found = False
        self.result = None
        self.results_list = []  # Para guardar resultados
    
    def detect_hash_type(self, hash_str):
        """Detecta tipo de hash por su longitud/formato"""
        hash_len = len(hash_str)
        hash_lower = hash_str.lower()
        
        # NTLM
        if hash_len == 32 and all(c in '0123456789abcdef' for c in hash_lower):
            return 'ntlm'
        # MD5
        elif hash_len == 32:
            return 'md5'
        # SHA1
        elif hash_len == 40:
            return 'sha1'
        # SHA256
        elif hash_len == 64:
            return 'sha256'
        # SHA512
        elif hash_len == 128:
            return 'sha512'
        # bcrypt
        elif hash_str.startswith('$2b$') or hash_str.startswith('$2a$') or hash_str.startswith('$2y$'):
            return 'bcrypt'
        else:
            return 'unknown'
    
    def hash_password(self, password, hash_type):
        """Calcula hash según el tipo"""
        if hash_type == 'md5':
            return hashlib.md5(password.encode()).hexdigest()
        elif hash_type == 'sha1':
            return hashlib.sha1(password.encode()).hexdigest()
        elif hash_type == 'sha256':
            return hashlib.sha256(password.encode()).hexdigest()
        elif hash_type == 'sha512':
            return hashlib.sha512(password.encode()).hexdigest()
        elif hash_type == 'ntlm':
            # NTLM = MD4 en UTF-16LE
            import hashlib
            return hashlib.new('md4', password.encode('utf-16le')).hexdigest()
        elif hash_type == 'bcrypt':
            return None  # bcrypt necesita verificación especial
        return None
    
    def try_password(self, password, target_hash, hash_type):
        """Prueba una contraseña contra el hash"""
        # Modo evasión - delay random
        if self.delay > 0:
            time.sleep(random.uniform(0, self.delay))
        
        try:
            if hash_type == 'bcrypt':
                try:
                    return bcrypt.checkpw(password.encode(), target_hash.encode())
                except:
                    return False
            else:
                hashed = self.hash_password(password, hash_type)
                return hashed == target_hash if hashed else False
        except:
            return False
    
    def save_result(self, hash_val, password, hash_type):
        """Guarda resultado en archivo"""
        result_line = f"[+] {hash_type.upper()} | {hash_val} : {password}\n"
        self.results_list.append(result_line)
        
        if self.output:
            with open(self.output, 'a') as f:
                f.write(result_line)
            print(f"💾 Resultado guardado en: {self.output}")
    
    def crack_single(self, target_hash):
        """Crackea un solo hash"""
        hash_type = self.detect_hash_type(target_hash)
        print(f"🎯 Hash objetivo: {target_hash}")
        print(f"🔍 Tipo detectado: {hash_type.upper()}")
        print(f"📖 Cargando wordlist: {self.wordlist}")
        
        if self.delay > 0:
            print(f"⏱️  Modo evasión activado: delay random hasta {self.delay}s")
        if self.proxy:
            print(f"🔌 Usando proxy: {self.proxy}")
        if self.output:
            print(f"💾 Guardando resultados en: {self.output}")
        
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
                        self.save_result(target_hash, password, hash_type)
                        self.found = True
                        executor.shutdown(wait=False)
                        break
                    pbar.update(1)
        
        if not self.found:
            print("\n❌ No se encontró la contraseña en el wordlist")
    
    def crack_file(self, hash_file):
        """Crackea múltiples hashes de un archivo"""
        print("📝 Modo multi-hash")
        
        with open(hash_file, 'r') as f:
            hashes = [line.strip() for line in f if line.strip()]
        
        print(f"📊 Total de hashes: {len(hashes)}")
        
        for idx, target_hash in enumerate(hashes, 1):
            if self.found:
                break
            print(f"\n[{idx}/{len(hashes)}] Probando hash: {target_hash[:20]}...")
            self.crack_single(target_hash)
