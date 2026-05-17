# 🔓 MxForce Brutte - Fuerza Bruta Hecha en México

> *"Porque la seguridad no existe, solo contraseñas que no hemos roto todavía"*

**MxForce Brutte** es una herramienta de fuerza bruta ofensiva para pentesters y entusiastas de la ciberseguridad. Diseñada para ser rápida, extensible y fácil de usar.

## ⚡ Características
- Crackeo de hashes (MD5, SHA1, SHA256, bcrypt)
- Ataque a formularios HTTP POST / Basic Auth
- Ataque con diccionario o generación de fuerza bruta (bruteforce)
- Multihilo para acelerar el proceso
- Soporte para wordlists comprimidas
- Logs detallados en tiempo real

## 📦 Instalación

```bash
git clone https://github.com/Falconmx1/MxForce-Brutte.git
cd MxForce-Brutte
pip install -r requirements.txt

🎮 Uso básico
bash

# Crackear un hash MD5
python mxforce.py -t hash -H 5f4dcc3b5aa765d61d8327deb882cf99 -w wordlists/rockyou.txt

# Fuerza bruta a login HTTP
python mxforce.py -t http -u https://ejemplo.com/login -U admin -w wordlists/passwords.txt

# Ataque completo con 8 hilos
python mxforce.py -t hash -H hash.txt -w wordlists/rockyou.txt -T 8

🧠 Modos soportados
Modo	Flag	Ejemplo
Hash cracker	-t hash	-H 5f4dcc...
HTTP Basic	-t http-basic	-u http://target.com/secret
HTTP Form	-t http-form	-u http://target.com/login
⚠️ Advertencia

    Esta herramienta solo debe usarse en sistemas con autorización explícita. El mal uso puede ser ilegal. No me hago responsable por daños a terceros.
