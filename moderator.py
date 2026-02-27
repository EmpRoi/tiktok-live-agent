"""
TikTok Live Agent - Moderasyon Modülü
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Set


class Moderator:
    """Yayın moderasyonunu yöneten sınıf"""
    
    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.spam_limit = config.get("spam_limit", 5)
        self.spam_time_window = config.get("spam_time_window", 10)
        self.bad_words = set(word.lower() for word in config.get("bad_words", []))
        self.auto_warn = config.get("auto_warn", True)
        
        # Kullanıcı mesaj geçmişi
        self.user_messages: Dict[str, List[datetime]] = defaultdict(list)
        self.warned_users: Set[str] = set()
        self.spam_detected: Dict[str, int] = defaultdict(int)
        
    def check_spam(self, username: str) -> bool:
        """Spam kontrolü yap"""
        if not self.enabled:
            return False
            
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=self.spam_time_window)
        
        # Eski mesajları temizle
        self.user_messages[username] = [
            msg_time for msg_time in self.user_messages[username]
            if msg_time > cutoff_time
        ]
        
        # Yeni mesajı ekle
        self.user_messages[username].append(now)
        
        # Spam kontrolü
        if len(self.user_messages[username]) > self.spam_limit:
            self.spam_detected[username] += 1
            return True
            
        return False
    
    def check_bad_words(self, message: str) -> bool:
        """Kötü kelime kontrolü yap"""
        if not self.enabled or not self.bad_words:
            return False
            
        message_lower = message.lower()
        return any(bad_word in message_lower for bad_word in self.bad_words)
    
    def should_warn(self, username: str) -> bool:
        """Kullanıcıya uyarı verilmeli mi?"""
        if not self.auto_warn:
            return False
            
        if username not in self.warned_users:
            self.warned_users.add(username)
            return True
            
        return False
    
    def get_spam_count(self, username: str) -> int:
        """Kullanıcının spam sayısını getir"""
        return self.spam_detected.get(username, 0)
    
    def reset_user(self, username: str):
        """Kullanıcı verilerini sıfırla"""
        if username in self.user_messages:
            del self.user_messages[username]
        if username in self.warned_users:
            self.warned_users.remove(username)
        if username in self.spam_detected:
            del self.spam_detected[username]
    
    def get_statistics(self) -> dict:
        """Moderasyon istatistiklerini getir"""
        return {
            "total_warned": len(self.warned_users),
            "total_spam_detected": sum(self.spam_detected.values()),
            "active_users": len(self.user_messages)
        }
