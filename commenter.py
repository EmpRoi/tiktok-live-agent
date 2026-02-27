"""
TikTok Yorum Botu - Selenium ile Tarayıcı Otomasyonu
Canlı yayınlara yorum yazmak için kullanılır
"""
import asyncio
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        GREEN = RED = YELLOW = CYAN = MAGENTA = BLUE = WHITE = ""
    class Style:
        RESET_ALL = ""


class TikTokCommenter:
    """TikTok Canlı Yayına Yorum Atan Bot"""
    
    def __init__(self, config: dict):
        """Yorumcu başlat"""
        self.config = config
        self.driver = None
        self.is_connected = False
        self.username = config.get("commenter", {}).get("username", "")
        self.password = config.get("commenter", {}).get("password", "")
        self.room_url = config.get("commenter", {}).get("room_url", "")
        self.comment_delay = config.get("commenter", {}).get("comment_delay", 2)
        self.headless = config.get("commenter", {}).get("headless", True)
        
        # Yorum k
        self.comment_queue = asyncio.Queue()
        
    def _init_browser(self):
        """Tarayıcıyı başlat"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        # Anti-tespit ayarları
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User Agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
    def login(self) -> bool:
        """TikTok hesabına giriş yap"""
        if not self.username or not self.password:
            print(f"{Fore.YELLOW}⚠️  Giriş bilgileri bulunamadı. Misafir olarak devam edilecek.{Style.RESET_ALL}")
            return False
            
        try:
            print(f"{Fore.CYAN}🔐 TikTok'a giriş yapılıyor...{Style.RESET_ALL}")
            self.driver.get("https://www.tiktok.com/login")
            time.sleep(3)
            
            # Telefon/Email ile giriş
            try:
                login_method = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Phone / Email / Username')]"))
                )
                login_method.click()
                time.sleep(2)
            except:
                pass
            
            # Kullanıcı adı girişi
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(self.username)
            time.sleep(1)
            
            # Şifre girişi
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(self.password)
            time.sleep(1)
            
            # Giriş butonu
            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
            login_btn.click()
            time.sleep(5)
            
            # Giriş kontrolü
            if "login" not in self.driver.current_url.lower():
                print(f"{Fore.GREEN}✅ Giriş başarılı!{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Giriş başarısız!{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Giriş hatası: {e}{Style.RESET_ALL}")
            return False
    
    def join_live(self, unique_id: str) -> bool:
        """Canlı yayına katıl"""
        try:
            print(f"{Fore.CYAN}📺 Canlı yayına katılınıyor: @{unique_id}{Style.RESET_ALL}")
            
            # Canlı yayın URL'si
            live_url = f"https://www.tiktok.com/@{unique_id}/live"
            self.driver.get(live_url)
            time.sleep(5)
            
            # Canlı yayın kontrolü
            if "live" in self.driver.current_url:
                print(f"{Fore.GREEN}✅ Canlı yayına katılındı!{Style.RESET_ALL}")
                self.is_connected = True
                return True
            else:
                print(f"{Fore.RED}❌ Canlı yayın bulunamadı!{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Yayına katılma hatası: {e}{Style.RESET_ALL}")
            return False
    
    async def post_comment(self, message: str) -> bool:
        """Yorum gönder"""
        if not self.is_connected:
            return False
            
        try:
            # Yorum kutusuna git
            comment_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='comment-input']"))
            )
            
            # Yorumu yaz
            comment_input.click()
            time.sleep(0.5)
            comment_input.send_keys(message)
            time.sleep(0.5)
            
            # Gönder butonunu bul ve tıkla
            post_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-e2e='comment-post']")
            post_btn.click()
            
            time.sleep(self.comment_delay)
            
            print(f"{Fore.GREEN}✅ Yorum gönderildi: {message}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Yorum gönderme hatası: {e}{Style.RESET_ALL}")
            return False
    
    async def auto_comment_loop(self, response_generator):
        """Otomatik yorum döngüsü"""
        print(f"{Fore.CYAN}🔄 Otomatik yorum döngüsü başlatıldı{Style.RESET_ALL}")
        
        while self.is_connected:
            try:
                # Yanıt bekle
                response = await asyncio.wait_for(
                    response_generator.get(),
                    timeout=1.0
                )
                
                if response:
                    await self.post_comment(response)
                    
            except asyncio.TimeoutError:
                # Timeout normal, devam et
                pass
            except Exception as e:
                print(f"{Fore.RED}❌ Yorum döngüsü hatası: {e}{Style.RESET_ALL}")
            
            await asyncio.sleep(0.5)
    
    def close(self):
        """Tarayıcıyı kapat"""
        if self.driver:
            self.driver.quit()
            print(f"{Fore.YELLOW}🔚 Tarayıcı kapatıldı{Style.RESET_ALL}")


class AutoResponder:
    """Otomatik Yanıt Üreteci"""
    
    def __init__(self, config: dict):
        self.config = config
        self.responses = config.get("auto_responses", {})
        self.queue = asyncio.Queue()
        
        # Özel yanıtlar
        self.custom_responses = config.get("custom_responses", {})
        
    async def generate_response(self, username: str, comment: str) -> str:
        """Yoruma otomatik yanıt üret"""
        comment_lower = comment.lower()

        # Özel komut kontrolü
        for keyword, response in self.custom_responses.items():
            if keyword in comment_lower:
                # Güvenli formatlama - sadece {username} izin ver
                return self._safe_format(response, username=username)

        # Anahtar kelime kontrolü
        for keyword, response in self.responses.items():
            if keyword in comment_lower:
                return self._safe_format(response, username=username)

        return None

    def _safe_format(self, template: str, **kwargs) -> str:
        """Güvenli formatlama - format string injection koruması"""
        import re
        allowed_vars = {'username', 'nickname', 'gift_name', 'count'}
        for key in kwargs:
            if key not in allowed_vars:
                raise ValueError(f"İzin verilmeyen değişken: {key}")

        # Sadece izin verilen değişkenleri tut
        safe_template = re.sub(r'\{(?!username|nickname|gift_name|count\})[^}]*\}', '{**}', template)
        try:
            return safe_template.format(**kwargs)
        except (KeyError, ValueError):
            return "Mesaj formatı hatalı"
    
    async def add_response(self, response: str):
        """Yanıt kuyruğuna ekle"""
        await self.queue.put(response)
    
    async def get(self):
        """Kuyruktan yanıt al"""
        return await self.queue.get()


def create_commenter(config: dict) -> TikTokCommenter:
    """Yorumcu oluştur"""
    return TikTokCommenter(config)


def create_responder(config: dict) -> AutoResponder:
    """Yanıt üreteci oluştur"""
    return AutoResponder(config)
