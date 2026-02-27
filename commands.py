"""
TikTok Live Agent - Komut Sistemi Modülü
"""
from typing import Optional
from statistics import Statistics
from colorama import Fore, Style


class CommandHandler:
    """Kullanıcı komutlarını işleyen sınıf"""
    
    def __init__(self, config: dict, stats: Statistics):
        self.commands = config.get("commands", {})
        self.stats = stats
        self.enabled = config.get("features", {}).get("commands", True)
        
    def is_command(self, message: str) -> bool:
        """Mesajın komut olup olmadığını kontrol et"""
        return message.startswith("!")
    
    def handle_command(self, command: str, username: str) -> Optional[str]:
        """Komutu işle ve yanıt döndür"""
        if not self.enabled:
            return None
            
        command = command.lower().strip()
        
        # Özel komutlar
        if command == "!stats":
            return self._handle_stats()
        elif command == "!top":
            return self._handle_top()
        elif command == "!hediye":
            return self._handle_gifts()
        elif command in self.commands:
            return self.commands[command]
        
        return None
    
    def _handle_stats(self) -> str:
        """İstatistik komutunu işle"""
        summary = self.stats.get_summary()
        return (
            f"📊 İstatistikler: "
            f"💬 {summary['total_comments']} yorum | "
            f"❤️ {summary['total_likes']} beğeni | "
            f"🎁 {summary['total_gifts']} hediye | "
            f"👥 {summary['current_viewers']} izleyici"
        )
    
    def _handle_top(self) -> str:
        """En aktif kullanıcılar komutunu işle"""
        top_commenters = self.stats.get_top_commenters(3)
        if not top_commenters:
            return "Henüz yorum yapan yok!"
        
        result = "🏆 En Aktif Kullanıcılar: "
        for i, (user, count) in enumerate(top_commenters, 1):
            result += f"{i}. {user} ({count}) "
        return result
    
    def _handle_gifts(self) -> str:
        """Hediye sıralaması komutunu işle"""
        top_gifters = self.stats.get_top_gifters(3)
        if not top_gifters:
            return "Henüz hediye gönderen yok!"
        
        result = "💝 En Çok Hediye Göndernler: "
        for i, (user, count, value) in enumerate(top_gifters, 1):
            result += f"{i}. {user} ({count} hediye) "
        return result
    
    def print_command_response(self, response: str, username: str):
        """Komut yanıtını renkli yazdır"""
        print(f"{Fore.CYAN}[KOMUT YANITI -> {username}]: {response}{Style.RESET_ALL}")
