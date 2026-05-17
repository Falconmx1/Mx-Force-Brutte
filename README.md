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

🚀 EJEMPLOS DE USO CON LAS NUEVAS FEATURES
# 1. Crackear SHA512
python mxforce.py -t hash -H "c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec" -w wordlists/rockyou.txt -T 8

# 2. Crackear NTLM
python mxforce.py -t hash -H "8846f7eaee8fb117ad06bdd830b7586c" -w wordlists/rockyou.txt

# 3. Fuerza bruta pura (sin wordlist) - prueba todas combinaciones
python mxforce.py -t bruteforce -H "5f4dcc3b5aa765d61d8327deb882cf99" --min-len 1 --max-len 4 --charset lower_digits

# 4. Ataque a SSH con proxy y evasión
python mxforce.py -t ssh --host 192.168.1.100 -U root -w passwords.txt --proxy http://127.0.0.1:8080 --delay 0.5 -T 4

# 5. Ataque a FTP guardando resultados
python mxforce.py -t ftp --host 10.0.0.5 -U admin -w rockyou.txt -o creds_encontradas.txt -T 8

# 6. HTTP con delay random (modo evasión)
python mxforce.py -t http -u http://target.com/login -U admin -w passwords.txt --delay 1 -T 2

# 7. Todo junto: hash + proxy + output + evasión
python mxforce.py -t hash -H hash.txt -w wordlist.txt --proxy http://127.0.0.1:8080 --delay 0.3 -o resultados.txt -T 10
