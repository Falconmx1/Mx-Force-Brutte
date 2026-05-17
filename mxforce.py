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

def banner():
    print("""
    ╔═══════════════════════════════════════╗
    ║  🔓 MxForce Brutte v1.0               ║
    ║  "La seguridad no existe"             ║
    ║  Hecho en México 🇲🇽                   ║
    ╚═══════════════════════════════════════╝
    """)

def main():
    banner()
    
    parser = argparse.ArgumentParser(description='MxForce Brutte - Herramienta de fuerza bruta')
    parser.add_argument('-t', '--type', choices=['hash', 'http', 'http-basic', 'http-form'], 
                        required=True, help='Tipo de ataque')
    parser.add_argument('-H', '--hash', help='Hash objetivo (para modo hash)')
    parser.add_argument('-f', '--hash-file', help='Archivo con hashes (uno por línea)')
    parser.add_argument('-u', '--url', help='URL objetivo (para modo http)')
    parser.add_argument('-U', '--user', default='admin', help='Usuario (default: admin)')
    parser.add_argument('-w', '--wordlist', required=True, help='Diccionario de contraseñas')
    parser.add_argument('-T', '--threads', type=int, default=4, help='Número de hilos (default: 4)')
    
    args = parser.parse_args()
    
    # Verificar que wordlist existe
    if not os.path.exists(args.wordlist):
        print(f"❌ Error: No se encuentra el wordlist '{args.wordlist}'")
        sys.exit(1)
    
    # Modo hash
    if args.type == 'hash':
        if not args.hash and not args.hash_file:
            print("❌ Error: Especifica -H o -f para el modo hash")
            sys.exit(1)
        
        cracker = HashCracker(args.wordlist, args.threads)
        
        if args.hash:
            cracker.crack_single(args.hash)
        elif args.hash_file:
            cracker.crack_file(args.hash_file)
    
    # Modo HTTP
    elif args.type in ['http', 'http-basic', 'http-form']:
        if not args.url:
            print("❌ Error: Especifica -u URL para el modo HTTP")
            sys.exit(1)
        
        brute = HTTPBrute(args.url, args.user, args.wordlist, args.threads, args.type)
        brute.start()
    
    else:
        print("❌ Modo no implementado aún")

if __name__ == "__main__":
    main()
