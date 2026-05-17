#!/usr/bin/env python3
import itertools
import string
import time
import random
from tqdm import tqdm

class BruteforceGenerator:
    def __init__(self, min_len=1, max_len=8, charset='lower', delay=0):
        self.min_len = min_len
        self.max_len = max_len
        self.delay = delay
        self.charset = self.get_charset(charset)
        self.total_combinations = self.calculate_total()
    
    def get_charset(self, charset_type):
        """Define el conjunto de caracteres"""
        charsets = {
            'lower': string.ascii_lowercase,
            'upper': string.ascii_uppercase,
            'digits': string.digits,
            'lower_digits': string.ascii_lowercase + string.digits,
            'upper_digits': string.ascii_uppercase + string.digits,
            'alnum': string.ascii_letters + string.digits,
            'full': string.ascii_letters + string.digits + string.punctuation
        }
        return charsets.get(charset_type, string.ascii_lowercase)
    
    def calculate_total(self):
        """Calcula total de combinaciones posibles"""
        total = 0
        for length in range(self.min_len, self.max_len + 1):
            total += len(self.charset) ** length
        return total
    
    def generate(self):
        """Generador de contraseñas"""
        for length in range(self.min_len, self.max_len + 1):
            for combo in itertools.product(self.charset, repeat=length):
                if self.delay > 0:
                    time.sleep(random.uniform(0, self.delay))
                yield ''.join(combo)
    
    def crack_hash(self, target_hash, hash_cracker, hash_type):
        """Crackea un hash usando generación bruta"""
        print(f"🎯 Iniciando fuerza bruta pura")
        print(f"📏 Longitud: {self.min_len}-{self.max_len}")
        print(f"🔤 Conjunto: {self.charset[:20]}...")
        print(f"📊 Combinaciones totales: {self.total_combinations:,}")
        
        with tqdm(total=self.total_combinations, desc="Generando y probando", unit="pass") as pbar:
            for password in self.generate():
                if hash_cracker.try_password(password, target_hash, hash_type):
                    print(f"\n✅ ¡CRACKED! 🎉")
                    print(f"📝 Contraseña encontrada: {password}")
                    return password
                pbar.update(1)
        
        print("\n❌ No se encontró la contraseña")
        return None
