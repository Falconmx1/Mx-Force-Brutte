#!/usr/bin/env python3
"""
MxForce Brutte - Herramienta de fuerza bruta
Author: Falconmx1
"""
import argparse
import sys
import os
from core.hash_cracker import HashCracker
from core.http_brute import HTTPBrute
from core.service_attacks import ServiceAttacker
from core.bruteforce_gen import BruteforceGenerator

def banner():
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║  🔓 MxForce Brutte v2.0 - FULL EDITION            ║
    ║  "La seguridad no existe, solo contraseñas"       ║
    ║  Hecho en México 🇲🇽                               ║
    ║  Features: Hash | HTTP | SSH | FTP | BruteForce   ║
    ╚═══════════════════════════════════════════════════╝
    """)

def main():
    banner()
    
    parser = argparse.ArgumentParser(description='MxForce Brutte - Herramienta de fuerza bruta completa')
    
    # Modos principales
    parser.add_argument('-t', '--type', choices=['hash', 'http', 'http-basic', 'http-form', 'ssh', 'ftp', 'bruteforce'], 
                        required=True, help='Tipo de ataque')
    
    # Opciones para hash
    parser.add_argument('-H', '--hash', help='Hash objetivo')
    parser.add_argument('-f', '--hash-file', help='Archivo con hashes')
    
    # Opciones para HTTP/SSH/FTP
    parser.add_argument('-u', '--url', help='URL objetivo (HTTP)')
    parser.add_argument('--host', help='Host objetivo (SSH/FTP)')
    parser.add_argument('-p', '--port', type=int, help='Puerto (default: SSH=22, FTP=21)')
    parser.add_argument('-U', '--user', default='admin', help='Usuario (default: admin)')
    
    # Wordlist o brute force
    parser.add_argument('-w', '--wordlist', help='Diccionario de contraseñas')
    
    # Brute force puro
    parser.add_argument('--min-len', type=int, default=4, help='Longitud mínima (bruteforce)')
    parser.add_argument('--max-len', type=int, default=6, help='Longitud máxima (bruteforce)')
    parser.add_argument('--charset', choices=['lower', 'upper', 'digits', 'lower_digits', 'upper_digits', 'alnum', 'full'], 
                       default='lower_digits', help='Conjunto de caracteres')
    
    # Configuración general
    parser.add_argument('-T', '--threads', type=int, default=4, help='Número de hilos')
    parser.add_argument('--delay', type=float, default=0, help='Delay random en segundos (modo evasión)')
    parser.add_argument('--proxy', help='Proxy (ej: http://127.0.0.1:8080)')
    parser.add_argument('-o', '--output', help='Guardar resultados en archivo')
    
    args = parser.parse_args()
    
    # Configurar proxy
    proxy_dict = None
    if args.proxy:
        proxy_dict = {'http': args.proxy, 'https': args.proxy}
    
    # Modo HASH
    if args.type == 'hash':
        if not args.wordlist:
            print("❌ Error: Modo hash requiere -w wordlist")
            sys.exit(1)
        if not args.hash and not args.hash_file:
            print("❌ Error: Especifica -H o -f para el modo hash")
            sys.exit(1)
        
        cracker = HashCracker(args.wordlist, args.threads, args.delay, args.proxy, args.output)
        
        if args.hash:
            cracker.crack_single(args.hash)
        elif args.hash_file:
            cracker.crack_file(args.hash_file)
    
    # Modo BRUTEFORCE (sin wordlist)
    elif args.type == 'bruteforce':
        if not args.hash:
            print("❌ Error: Modo bruteforce requiere -H <hash>")
            sys.exit(1)
        
        # Detectar tipo de hash
        cracker = HashCracker('', args.threads, args.delay, args.proxy, args.output)
        hash_type = cracker.detect_hash_type(args.hash)
        
        print(f"🔍 Hash tipo: {hash_type.upper()}")
        
        generator = BruteforceGenerator(args.min_len, args.max_len, args.charset, args.delay)
        generator.crack_hash(args.hash, cracker, hash_type)
    
    # Modo HTTP
    elif args.type in ['http', 'http-basic', 'http-form']:
        if not args.url:
            print("❌ Error: Especifica -u URL para el modo HTTP")
            sys.exit(1)
        if not args.wordlist:
            print("❌ Error: Modo HTTP requiere -w wordlist")
            sys.exit(1)
        
        brute = HTTPBrute(args.url, args.user, args.wordlist, args.threads, 
                         args.type, args.delay, args.proxy, args.output)
        brute.start()
    
    # Modo SSH
    elif args.type == 'ssh':
        if not args.host:
            print("❌ Error: Especifica --host para SSH")
            sys.exit(1)
        if not args.wordlist:
            print("❌ Error: Modo SSH requiere -w wordlist")
            sys.exit(1)
        
        port = args.port if args.port else 22
        attacker = ServiceAttacker(args.host, port, args.user, args.wordlist, 
                                   args.threads, args.delay, args.output)
        attacker.attack_ssh()
    
    # Modo FTP
    elif args.type == 'ftp':
        if not args.host:
            print("❌ Error: Especifica --host para FTP")
            sys.exit(1)
        if not args.wordlist:
            print("❌ Error: Modo FTP requiere -w wordlist")
            sys.exit(1)
        
        port = args.port if args.port else 21
        attacker = ServiceAttacker(args.host, port, args.user, args.wordlist, 
                                   args.threads, args.delay, args.output)
        attacker.attack_ftp()

if __name__ == "__main__":
    main()
