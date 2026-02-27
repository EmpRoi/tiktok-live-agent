# Plan: TTS Bug Fix & Panel Ayarları Genişletme

## 1. Bug: TTS İlk Yorumdan Sonra Sessiz Kalıyor

### Sorunun Kök Nedeni
`speech.py` dosyasındaki `_speech_worker()` metodu her yorum için:
1. `pyttsx3.init()` ile yeni bir motor oluşturuyor (satır 68)
2. `engine.runAndWait()` çalıştırıyor (satır 90)
3. `engine.stop()` çağırıyor (satır 91)

Windows'ta `pyttsx3` COM tabanlı çalışır. Her seferinde yeni motor oluşturup yok etmek, COM nesnelerinin düzgün temizlenmemesine ve sonraki çağrıların sessizce başarısız olmasına neden olur.

### Çözüm
- Motor bir kez oluşturulacak ve thread boyunca yeniden kullanılacak
- `engine.stop()` kaldırılacak (runAndWait zaten motoru durdurur)
- Hata durumunda motor yeniden başlatılacak (fallback mekanizması)

```python
def _speech_worker(self):
    engine = pyttsx3.init()
    # Ses ayarlarını bir kez yap
    engine.setProperty('rate', self.rate)
    engine.setProperty('volume', self.volume)
    # Ses seçimi bir kez yap
    ...
    
    while not self.stop_speaking:
        try:
            text = self.speech_queue.get(timeout=1)
            if text is None:
                break
            self.speaking = True
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                # Motor bozulduysa yeniden başlat
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', self.rate)
                    engine.setProperty('volume', self.volume)
                except:
                    pass
            self.speaking = False
            self.speech_queue.task_done()
        except queue.Empty:
            continue
    
    engine.stop()
```

---

## 2. Panel Ayarları Genişletme

### Mevcut Durum
Panel şu anda sadece şu bölümleri içeriyor:
- Genel Ayarlar: unique_id, colored_output
- Özellikler: features toggle'ları
- Seslendirme: enabled, language, language_code, rate, volume
- Moderasyon: enabled, spam_limit, spam_time_window, auto_warn, bad_words
- Mesajlar: welcome, follow, share, gift_small/medium/large
- Otomatik Yanıtlar: responses tablosu
- Özel Komutlar: commands tablosu

### Eklenecek Bölümler

#### 2.1 TTS Olay Ayarları
`speech.events` altındaki her olay için toggle eklenecek:
- comment, gift, follow, join, like, share

#### 2.2 Commenter - Yorum Botu Ayarları
Yeni bölüm:
- enabled: checkbox
- username: text input
- password: password input
- headless: checkbox
- comment_delay: number input
- auto_reply: checkbox

#### 2.3 Auto Responses Tablosu
`auto_responses` config bölümü için dinamik tablo (responses ve commands gibi)

#### 2.4 İstatistik Ayarları
- save_to_file: checkbox
- show_summary: checkbox
- track_top_users: number input

#### 2.5 Display Ayarları Tamamlama
- show_emojis: checkbox
- show_timestamps: checkbox

#### 2.6 Genel Ayarlar Genişletme
- auto_reconnect: checkbox
- check_interval: number input (saniye)

#### 2.7 Mesaj Şablonları Tamamlama
- vip_join: text input
- top_gifter: text input

### Panel UI Yapısı

```
┌─────────────────────────────────────────┐
│ TikTok Live Agent Kontrol Paneli        │
├─────────────────────────────────────────┤
│ Genel Ayarlar                           │
│  - TikTok Kullanıcı Adı                │
│  - Otomatik Yeniden Bağlan              │
│  - Kontrol Aralığı                      │
├─────────────────────────────────────────┤
│ Özellikler                              │
│  - [toggle'lar]                         │
├─────────────────────────────────────────┤
│ Görünüm Ayarları                        │
│  - Renkli Çıktı                         │
│  - Emoji Göster                         │
│  - Zaman Damgası Göster                 │
├─────────────────────────────────────────┤
│ Seslendirme - TTS                       │
│  - Aktif/Pasif                          │
│  - Dil, Dil Kodu, Hız, Ses Seviyesi    │
│  - Olay Ayarları: yorum, hediye, takip  │
│    katılım, beğeni, paylaşım            │
├─────────────────────────────────────────┤
│ Yorum Botu                              │
│  - Aktif/Pasif                          │
│  - Kullanıcı Adı, Şifre                │
│  - Headless, Gecikme, Otomatik Yanıt   │
├─────────────────────────────────────────┤
│ Moderasyon                              │
│  - [mevcut ayarlar]                     │
├─────────────────────────────────────────┤
│ İstatistik Ayarları                     │
│  - Dosyaya Kaydet                       │
│  - Özet Göster                          │
│  - Top Kullanıcı Sayısı                │
├─────────────────────────────────────────┤
│ Mesajlar                                │
│  - [mevcut + vip_join, top_gifter]      │
├─────────────────────────────────────────┤
│ Otomatik Yanıtlar (responses)           │
│ Otomatik Bot Yanıtları (auto_responses) │
│ Özel Komutlar (commands)                │
│ Özel Bot Komutları (custom_responses)   │
├─────────────────────────────────────────┤
│ [Tüm Ayarları Kaydet]                   │
└─────────────────────────────────────────┘
```

---

## Değiştirilecek Dosyalar

| Dosya | Değişiklik |
|-------|-----------|
| `speech.py` | pyttsx3 motor yönetimi düzeltmesi |
| `panel/index.html` | Tüm yeni panel bölümleri ve form alanları |

## Değiştirilmeyecek Dosyalar
- `main.py` - Değişiklik gerektirmiyor
- `config.json` - Mevcut yapı yeterli, panel zaten config'i okuyup yazıyor
- `panel.py` - Backend zaten recursive_update ile tüm config değişikliklerini destekliyor
- `commenter.py`, `moderator.py`, `commands.py`, `statistics.py` - Değişiklik gerektirmiyor
