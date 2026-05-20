#!/usr/bin/env python3
"""
MxForce Brutte v3.0 - Herramienta de fuerza bruta multi-propósito
Author: Falconmx1
GitHub: https://github.com/Falconmx1/Mx-Force-Brutte
"""
import argparse
import sys
import os
import signal
import json
from datetime import datetime

# Core modules
from core.hash_cracker import HashCracker
from core.http_brute import HTTPBrute
from core.service_attacks import ServiceAttacker
from core.bruteforce_gen import BruteforceGenerator
from core.rule_engine import RuleEngine
from core.rdp_attack import RDPAttacker
from core.db_attack import DBAttacker
from core.wpa_handshake import WPACapturer
from core.distributed_attack import DistributedMaster, DistributedWorker

# Para la interfaz web
import subprocess
import threading

VERSION = "3.0.0"

def banner():
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║  🔓 MxForce Brutte v{} - FULL EDITION                              ║
    ║  "La seguridad no existe, solo contraseñas que no hemos roto"      ║
    ║  Hecho en México 🇲🇽                                               ║
    ║                                                                     ║
    ║  Modos disponibles:                                                 ║
    ║  • Hash Cracker (MD5, SHA1, SHA256, SHA512, NTLM, bcrypt)          ║
    ║  • HTTP/HTTPS Brute Force                                          ║
    ║  • SSH Brute Force                                                 ║
    ║  • FTP Brute Force                                                 ║
    ║  • RDP Brute Force                                                 ║
    ║  • MySQL/PostgreSQL Brute Force                                    ║
    ║  • WPA2 Handshake Capture & Crack                                  ║
    ║  • Pure Brute Force (sin wordlist)                                 ║
    ║  • Hashcat-style Rules Engine                                      ║
    ║  • Distributed Network Attacks                                     ║
    ║  • Web Interface (Flask)                                           ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """.format(VERSION))

def signal_handler(sig, frame):
    print("\n\n⚠️  Ataque interrumpido por el usuario")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    banner()
    
    parser = argparse.ArgumentParser(
        description='MxForce Brutte - Herramienta de fuerza bruta completa',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS DE USO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔐 HASH CRACKER:
    python mxforce.py -t hash -H 5f4dcc3b5aa765d61d8327deb882cf99 -w rockyou.txt
    python mxforce.py -t hash -f hashes.txt -w rockyou.txt -T 8 -o resultados.txt

  🌐 HTTP BRUTE:
    python mxforce.py -t http -u http://target.com/login -U admin -w passwords.txt
    python mxforce.py -t http-form -u http://target.com/login -U root -w rockyou.txt --delay 0.5

  🖥️  SSH ATTACK:
    python mxforce.py -t ssh --host 192.168.1.100 -U root -w rockyou.txt -T 8

  💻 RDP ATTACK:
    python mxforce.py -t rdp --host 192.168.1.100 -U Administrator -w rockyou.txt

  🗄️  DATABASE ATTACK:
    python mxforce.py -t mysql --host localhost -U root -w passwords.txt
    python mxforce.py -t postgresql --host 192.168.1.50 -U postgres -w rockyou.txt

  📡 WPA2 ATTACK:
    python mxforce.py -t wpa2 --wifi-interface wlan0 --bssid AA:BB:CC:DD:EE:FF
    python mxforce.py -t wpa2 --crack-handshake capture-01.cap -w rockyou.txt

  🔄 BRUTE FORCE PURO:
    python mxforce.py -t bruteforce -H 5f4dcc3b5aa765d61d8327deb882cf99 --min-len 1 --max-len 4

  📜 RULES ENGINE:
    python mxforce.py -t hash -H hash.txt -w passwords.txt --rules /usr/share/hashcat/rules/best64.rule

  🌐 WEB INTERFACE:
    python mxforce.py --web-interface --web-port 5000

  🔗 DISTRIBUTED MODE:
    python mxforce.py --master --port 5555
    python mxforce.py --worker 192.168.1.100
        """
    )
    
    # ==================== MODOS PRINCIPALES ====================
    parser.add_argument('-t', '--type', 
                        choices=['hash', 'http', 'http-basic', 'http-form', 'ssh', 'ftp', 
                                'rdp', 'mysql', 'postgresql', 'wpa2', 'bruteforce'],
                        help='Tipo de ataque')
    
    # ==================== OPCIONES PARA HASH ====================
    parser.add_argument('-H', '--hash', help='Hash objetivo (para modo hash/bruteforce)')
    parser.add_argument('-f', '--hash-file', help='Archivo con hashes (uno por línea)')
    
    # ==================== OPCIONES PARA HTTP/SSH/FTP/RDP/DB ====================
    parser.add_argument('-u', '--url', help='URL objetivo (para modo HTTP)')
    parser.add_argument('--host', help='Host objetivo (para SSH/FTP/RDP/DB)')
    parser.add_argument('-p', '--port', type=int, help='Puerto (default según servicio)')
    parser.add_argument('-U', '--user', default='admin', help='Usuario (default: admin)')
    
    # ==================== OPCIONES PARA WPA2 ====================
    parser.add_argument('--wifi-interface', help='Interfaz WiFi (ej: wlan0) para WPA2')
    parser.add_argument('--bssid', help='BSSID objetivo para WPA2')
    parser.add_argument('--channel', type=int, help='Canal WiFi objetivo')
    parser.add_argument('--capture-only', action='store_true', help='Solo capturar handshake, no crackear')
    parser.add_argument('--crack-handshake', help='Archivo .cap para crackear handshake')
    
    # ==================== WORDLIST Y BRUTEFORCE ====================
    parser.add_argument('-w', '--wordlist', help='Diccionario de contraseñas')
    parser.add_argument('--min-len', type=int, default=4, help='Longitud mínima (modo bruteforce)')
    parser.add_argument('--max-len', type=int, default=6, help='Longitud máxima (modo bruteforce)')
    parser.add_argument('--charset', 
                        choices=['lower', 'upper', 'digits', 'lower_digits', 'upper_digits', 'alnum', 'full'],
                        default='lower_digits', 
                        help='Conjunto de caracteres para bruteforce')
    
    # ==================== RULES ENGINE ====================
    parser.add_argument('--rules', help='Archivo de reglas estilo Hashcat')
    parser.add_argument('--apply-rules', help='Aplicar reglas a wordlist y generar nueva')
    
    # ==================== CONFIGURACIÓN GENERAL ====================
    parser.add_argument('-T', '--threads', type=int, default=4, help='Número de hilos (default: 4)')
    parser.add_argument('--delay', type=float, default=0, help='Delay random en segundos (modo evasión)')
    parser.add_argument('--proxy', help='Proxy (ej: http://127.0.0.1:8080 o socks5://127.0.0.1:9050)')
    parser.add_argument('-o', '--output', help='Guardar resultados en archivo')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout de conexión en segundos')
    
    # ==================== MODO DISTRIBUIDO ====================
    parser.add_argument('--master', action='store_true', help='Iniciar como master (servidor)')
    parser.add_argument('--worker', help='Conectar como worker a la IP del master')
    parser.add_argument('--master-port', type=int, default=5555, help='Puerto para modo distribuido')
    
    # ==================== INTERFAZ WEB ====================
    parser.add_argument('--web-interface', action='store_true', help='Iniciar interfaz web')
    parser.add_argument('--web-port', type=int, default=5000, help='Puerto para interfaz web (default: 5000)')
    parser.add_argument('--web-host', default='0.0.0.0', help='Host para interfaz web (default: 0.0.0.0)')
    
    # ==================== MODO SILENCIOSO ====================
    parser.add_argument('-q', '--quiet', action='store_true', help='Modo silencioso (menos output)')
    parser.add_argument('--no-banner', action='store_true', help='Ocultar banner')
    
    args = parser.parse_args()
    
    # Ocultar banner si se pide
    if args.no_banner:
        pass  # Ya no mostramos banner
    
    # ==================== INTERFAZ WEB ====================
    if args.web_interface:
        print("🌐 Iniciando interfaz web de MxForce Brutte...")
        print(f"📍 URL: http://{args.web_host}:{args.web_port}")
        print("⚠️  Presiona Ctrl+C para detener el servidor\n")
        
        try:
            from web_interface.app import app
            app.run(host=args.web_host, port=args.web_port, debug=False, use_reloader=False)
        except ImportError:
            print("❌ Error: No se encuentra web_interface.app")
            print("   Asegúrate de tener la estructura completa del proyecto")
            sys.exit(1)
        return
    
    # ==================== MODO DISTRIBUIDO ====================
    if args.master:
        print(f"🎯 Iniciando modo MASTER en puerto {args.master_port}")
        master = DistributedMaster(args.master_port)
        master.start_server()
        return
    
    if args.worker:
        print(f"🔗 Conectando como WORKER a {args.worker}:{args.master_port}")
        worker = DistributedWorker(args.worker, args.master_port)
        worker.connect()
        return
    
    # ==================== VALIDACIÓN DE MODO ====================
    if not args.type:
        parser.print_help()
        print("\n❌ Error: Especifica un modo de ataque con -t")
        sys.exit(1)
    
    # Configurar proxy si se especificó
    proxy_dict = None
    if args.proxy:
        proxy_dict = {'http': args.proxy, 'https': args.proxy}
        print(f"🔌 Usando proxy: {args.proxy}")
    
    # ==================== PROCESAMIENTO DE REGLAS ====================
    if args.rules and args.wordlist:
        print("📜 Aplicando reglas estilo Hashcat...")
        rule_engine = RuleEngine()
        rule_engine.load_rules(args.rules)
        
        output_wordlist = f"wordlist_with_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        rule_engine.generate_wordlist(args.wordlist, output_wordlist)
        args.wordlist = output_wordlist
        print(f"✅ Nueva wordlist generada: {output_wordlist}")
    
    # ==================== MODO WPA2 ====================
    if args.type == 'wpa2':
        if args.crack_handshake:
            if not args.wordlist:
                print("❌ Error: Para crackear handshake necesitas -w wordlist")
                sys.exit(1)
            
            capturer = WPACapturer('', '', '', '')
            password = capturer.crack_handshake(args.crack_handshake, args.wordlist)
            if password and args.output:
                with open(args.output, 'a') as f:
                    f.write(f"[WPA2] {args.crack_handshake} : {password}\n")
        
        elif args.wifi_interface:
            capturer = WPACapturer(args.wifi_interface, args.bssid, args.channel, args.output)
            
            if args.capture_only:
                print("📡 Modo captura solamente")
                if not capturer.enable_monitor_mode():
                    sys.exit(1)
                capturer.scan_networks(30)
                if args.bssid:
                    cap_file = capturer.capture_handshake(args.bssid, args.channel or 1, "Target")
                    if cap_file:
                        print(f"✅ Handshake guardado en: {cap_file}")
                capturer.cleanup()
            else:
                capturer.run_full_attack(args.wordlist)
        else:
            print("❌ Error: Para modo wpa2 necesitas --wifi-interface o --crack-handshake")
            sys.exit(1)
        return
    
    # ==================== MODO HASH ====================
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
        return
    
    # ==================== MODO BRUTEFORCE (sin wordlist) ====================
    if args.type == 'bruteforce':
        if not args.hash:
            print("❌ Error: Modo bruteforce requiere -H <hash>")
            sys.exit(1)
        
        cracker = HashCracker('', args.threads, args.delay, args.proxy, args.output)
        hash_type = cracker.detect_hash_type(args.hash)
        
        print(f"🔍 Hash tipo detectado: {hash_type.upper()}")
        print(f"📏 Longitud: {args.min_len}-{args.max_len}")
        print(f"🔤 Conjunto: {args.charset}")
        
        generator = BruteforceGenerator(args.min_len, args.max_len, args.charset, args.delay)
        generator.crack_hash(args.hash, cracker, hash_type)
        return
    
    # ==================== MODO HTTP ====================
    if args.type in ['http', 'http-basic', 'http-form']:
        if not args.url:
            print("❌ Error: Especifica -u URL para el modo HTTP")
            sys.exit(1)
        if not args.wordlist:
            print("❌ Error: Modo HTTP requiere -w wordlist")
            sys.exit(1)
        
        brute = HTTPBrute(args.url, args.user, args.wordlist, args.threads, 
                         args.type, args.delay, args.proxy, args.output)
        brute.start()
        return
    
    # ==================== MODO SSH ====================
    if args.type == 'ssh':
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
        return
    
    # ==================== MODO FTP ====================
    if args.type == 'ftp':
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
        return
    
    # ==================== MODO RDP ====================
    if args.type == 'rdp':
        if not args.host:
            print("❌ Error: Especifica --host para RDP")
            sys.exit(1)
        if not args.wordlist:
            print("❌ Error: Modo RDP requiere -w wordlist")
            sys.exit(1)
        
        port = args.port if args.port else 3389
        attacker = RDPAttacker(args.host, args.user, args.wordlist, 
                               args.threads, args.delay, args.output)
        attacker.attack()
        return
    
    # ==================== MODO MYSQL ====================
    if args.type == 'mysql':
        if not args.host:
            print("❌ Error: Especifica --host para MySQL")
            sys.exit(1)
        if not args.wordlist:
            print("❌ Error: Modo MySQL requiere -w wordlist")
            sys.exit(1)
        
        port = args.port if args.port else 3306
        attacker = DBAttacker(args.host, port, 'mysql', args.user, args.wordlist,
                              args.threads, args.delay, args.output)
        attacker.attack()
        return
    
    # ==================== MODO POSTGRESQL ====================
    if args.type == 'postgresql':
        if not args.host:
            print("❌ Error: Especifica --host para PostgreSQL")
            sys.exit(1)
        if not args.wordlist:
            print("❌ Error: Modo PostgreSQL requiere -w wordlist")
            sys.exit(1)
        
        port = args.port if args.port else 5432
        attacker = DBAttacker(args.host, port, 'postgresql', args.user, args.wordlist,
                              args.threads, args.delay, args.output)
        attacker.attack()
        return

if __name__ == "__main__":
    main()
