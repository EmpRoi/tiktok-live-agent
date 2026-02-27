"""
TikTok Canlı Yayın Ajanı - Gelişmiş Versiyon
Tüm özelliklerle birlikte tam fonksiyonel ajan
"""
import json
import asyncio
import re
from datetime import datetime
from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent, DisconnectEvent, CommentEvent, GiftEvent, LikeEvent,
    FollowEvent, ShareEvent, JoinEvent, RoomUserSeqEvent, 
    BarrageEvent, RankTextEvent, PollEvent, QuestionNewEvent,
    EmoteChatEvent, ImDeleteEvent, RoomPinEvent, LiveEndEvent
)

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLORS_ENABLED = True
except ImportError:
    COLORS_ENABLED = False
    # Fallback sınıfları
    class Fore:
        GREEN = RED = YELLOW = CYAN = MAGENTA = BLUE = WHITE = ""
    class Style:
        RESET_ALL = BRIGHT = ""
    class Back:
        BLACK = ""

# Yerel modülleri import et
from statistics import Statistics
from moderator import Moderator
from commands import CommandHandler
from commenter import TikTokCommenter, AutoResponder
from speech import TextToSpeech, SpeechHandler
from panel import start_panel_in_thread


class TikTokLiveAgent:
    """Gelişmiş TikTok Canlı Yayın Ajanı"""
    
    def __init__(self, config_file: str = "config.json"):
        """Ajanı başlat"""
        # Yapılandırmayı yükle
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # TikTok istemcisini oluştur
        unique_id = self.config["tiktok"]["unique_id"]
        self.client = TikTokLiveClient(unique_id=unique_id)
        
        # Modülleri başlat
        self.stats = Statistics()
        self.moderator = Moderator(self.config["moderation"])
        self.command_handler = CommandHandler(self.config, self.stats)

        # Seslendirme modülünü başlat
        self.tts = TextToSpeech(self.config.get("speech", {}))
        self.speech_handler = SpeechHandler(self.tts, self.config.get("speech", {}))
        
        # Özellik bayrakları
        self.features = self.config["features"]
        self.messages = self.config["messages"]
        self.responses = self.config["responses"]
        
        # Event handler'ları kaydet
        self._register_events()
        
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}🚀 TikTok Canlı Yayın Ajanı Başlatılıyor...")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
    
    def _register_events(self):
        """Tüm event handler'ları kaydet"""
        self.client.add_listener(ConnectEvent, self.on_connect)
        self.client.add_listener(DisconnectEvent, self.on_disconnect)
        self.client.add_listener(CommentEvent, self.on_comment)
        self.client.add_listener(GiftEvent, self.on_gift)
        self.client.add_listener(LikeEvent, self.on_like)
        self.client.add_listener(LiveEndEvent, self.on_live_end)
        
        if self.features["welcome_users"]:
            self.client.add_listener(JoinEvent, self.on_join)
        
        if self.features["thank_followers"]:
            self.client.add_listener(FollowEvent, self.on_follow)
        
        if self.features["thank_sharers"]:
            self.client.add_listener(ShareEvent, self.on_share)
        
        if self.features["track_statistics"]:
            self.client.add_listener(RoomUserSeqEvent, self.on_viewer_update)
        
        if self.features["vip_recognition"]:
            self.client.add_listener(BarrageEvent, self.on_vip_join)
            self.client.add_listener(RankTextEvent, self.on_rank_update)
        
        if self.features["poll_tracking"]:
            self.client.add_listener(PollEvent, self.on_poll)
        
        if self.features["question_tracking"]:
            self.client.add_listener(QuestionNewEvent, self.on_question)
        
        if self.features["moderation"]:
            self.client.add_listener(ImDeleteEvent, self.on_message_deleted)
            self.client.add_listener(RoomPinEvent, self.on_message_pinned)
        
        self.client.add_listener(EmoteChatEvent, self.on_emote)
    
    async def on_connect(self, event: ConnectEvent):
        """Bağlantı kurulduğunda"""
        self.print_event(
            "BAĞLANTI",
            f"@{event.unique_id} yayınına bağlanıldı! (Oda ID: {self.client.room_id})",
            Fore.GREEN
        )
    
    async def on_disconnect(self, event: DisconnectEvent):
        """Bağlantı kesildiğinde"""
        self.print_event("BAĞLANTI KESİLDİ", "Yayın bağlantısı sonlandı", Fore.RED)
        
        # İstatistikleri kaydet ve göster
        if self.config["statistics"]["save_to_file"]:
            filename = self.stats.save_to_file()
            print(f"{Fore.YELLOW}📁 İstatistikler kaydedildi: {filename}{Style.RESET_ALL}")
        
        if self.config["statistics"]["show_summary"]:
            self.stats.print_summary()
    
    async def on_live_end(self, event: LiveEndEvent):
        """Yayın sonlandığında"""
        self.print_event("YAYIN SONU", "Canlı yayın sona erdi!", Fore.RED)
    
    async def on_comment(self, event: CommentEvent):
        """Yorum geldiğinde"""
        username = event.user.nickname
        comment = event.comment
        
        # İstatistik güncelle
        if self.features["track_statistics"]:
            self.stats.add_comment(username)
        
        # Moderasyon kontrolü
        if self.features["moderation"]:
            # Spam kontrolü
            if self.moderator.check_spam(username):
                self.print_event(
                    "SPAM TESPİT",
                    f"{username} spam yapıyor!",
                    Fore.RED
                )
                if self.moderator.should_warn(username):
                    print(f"{Fore.YELLOW}⚠️  [UYARI -> {username}]: Lütfen spam yapmayın!{Style.RESET_ALL}")
                return
            
            # Kötü kelime kontrolü
            if self.moderator.check_bad_words(comment):
                self.print_event(
                    "UYGUNSUZ İÇERİK",
                    f"{username}: Uygunsuz kelime tespit edildi",
                    Fore.RED
                )
                return
        
        # Komut kontrolü
        if self.features["commands"] and self.command_handler.is_command(comment):
            response = self.command_handler.handle_command(comment, username)
            if response:
                self.command_handler.print_command_response(response, username)
            return
        
        # Normal yorum
        self.print_event("YORUM", f"{username}: {comment}", Fore.CYAN)

        # Yorumu seslendir
        self.speech_handler.on_comment(username, comment)

        # Otomatik yanıtlar
        comment_lower = comment.lower()
        for keyword, response_template in self.responses.items():
            if keyword in comment_lower:
                # Güvenli formatlama - sadece izin verilen değişkenleri kabul et
                response = self._safe_format(response_template, username=username)
                self.print_event("AJAN YANITI", response, Fore.MAGENTA)
                break
    
    async def on_gift(self, event: GiftEvent):
        """Hediye geldiğinde"""
        username = event.user.nickname
        gift_name = event.gift.info.name
        
        # Streak kontrolü
        if event.gift.streakable and not event.gift.streaking:
            count = event.gift.repeat_count
            gift_value = event.gift.info.diamond_count
            
            # İstatistik güncelle
            if self.features["track_statistics"]:
                self.stats.add_gift(username, gift_name, count, gift_value)
            
            # Hediye mesajı
            message = self._get_gift_message(username, gift_name, count)
            self.print_event("HEDİYE", message, Fore.YELLOW)
            
        elif not event.gift.streakable:
            gift_value = event.gift.info.diamond_count
            
            # İstatistik güncelle
            if self.features["track_statistics"]:
                self.stats.add_gift(username, gift_name, 1, gift_value)
            
            message = self._safe_format(
                self.messages["gift_small"],
                nickname=username,
                gift_name=gift_name
            )
            self.print_event("HEDİYE", message, Fore.YELLOW)
    
    def _safe_format(self, template: str, **kwargs) -> str:
        """Güvenli formatlama - format string injection koruması"""
        # Sadece izin verilen değişkenleri kontrol et
        allowed_vars = {'nickname', 'gift_name', 'count', 'username'}
        for key in kwargs:
            if key not in allowed_vars:
                raise ValueError(f"İzin verilmeyen değişken: {key}")

        # Template'deki tüm {} yer tutucularını {var} formatına dönüştür
        # Önce {something} -> something olarak çıkar
        def replace_placeholder(match):
            full_match = match.group(0)
            # {something} -> something olarak çıkar
            var = full_match[1:-1].split('!')[0].split(':')[0].strip()
            if var in allowed_vars:
                return full_match
            # İzin verilmeyen değişken varsa, hata yerine güvenli metin koy
            return "{**}"

        # Basit kontrol: sadece {nickname}, {username}, {gift_name}, {count} izin ver
        safe_template = re.sub(r'\{(?!nickname|username|gift_name|count\})[^}]*\}', '{**}', template)
        try:
            return safe_template.format(**kwargs)
        except (KeyError, ValueError):
            return "Mesaj formatı hatalı"

    def _get_gift_message(self, username: str, gift_name: str, count: int) -> str:
        """Hediye sayısına göre mesaj seç"""
        if count >= 100:
            template = self.messages["gift_large"]
        elif count >= 10:
            template = self.messages["gift_medium"]
        else:
            template = self.messages["gift_small"]

        return self._safe_format(template, nickname=username, gift_name=gift_name, count=count)
    
    async def on_like(self, event: LikeEvent):
        """Beğeni geldiğinde"""
        username = event.user.nickname
        count = event.count
        
        # İstatistik güncelle
        if self.features["track_statistics"]:
            self.stats.add_like(username, count)
        
        self.print_event(
            "BEĞENİ",
            f"{username} {count}x beğendi! (Toplam: {event.total_like_count})",
            Fore.MAGENTA
        )
    
    async def on_join(self, event: JoinEvent):
        """Kullanıcı katıldığında"""
        username = event.user.nickname
        
        # İstatistik güncelle
        if self.features["track_statistics"]:
            self.stats.add_join()
        
        message = self._safe_format(self.messages["welcome"], nickname=username)
        self.print_event("KATILIM", message, Fore.GREEN)
    
    async def on_follow(self, event: FollowEvent):
        """Takip edildiğinde"""
        username = event.user.nickname
        
        # İstatistik güncelle
        if self.features["track_statistics"]:
            self.stats.add_follow()
        
        message = self._safe_format(self.messages["follow"], nickname=username)
        self.print_event("TAKİP", message, Fore.GREEN)
    
    async def on_share(self, event: ShareEvent):
        """Paylaşım yapıldığında"""
        username = event.user.nickname
        
        # İstatistik güncelle
        if self.features["track_statistics"]:
            self.stats.add_share()
        
        message = self._safe_format(self.messages["share"], nickname=username)
        self.print_event("PAYLAŞIM", message, Fore.GREEN)
    
    async def on_viewer_update(self, event: RoomUserSeqEvent):
        """İzleyici sayısı güncellendiğinde"""
        viewer_count = event.total_user
        
        # İstatistik güncelle
        if self.features["track_statistics"]:
            self.stats.update_viewers(viewer_count)
        
        self.print_event(
            "İZLEYİCİ",
            f"Anlık izleyici: {viewer_count}",
            Fore.BLUE
        )
    
    async def on_vip_join(self, event: BarrageEvent):
        """VIP kullanıcı katıldığında"""
        username = event.user.nickname
        
        # İstatistik güncelle
        if self.features["track_statistics"]:
            self.stats.add_vip_user(username)
        
        message = self._safe_format(self.messages["vip_join"], nickname=username)
        self.print_event("VIP", message, Fore.YELLOW)
    
    async def on_rank_update(self, event: RankTextEvent):
        """Sıralama güncellendiğinde"""
        # Top 3'e giren kullanıcıları bildir
        self.print_event(
            "SIRALAMA",
            "Hediye sıralaması güncellendi!",
            Fore.YELLOW
        )
    
    async def on_poll(self, event: PollEvent):
        """Anket başlatıldığında"""
        self.print_event(
            "ANKET",
            f"Yeni anket başlatıldı!",
            Fore.CYAN
        )
    
    async def on_question(self, event: QuestionNewEvent):
        """Soru sorulduğunda"""
        username = event.user.nickname
        self.print_event(
            "SORU",
            f"{username} bir soru sordu!",
            Fore.CYAN
        )
    
    async def on_emote(self, event: EmoteChatEvent):
        """Emoji gönderildiğinde"""
        username = event.user.nickname
        self.print_event(
            "EMOJİ",
            f"{username} emoji gönderdi!",
            Fore.MAGENTA
        )
    
    async def on_message_deleted(self, event: ImDeleteEvent):
        """Mesaj silindiğinde"""
        self.print_event(
            "MODERASYON",
            "Bir mesaj silindi",
            Fore.RED
        )
    
    async def on_message_pinned(self, event: RoomPinEvent):
        """Mesaj sabitlendiğinde"""
        self.print_event(
            "SABİTLENDİ",
            "Bir mesaj sabitlend!",
            Fore.YELLOW
        )
    
    def print_event(self, event_type: str, message: str, color):
        """Olayı renkli yazdır"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.config["display"]["colored_output"] and COLORS_ENABLED:
            print(f"{color}[{timestamp}] [{event_type}] {message}{Style.RESET_ALL}")
        else:
            print(f"[{timestamp}] [{event_type}] {message}")
    
    async def run(self):
        """Ajanı çalıştır"""
        unique_id = self.config['tiktok']['unique_id']
        check_interval = self.config.get("tiktok", {}).get("check_interval", 30)
        
        while True:
            try:
                if await self.client.is_live():
                    print(f"{Fore.GREEN}✅ @{unique_id} canlı yayında! Bağlanılıyor...{Style.RESET_ALL}\n")
                    await self.client.connect()
                    break
                else:
                    print(f"{Fore.YELLOW}⏳ @{unique_id} şu an canlı yayında degil. {check_interval} saniye sonra tekrar kontrol edilecek... (Durdurmak icin Ctrl+C){Style.RESET_ALL}")
                    await asyncio.sleep(check_interval)
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️  Kullanici tarafindan durduruldu{Style.RESET_ALL}")
                return
            except Exception as e:
                print(f"{Fore.RED}❌ Hata olustu: {e}{Style.RESET_ALL}")
                await asyncio.sleep(check_interval)
        
        if self.config["statistics"]["save_to_file"]:
            filename = self.stats.save_to_file()
            print(f"{Fore.YELLOW}📁 İstatistikler kaydedildi: {filename}{Style.RESET_ALL}")
        
        if self.config["statistics"]["show_summary"]:
            self.stats.print_summary()


def main():
    """Ana fonksiyon"""
    import os
    port = int(os.environ.get('PORT', 8081))
    
    print(f"""
{Fore.CYAN}{'='*70}
    ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗
    ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝
       ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝ 
       ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗ 
       ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗
       ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                    
    🤖 CANLI YAYIN AJANI - Gelişmiş Versiyon v2.0
{'='*70}{Style.RESET_ALL}
    """)
    
    start_panel_in_thread(port)
    
    try:
        agent = TikTokLiveAgent()
        asyncio.run(agent.run())
    except FileNotFoundError:
        print(f"{Fore.RED}❌ Hata: config.json dosyası bulunamadı!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Lütfen config.json dosyasını oluşturun.{Style.RESET_ALL}")
    except json.JSONDecodeError:
        print(f"{Fore.RED}❌ Hata: config.json dosyası geçersiz!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Beklenmeyen hata: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
