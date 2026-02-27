"""
TikTok Canlı Yayın Ajanı - Seslendirme Modülü
Yorumları sese dönüştürür
"""
import threading
import queue
import time
from typing import Optional

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pyttsx3 = None  # type: ignore
    TTS_AVAILABLE = False
    print("Uyarı: pyttsx3 kurulu değil. Seslendirme özelliği devre dışı.")

# gTTS fallback for server environments
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    gTTS = None
    GTTS_AVAILABLE = False
    print("Uyarı: gTTS kurulu değil. Sunucu modunda seslendirme çalışmayabilir.")

# Çeviri desteği
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    # Yedek çeviri fonksiyonu
    def GoogleTranslator(source='auto', target='tr'):
        class Translator:
            def translate(self, text):
                return text  # Çeviri yoksa orijinal metni döndür
        return Translator()

try:
    from colorama import Fore as _Fore, Style as _Style
    COLORS_ENABLED = True

    class Fore:
        GREEN = _Fore.GREEN
        RED = _Fore.RED
        YELLOW = _Fore.YELLOW
        CYAN = _Fore.CYAN
        MAGENTA = _Fore.MAGENTA
        BLUE = _Fore.BLUE
        WHITE = _Fore.WHITE

    class Style:
        RESET_ALL = _Style.RESET_ALL

except ImportError:
    COLORS_ENABLED = False

    class Fore:
        GREEN = RED = YELLOW = CYAN = MAGENTA = BLUE = WHITE = ""

    class Style:
        RESET_ALL = ""


class TextToSpeech:
    """Yazıyı sese dönüştüren sınıf"""

    def __init__(self, config: Optional[dict] = None):
        """TTS motorunu başlat"""
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.rate = self.config.get("rate", 150)  # Konuşma hızı
        self.volume = self.config.get("volume", 1.0)  # Ses seviyesi
        self.voice_id = self.config.get("voice_id", None)  # Ses seçimi
        self.language = self.config.get("language", "turkish") # Dil seçimi
        self.language_code = self.config.get("language_code", "tr") # Dil kodu seçimi

        # Çeviri ayarları
        self.translate_enabled = self.config.get("translate_enabled", False)
        self.translate_to = self.config.get("translate_to", "tr")
        self._translator = None
        if self.translate_enabled and TRANSLATOR_AVAILABLE:
            try:
                self._translator = GoogleTranslator(source='auto', target=self.translate_to)
                if COLORS_ENABLED:
                    print(f"{Fore.GREEN}✅ Çeviri özelliği aktif: {self.translate_to}'ye çeviri{Style.RESET_ALL}")
            except Exception as e:
                if COLORS_ENABLED:
                    print(f"{Fore.YELLOW}⚠️  Çeviri başlatılamadı: {e}{Style.RESET_ALL}")
        
        # Ses kuyruğu
        self.speech_queue = queue.Queue()
        self.speaking = False
        self.stop_speaking = False
        
        if TTS_AVAILABLE and self.enabled:
            self._start_speech_thread()
            if COLORS_ENABLED:
                print(f"{Fore.GREEN}✅ TTS motoru başlatıldı{Style.RESET_ALL}")

    def _start_speech_thread(self):
        """Seslendirme iş parçacığını başlat"""
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
    
    def _init_engine(self):
        """pyttsx3 motorunu başlat ve ayarları uygula"""
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.setProperty('volume', self.volume)
        
        # Ses seçimi
        if self.voice_id:
            engine.setProperty('voice', self.voice_id)
        else:
            voices = engine.getProperty('voices')
            selected_voice = None
            for voice in voices:
                if self.language.lower() in voice.name.lower() or self.language_code.lower() in voice.id.lower():
                    selected_voice = voice.id
                    break
            
            if selected_voice:
                engine.setProperty('voice', selected_voice)
            else:
                if COLORS_ENABLED:
                    print(f"{Fore.YELLOW}⚠️  '{self.language}' dilinde ses bulunamadı. Varsayılan ses kullanılacak.{Style.RESET_ALL}")
        
        return engine

    def _speech_worker(self):
        """Seslendirme işçisi - kuyruktaki metinleri seslendirir"""
        # Motor bir kez oluşturulur ve thread boyunca yeniden kullanılır
        engine = None
        use_gtts = False
        
        try:
            engine = self._init_engine()
        except Exception as e:
            if COLORS_ENABLED:
                print(f"{Fore.YELLOW}⚠️  pyttsx3 başarısız, gTTS deneniyor...{Style.RESET_ALL}")
            
            # gTTS fallback
            if GTTS_AVAILABLE:
                use_gtts = True
                if COLORS_ENABLED:
                    print(f"{Fore.GREEN}✓ gTTS modunda çalışıyor{Style.RESET_ALL}")
            else:
                if COLORS_ENABLED:
                    print(f"{Fore.RED}❌ TTS motor başlatma hatası: {e}{Style.RESET_ALL}")
                return

        while not self.stop_speaking:
            try:
                # Kuyruktan mesaj al (bekleme süresi 1 saniye)
                text = self.speech_queue.get(timeout=1)
                
                if text is None:  # Durdurma sinyali
                    break
                
                self.speaking = True
                print(f"[TTS Worker] Mesaj alındı: {text[:30]}...")
                
                if use_gtts:
                    # gTTS ile seslendir
                    try:
                        tts = gTTS(text=text, lang=self.language_code[:2] if self.language_code else 'en')
                        tts.save("/tmp/tts_output.mp3")
                        import os
                        os.system("ffplay -nodisp -autoexit /tmp/tts_output.mp3 >/dev/null 2>&1 || mpg123 /tmp/tts_output.mp3 >/dev/null 2>&1 || play /tmp/tts_output.mp3 >/dev/null 2>&1 || echo 'Audio playback not available'")
                    except Exception as gtts_err:
                        if COLORS_ENABLED:
                            print(f"{Fore.RED}gTTS hatası: {gtts_err}{Style.RESET_ALL}")
                else:
                    # pyttsx3 ile seslendir
                    try:
                        # Ayarlar değiştiyse güncelle
                        engine.setProperty('rate', self.rate)
                        engine.setProperty('volume', self.volume)
                        
                        engine.say(text)
                        engine.runAndWait()

                    except Exception as e:
                        if COLORS_ENABLED:
                            print(f"{Fore.RED}❌ TTS motor hatası: {e} — Motor yeniden başlatılıyor...{Style.RESET_ALL}")
                    # Motor bozulduysa yeniden başlat
                    try:
                        engine = self._init_engine()
                    except Exception as reinit_err:
                        if COLORS_ENABLED:
                            print(f"{Fore.RED}❌ TTS motor yeniden başlatılamadı: {reinit_err}{Style.RESET_ALL}")

                self.speaking = False
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                if COLORS_ENABLED:
                    print(f"{Fore.RED}❌ Seslendirme hatası: {e}{Style.RESET_ALL}")
                self.speaking = False
        
        # Thread sonlanırken motoru temizle
        try:
            if engine:
                engine.stop()
        except Exception:
            pass
    
    def translate_text(self, text: str) -> str:
        """Metni çevir"""
        if not self.translate_enabled or not self._translator:
            return text

        try:
            translated = self._translator.translate(text)
            if translated and translated != text:
                if COLORS_ENABLED:
                    print(f"{Fore.CYAN}🌐 Çeviri: {text} → {translated}{Style.RESET_ALL}")
                return translated
        except Exception as e:
            if COLORS_ENABLED:
                print(f"{Fore.YELLOW}⚠️  Çeviri hatası: {e}{Style.RESET_ALL}")
        return text

    def speak(self, text: str, translate: bool = True):
        """Metni seslendir"""
        if not self.enabled or not TTS_AVAILABLE:
            print(f"[TTS] Seslendirme devre dışı: enabled={self.enabled}, TTS_AVAILABLE={TTS_AVAILABLE}")
            return

        if text and len(text.strip()) > 0:
            # Çeviri isteniyorsa ve yorum ise çevir
            if translate and self.translate_enabled:
                text = self.translate_text(text)

            self.speech_queue.put(text)
            print(f"[TTS] Kuyruğa eklendi: {text[:30]}...")
            if COLORS_ENABLED:
                print(f"{Fore.CYAN}🔊 Seslendiriliyor: {text}{Style.RESET_ALL}")
            else:
                print(f"[SES] {text}")
    
    def speak_event(self, event_type: str, text: str):
        """Olayı seslendir"""
        full_text = f"{event_type}: {text}"
        self.speak(full_text)
    
    def stop(self):
        """Seslendirmeyi durdur"""
        self.stop_speaking = True
        self.speech_queue.put(None)  # Durdurma sinyali
    
    def is_speaking(self):
        """Şu an seslendirme yapıyor mu?"""
        return self.speaking
    
    def set_rate(self, rate: int):
        """Konuşma hızını değiştir"""
        self.rate = rate
    
    def set_volume(self, volume: float):
        """Ses seviyesini değiştir (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))


class SpeechHandler:
    """Olayları seslendirmek için yardımcı sınıf"""
    
    def __init__(self, tts: TextToSpeech, config: dict):
        self.tts = tts
        self.config = config
        self.events = config.get("events", {})
    
    def should_speak(self, event_type: str) -> bool:
        """Bu olay seslendirilmeli mi?"""
        # Ana enabled kontrolü
        enabled = self.config.get("enabled", False)
        if not enabled:
            print(f"[TTS] Seslendirme kapalı: {event_type}")
            return False
        result = self.events.get(event_type, True)
        print(f"[TTS] should_speak({event_type}): {result}")
        return result
    
    def on_comment(self, username: str, comment: str):
        """Yorum seslendir"""
        if self.should_speak("comment"):
            print(f"[TTS] Yorum seslendiriliyor: {username}: {comment}")
            text = f"{username} dedi ki: {comment}"
            # Yorumları çevir (translate=True)
            self.tts.speak(text, translate=True)
    
    def on_gift(self, username: str, gift_name: str, count: int):
        """Hediye seslendir"""
        if self.should_speak("gift"):
            if count > 1:
                text = f"{username}, {count} tane {gift_name} hediye etti!"
            else:
                text = f"{username}, {gift_name} hediye etti!"
            self.tts.speak(text)
    
    def on_follow(self, username: str):
        """Takip seslendir"""
        if self.should_speak("follow"):
            text = f"{username} takip etti!"
            self.tts.speak(text)
    
    def on_join(self, username: str):
        """Katılım seslendir"""
        if self.should_speak("join"):
            text = f"{username} yayına katıldı"
            self.tts.speak(text)
    
    def on_like(self, username: str, count: int):
        """Beğeni seslendir"""
        if self.should_speak("like"):
            text = f"{username} {count} beğeni gönderdi"
            self.tts.speak(text)
    
    def on_share(self, username: str):
        """Paylaşım seslendir"""
        if self.should_speak("share"):
            text = f"{username} yayını paylaştı"
            self.tts.speak(text)
