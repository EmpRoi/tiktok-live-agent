"""
TikTok Live Agent - İstatistik Yönetimi Modülü
"""
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any


class Statistics:
    """Yayın istatistiklerini yöneten sınıf"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.total_comments = 0
        self.total_likes = 0
        self.total_gifts = 0
        self.total_gift_value = 0
        self.total_joins = 0
        self.total_follows = 0
        self.total_shares = 0
        self.peak_viewers = 0
        self.current_viewers = 0
        
        # Kullanıcı bazlı istatistikler
        self.user_comments: Dict[str, int] = defaultdict(int)
        self.user_likes: Dict[str, int] = defaultdict(int)
        self.user_gifts: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "value": 0})
        self.vip_users: List[str] = []
        self.top_gifters: List[Dict[str, Any]] = []
        
        # Hediye detayları
        self.gift_details: List[Dict[str, Any]] = []
        
    def add_comment(self, username: str):
        """Yorum ekle"""
        self.total_comments += 1
        self.user_comments[username] += 1
        
    def add_like(self, username: str, count: int = 1):
        """Beğeni ekle"""
        self.total_likes += count
        self.user_likes[username] += count
        
    def add_gift(self, username: str, gift_name: str, count: int, value: int = 0):
        """Hediye ekle"""
        self.total_gifts += count
        self.total_gift_value += value * count
        self.user_gifts[username]["count"] += count
        self.user_gifts[username]["value"] += value * count
        
        self.gift_details.append({
            "username": username,
            "gift_name": gift_name,
            "count": count,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_join(self):
        """Katılım ekle"""
        self.total_joins += 1
        
    def add_follow(self):
        """Takip ekle"""
        self.total_follows += 1
        
    def add_share(self):
        """Paylaşım ekle"""
        self.total_shares += 1
        
    def update_viewers(self, count: int):
        """İzleyici sayısını güncelle"""
        self.current_viewers = count
        if count > self.peak_viewers:
            self.peak_viewers = count
            
    def add_vip_user(self, username: str):
        """VIP kullanıcı ekle"""
        if username not in self.vip_users:
            self.vip_users.append(username)
            
    def get_top_commenters(self, limit: int = 10) -> List[tuple]:
        """En çok yorum yapanları getir"""
        return sorted(self.user_comments.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_top_gifters(self, limit: int = 10) -> List[tuple]:
        """En çok hediye gönderenleri getir"""
        return sorted(
            [(user, data["count"], data["value"]) for user, data in self.user_gifts.items()],
            key=lambda x: x[2],
            reverse=True
        )[:limit]
    
    def get_duration(self) -> str:
        """Yayın süresini getir"""
        duration = datetime.now() - self.start_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_summary(self) -> Dict[str, Any]:
        """Özet istatistikleri getir"""
        return {
            "duration": self.get_duration(),
            "total_comments": self.total_comments,
            "total_likes": self.total_likes,
            "total_gifts": self.total_gifts,
            "total_gift_value": self.total_gift_value,
            "total_joins": self.total_joins,
            "total_follows": self.total_follows,
            "total_shares": self.total_shares,
            "peak_viewers": self.peak_viewers,
            "current_viewers": self.current_viewers,
            "top_commenters": self.get_top_commenters(5),
            "top_gifters": self.get_top_gifters(5),
            "vip_count": len(self.vip_users)
        }
    
    def save_to_file(self, filename: str = None):
        """İstatistikleri dosyaya kaydet"""
        if filename is None:
            filename = f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        data = {
            "summary": self.get_summary(),
            "detailed_stats": {
                "all_commenters": dict(self.user_comments),
                "all_gifters": {user: data for user, data in self.user_gifts.items()},
                "gift_details": self.gift_details,
                "vip_users": self.vip_users
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return filename
    
    def print_summary(self):
        """Özet istatistikleri yazdır"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 YAYIN İSTATİSTİKLERİ")
        print("="*60)
        print(f"⏱️  Süre: {summary['duration']}")
        print(f"👥 Toplam Katılım: {summary['total_joins']}")
        print(f"👀 En Yüksek İzleyici: {summary['peak_viewers']}")
        print(f"💬 Toplam Yorum: {summary['total_comments']}")
        print(f"❤️  Toplam Beğeni: {summary['total_likes']}")
        print(f"🎁 Toplam Hediye: {summary['total_gifts']}")
        print(f"💎 Hediye Değeri: {summary['total_gift_value']}")
        print(f"➕ Yeni Takipçi: {summary['total_follows']}")
        print(f"🔄 Paylaşım: {summary['total_shares']}")
        print(f"👑 VIP Kullanıcı: {summary['vip_count']}")
        
        if summary['top_commenters']:
            print("\n🏆 EN AKTİF YORUMCULAR:")
            for i, (user, count) in enumerate(summary['top_commenters'], 1):
                print(f"   {i}. {user}: {count} yorum")
                
        if summary['top_gifters']:
            print("\n💝 EN ÇOK HEDİYE GÖNDERNLER:")
            for i, (user, count, value) in enumerate(summary['top_gifters'], 1):
                print(f"   {i}. {user}: {count} hediye (Değer: {value})")
                
        print("="*60 + "\n")
