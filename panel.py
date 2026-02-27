"""
TikTok Live Agent - Web Kontrol Paneli
"""
import http.server
import socketserver
import json
import os
import tempfile
import shutil
import subprocess
import sys
import base64
import hashlib
from threading import Thread
from functools import wraps

def recursive_update(d, u):
    """Sözlükleri iç içe güncelleyen yardımcı fonksiyon"""
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = recursive_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

class ConfigPanelHandler(http.server.SimpleHTTPRequestHandler):
    """Kontrol paneli için HTTP isteklerini işleyen sınıf"""
    
    CONFIG_FILE = "config.json"

    # Sunucu modunda çalışıp çalışmadığını belirten bayrak
    SERVER_MODE = os.environ.get("TIKTOK_PANEL_SERVER", "false").lower() == "true"

    # Yönetici kullanıcı adı ve şifresi
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"  # admin123

    # Başlangıçta auth dosyasını yükle
    @classmethod
    def _load_auth(cls):
        """Auth dosyasından kullanıcı bilgilerini yükle"""
        auth_file = "panel_auth.json"
        if os.path.exists(auth_file):
            try:
                with open(auth_file, 'r', encoding='utf-8') as f:
                    auth_data = json.load(f)
                    cls.ADMIN_USERNAME = auth_data.get('username', 'admin')
                    cls.ADMIN_PASSWORD_HASH = auth_data.get('password_hash', cls.ADMIN_PASSWORD_HASH)
            except Exception:
                pass

    def _check_localhost(self):
        """Sadece localhost'tan gelen isteklere izin ver (proxy destekli)"""
        client_ip = self.client_address[0]

        # Proxy arkasındaki istekler için X-Forwarded-For kontrolü
        x_forwarded_for = self.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0].strip()

        # localhost kontrolü
        if client_ip in ('127.0.0.1', '::1', 'localhost'):
            return True

        # Sunucu modunda değilse localhost dışından gelen istekleri reddet
        if not self.SERVER_MODE:
            self.send_response(403)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Erişim reddedildi - Sadece localhost"}).encode('utf-8'))
            return False

        return True

    def _check_auth(self):
        """Basic authentication kontrolü"""
        # Sunucu modunda değilse auth gerekmez
        if not self.SERVER_MODE:
            return True

        auth_header = self.headers.get('Authorization')
        if not auth_header:
            return False

        try:
            # Basic auth format: "Basic base64(username:password)"
            auth_type, credentials = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                return False

            decoded = base64.b64decode(credentials).decode('utf-8')
            username, password = decoded.split(':', 1)

            # Şifreyi hashle ve karşılaştır
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Kullanıcı adı ve şifre hash kontrolü
            if username == self.ADMIN_USERNAME and password_hash == self.ADMIN_PASSWORD_HASH:
                return True
        except Exception:
            pass

        return False

    def _send_auth_required(self):
        """401 Unauthorized gönder"""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="TikTok Panel"')
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Kimlik doğrulama gerekli"}).encode('utf-8'))

    def do_GET(self):
        """GET isteklerini işle"""
        # Önce localhost kontrolü
        if not self._check_localhost():
            return

        # Sunucu modunda ise auth kontrolü yap
        if self.SERVER_MODE and not self._check_auth():
            self._send_auth_required()
            return

        if self.path == '/':
            self.path = 'panel/index.html'
        elif self.path == '/api/config':
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "config.json bulunamadı!"}).encode('utf-8'))
            return
        
        # Diğer tüm istekler için sadece panel/ dizininden servis et
        safe_path = os.path.normpath(os.path.join("panel", self.path.lstrip('/')))
        panel_root = os.path.normpath("panel")
        if not (safe_path.startswith(panel_root + os.sep) or safe_path == panel_root):
            self.send_response(403)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Erişim reddedildi"}).encode('utf-8'))
            return
        self.path = '/' + safe_path.replace('\\', '/')

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """POST isteklerini işle"""
        # Önce localhost kontrolü
        if not self._check_localhost():
            return

        # Sunucu modunda ise auth kontrolü yap
        if self.SERVER_MODE and not self._check_auth():
            self._send_auth_required()
            return

        MAX_BODY_SIZE = 1 * 1024 * 1024  # 1 MB

        if self.path == '/api/config':
            content_length_header = self.headers.get('Content-Length')
            if not content_length_header:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Content-Length başlığı eksik"}).encode('utf-8'))
                return
            try:
                content_length = int(content_length_header)
            except ValueError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Geçersiz Content-Length"}).encode('utf-8'))
                return

            if content_length > MAX_BODY_SIZE:
                self.send_response(413)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "İstek çok büyük (max 1 MB)"}).encode('utf-8'))
                return

            post_data = self.rfile.read(content_length)
            
            try:
                new_config = json.loads(post_data.decode('utf-8'))
                
                # Mevcut config'i oku
                try:
                    with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                except FileNotFoundError:
                    config_data = {}

                # Sadece değişen değerleri iç içe güncelle
                config_data = recursive_update(config_data, new_config)

                # Geçici dosyaya yaz, sonra taşı (atomik yazma)
                config_dir = os.path.dirname(os.path.abspath(self.CONFIG_FILE)) or '.'
                tmp_fd, tmp_path = tempfile.mkstemp(suffix='.json', dir=config_dir)
                try:
                    with os.fdopen(tmp_fd, 'w', encoding='utf-8') as tmp_f:
                        json.dump(config_data, tmp_f, ensure_ascii=False, indent=2)
                    # Başarılı yazma sonrası taşı
                    if os.path.exists(self.CONFIG_FILE):
                        os.replace(tmp_path, self.CONFIG_FILE)
                    else:
                        os.rename(tmp_path, self.CONFIG_FILE)
                except Exception:
                    # Hata durumunda geçici dosyayı temizle
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                    raise
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Ayarlar kaydedildi!"}).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Geçersiz JSON formatı"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                # Hata mesajında hassas bilgi gösterme
                self.wfile.write(json.dumps({"message": "Sunucu hatası oluştu"}).encode('utf-8'))

            return

        # Botu yeniden başlat
        if self.path == '/api/restart':
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Bot yeniden başlatılıyor..."}).encode('utf-8'))

                # main.py'yi yeniden başlat
                # Mevcut process'i sonlandır ve yeniden başlat
                subprocess.Popen([sys.executable, "main.py"],
                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0)
                os._exit(0)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Yeniden başlatma hatası"}).encode('utf-8'))
            return

        # Şifre değiştir
        if self.path == '/api/change-password':
            content_length_header = self.headers.get('Content-Length')
            if not content_length_header:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Content-Length başlığı eksik"}).encode('utf-8'))
                return

            try:
                content_length = int(content_length_header)
            except ValueError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Geçersiz Content-Length"}).encode('utf-8'))
                return

            if content_length > 1024:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "İstek çok büyük"}).encode('utf-8'))
                return

            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
                new_username = data.get('username', '').strip()
                new_password = data.get('password', '')

                if not new_username or not new_password:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "message": "Kullanıcı adı ve şifre gerekli"}).encode('utf-8'))
                    return

                if len(new_password) < 4:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "message": "Şifre en az 4 karakter olmalı"}).encode('utf-8'))
                    return

                # Şifreyi hashle ve kaydet
                password_hash = hashlib.sha256(new_password.encode()).hexdigest()

                # Auth dosyasını güncelle
                auth_file = "panel_auth.json"
                auth_data = {
                    "username": new_username,
                    "password_hash": password_hash
                }

                with open(auth_file, 'w', encoding='utf-8') as f:
                    json.dump(auth_data, f, ensure_ascii=False, indent=2)

                # Belleği güncelle
                ConfigPanelHandler.ADMIN_USERNAME = new_username
                ConfigPanelHandler.ADMIN_PASSWORD_HASH = password_hash

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": "Şifre başarıyla değiştirildi"}).encode('utf-8'))

            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Geçersiz JSON"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Sunucu hatası"}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()


def run_panel_server(port: int = 8080):
    """Kontrol paneli sunucusunu başlatır (localhost modu)"""
    # Panel dizinini ve ana sayfasını kontrol et
    if not os.path.exists("panel"):
        os.makedirs("panel")
    if not os.path.exists("panel/index.html"):
        with open("panel/index.html", "w", encoding='utf-8') as f:
            f.write("<h1>Kontrol Paneli</h1><p>index.html dosyası oluşturuldu.</p>")

    # Auth bilgilerini yükle
    ConfigPanelHandler._load_auth()
    ConfigPanelHandler.SERVER_MODE = False

    with socketserver.TCPServer(("", port), ConfigPanelHandler) as httpd:
        print(f"✅ Kontrol Paneli http://localhost:{port} adresinde çalışıyor")
        httpd.serve_forever()


def run_panel_server_production(port: int = 8080, password: str = None, username: str = None):
    """Kontrol paneli sunucusunu sunucu modunda başlatır (harici erişim için)

    Kullanım:
        # Basit kullanım
        from panel import run_panel_server_production
        run_panel_server_production(8080, "sifreniz", "kullaniciadi")

        # Veya panelden şifre değiştirin
    """
    if not os.path.exists("panel"):
        os.makedirs("panel")

    # Auth bilgilerini yükle (dosyadan veya parametreden)
    ConfigPanelHandler._load_auth()
    ConfigPanelHandler.SERVER_MODE = True

    # Şifre ayarla (parametre verilirse)
    if password:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        ConfigPanelHandler.ADMIN_PASSWORD_HASH = password_hash

    # Kullanıcı adı ayarla
    if username:
        ConfigPanelHandler.ADMIN_USERNAME = username

    with socketserver.TCPServer(("", port), ConfigPanelHandler) as httpd:
        print(f"✅ Kontrol Paneli (SUNUCU MODU) http://localhost:{port} adresinde çalışıyor")
        print(f"   Harici erişim için: http://sunucu-ip:{port}")
        print(f"   Kullanıcı adı: {ConfigPanelHandler.ADMIN_USERNAME}")
        print(f"   ⚠️  İlk kullanımda şifreyi değiştirin!")
        httpd.serve_forever()

def start_panel_in_thread(port: int = 8080):
    """Sunucuyu ayrı bir iş parçacığında başlat"""
    panel_thread = Thread(target=run_panel_server, args=(port,), daemon=True)
    panel_thread.start()
    return panel_thread

if __name__ == "__main__":
    run_panel_server()
