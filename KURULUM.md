# 📚 TikTok Canlı Yayın Ajanı - Detaylı Kurulum Kılavuzu

## 📋 İçindekiler
1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Python Kurulumu](#python-kurulumu)
3. [Proje Kurulumu](#proje-kurulumu)
4. [Yapılandırma](#yapılandırma)
5. [İlk Çalıştırma](#ilk-çalıştırma)
6. [Özellikler](#özellikler)
7. [Komutlar](#komutlar)
8. [Sorun Giderme](#sorun-giderme)
9. [SSS](#sss)

---

## 🖥️ Sistem Gereksinimleri

### Minimum Gereksinimler:
- **İşletim Sistemi:** Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python:** 3.8 veya üzeri
- **RAM:** 2 GB (4 GB önerilir)
- **İnternet:** Stabil internet bağlantısı
- **Disk Alanı:** 100 MB boş alan

### Önerilen Gereksinimler:
- **Python:** 3.10 veya üzeri
- **RAM:** 4 GB veya üzeri
- **İnternet:** 5 Mbps veya daha hızlı

---

## 🐍 Python Kurulumu

### Windows için:

1. **Python İndirme:**
   - [Python.org](https://www.python.org/downloads/) adresine gidin
   - "Download Python 3.x.x" butonuna tıklayın
   - İndirilen dosyayı çalıştırın

2. **Kurulum:**
   - ✅ **ÖNEMLİ:** "Add Python to PATH" seçeneğini işaretleyin!
   - "Install Now" seçeneğine tıklayın
   - Kurulum tamamlanana kadar bekleyin

3. **Doğrulama:**
   ```cmd
   python --version
   ```
   Çıktı: `Python 3.x.x` görmelisiniz

### macOS için:

1. **Homebrew ile Kurulum:**
   ```bash
   # Homebrew kurulu değilse önce kurun
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Python'u kurun
   brew install python3
   ```

2. **Doğrulama:**
   ```bash
   python3 --version
   ```

### Linux (Ubuntu/Debian) için:

1. **Kurulum:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Doğrulama:**
   ```bash
   python3 --version
   pip3 --version
   ```

---

## 📦 Proje Kurulumu

### 🚀 Hızlı Kurulum (Windows için)

Komut istemiyle uğraşmak istemiyorsanız, bu yöntem tam size göre!

1.  **`install.bat` dosyasını çalıştırın:**
    -   Proje klasöründeki `install.bat` dosyasına çift tıklayın.
    -   Bu sihirbaz, Python'u kontrol edecek, gerekli tüm paketleri sizin için otomatik olarak kuracak ve sanal bir ortam oluşturacaktır.
    -   İşlem tamamlandığında bir tuşa basarak pencereyi kapatabilirsiniz.

2.  **Kurulum sonrası:**
    -   Kurulum tamamlandıktan sonra, `config.json` dosyasını düzenleyerek ajanı kendi isteğinize göre yapılandırın.
    -   Yapılandırmayı tamamladıktan sonra, ajanı başlatmak için **`calistir.bat`** dosyasına çift tıklamanız yeterlidir.

---

### 👨‍💻 Manuel Kurulum (macOS/Linux ve Gelişiriciler için)


### Adım 1: Proje Klasörüne Gidin

**Windows:**
```cmd
cd C:\Users\KULLANICI_ADINIZ\Desktop\tiktok-live-agent
```

**macOS/Linux:**
```bash
cd ~/Desktop/tiktok-live-agent
```

### Adım 2: Gerekli Paketleri Kurun

**Windows:**
```cmd
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
pip3 install -r requirements.txt
```

### Kurulacak Paketler:
- `TikTokLive` - TikTok canlı yayın API'si
- `colorama` - Renkli konsol çıktısı
- `python-dotenv` - Ortam değişkenleri yönetimi

### Kurulum Sorunları:

**Hata: "pip is not recognized"**
```cmd
python -m pip install -r requirements.txt
```

**Hata: "Permission denied"** (Linux/macOS)
```bash
pip3 install --user -r requirements.txt
```

**Hata: "SSL Certificate"**
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## ⚙️ Yapılandırma

### config.json Dosyası

Proje klasöründe `config.json` dosyası bulunmaktadır. Bu dosyayı düzenleyerek ajanı özelleştirebilirsiniz.

Ayrıca, ajanı çalıştırdıktan sonra **http://localhost:8080** adresine giderek **web kontrol panelinden** de ayarları kolayca yapabilirsiniz!

### 1. TikTok Kullanıcı Adını Ayarlama

```json
"tiktok": {
    "unique_id": "BURAYA_TIKTOK_KULLANICI_ADINIZI_YAZIN",
    "auto_reconnect": true
}
```

**Örnek:**
```json
"tiktok": {
    "unique_id": "creator01.72",
    "auto_reconnect": true
}
```

> 💡 **İpucu:** TikTok kullanıcı adı, profil URL'sindeki @ işaretinden sonraki kısımdır.
> Örnek: `https://www.tiktok.com/@creator01.72` → `creator01.72`

### 2. Özellikleri Açma/Kapama

```json
"features": {
    "welcome_users": true,        // Kullanıcıları karşılama
    "thank_followers": true,      // Takipçilere teşekkür
    "thank_sharers": true,        // Paylaşanlara teşekkür
    "track_statistics": true,     // İstatistik takibi
    "moderation": true,           // Moderasyon sistemi
    "commands": true,             // Komut sistemi
    "vip_recognition": true,      // VIP tanıma
    "poll_tracking": true,        // Anket takibi
    "question_tracking": true     // Soru takibi
}
```

> 🔧 Bir özelliği kapatmak için `true` yerine `false` yazın.

### 3. Mesajları Özelleştirme

```json
"messages": {
    "welcome": "Hoş geldin {nickname}! 🎉",
    "follow": "Teşekkürler {nickname}, takip ettiğin için! ❤️",
    "share": "{nickname} yayını paylaştı! Çok teşekkürler! 🔥"
}
```

> 📝 **Not:** `{nickname}` otomatik olarak kullanıcı adıyla değiştirilir.

### 4. Otomatik Yanıtları Ayarlama

```json
"responses": {
    "selam": "Aleyküm selam, {nickname}! Hoş geldin! 👋",
    "merhaba": "Merhaba {nickname}, nasılsın? 😊",
    "nasılsın": "İyiyim, teşekkürler! Sen nasılsın {nickname}? 💫"
}
```

Yeni yanıtlar ekleyebilirsiniz:
```json
"responses": {
    "selam": "Aleyküm selam, {nickname}! Hoş geldin! 👋",
    "naber": "İyidir {nickname}, senden naber? 😄",
    "güzel": "Teşekkürler {nickname}! 🌟"
}
```

### 5. Moderasyon Ayarları

```json
"moderation": {
    "enabled": true,              // Moderasyonu aç/kapat
    "spam_limit": 5,              // 10 saniyede max mesaj sayısı
    "spam_time_window": 10,       // Zaman penceresi (saniye)
    "bad_words": ["spam", "reklam"],  // Yasaklı kelimeler
    "auto_warn": true             // Otomatik uyarı
}
```

**Yasaklı Kelime Ekleme:**
```json
"bad_words": ["spam", "reklam", "link", "takip"]
```

### 6. Komutları Özelleştirme

```json
"commands": {
    "!komutlar": "Mevcut komutlar: !komutlar, !stats, !top, !hediye, !yardım",
    "!yardım": "Yardım için komutları görmek isterseniz !komutlar yazın."
}
```

Yeni komutlar ekleyebilirsiniz:
```json
"commands": {
    "!komutlar": "Mevcut komutlar: !komutlar, !stats, !top, !hediye",
    "!discord": "Discord sunucumuz: discord.gg/example",
    "!instagram": "Instagram: @example"
}
```

---

## 🚀 İlk Çalıştırma

### Adım 1: Yapılandırmayı Kontrol Edin

`config.json` dosyasında `unique_id` alanını kendi TikTok kullanıcı adınızla değiştirdiğinizden emin olun. Bu ayarı web kontrol panelinden de yapabilirsiniz.

### Adım 2: Ajanı Başlatın

**Windows (En Kolay Yöntem):**
- **`calistir.bat`** dosyasına çift tıklayın.

**Manuel (Windows):**
```cmd
python main.py
```

**macOS/Linux:**
```bash
python3 main.py
```

### Adım 3: Beklenen Çıktı

```
======================================================================
    ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗
    ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝
       ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝ 
       ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗ 
       ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗
       ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                    
    🤖 CANLI YAYIN AJANI - Gelişmiş Versiyon v2.0
======================================================================

✅ Kontrol Paneli http://localhost:8080 adresinde çalışıyor
======================================================================
🚀 TikTok Canlı Yayın Ajanı Başlatılıyor...
======================================================================
✅ Kullanıcı canlı yayında! Bağlanılıyor...

[01:23:45] [BAĞLANTI] @creator01.72 yayınına bağlanıldı! (Oda ID: 123456789)
```

### Adım 4: Ajanı Durdurmak

Ajanı durdurmak için:
- **`calistir.bat`** penceresini kapatın veya `Ctrl + C` tuşlarına basın.
- **Manuel:** `Ctrl + C` tuşlarına basın.

---

## ✨ Özellikler

### 1. 👋 İzleyici Karşılama Sistemi
- Yayına katılan her kullanıcıyı otomatik karşılar
- Özelleştirilebilir karşılama mesajları
- VIP kullanıcılar için özel mesajlar

### 2. 💬 Akıllı Yorum Sistemi
- Anahtar kelimelere otomatik yanıt
- Çoklu dil desteği
- Kişiselleştirilmiş mesajlar

### 3. 🎁 Gelişmiş Hediye Yönetimi
- Hediye streak takibi
- Hediye değeri hesaplama
- Hediye sıralaması
- Özel teşekkür mesajları

### 4. 📊 İstatistik ve Analitik
- Gerçek zamanlı izleyici sayısı
- Toplam yorum/beğeni/hediye
- En aktif kullanıcılar
- Yayın sonu raporu
- JSON formatında kayıt

### 5. 🛡️ Moderasyon Sistemi
- Spam algılama ve engelleme
- Kötü kelime filtresi
- Otomatik uyarı sistemi
- Silinen mesaj takibi

### 6. 🤖 Komut Sistemi
- `!stats` - İstatistikleri göster
- `!top` - En aktif kullanıcılar
- `!hediye` - Hediye sıralaması
- `!komutlar` - Tüm komutları listele
- Özel komutlar eklenebilir

### 7. 👑 VIP Kullanıcı Tanıma
- VIP izleyicileri otomatik algılama
- Özel karşılama mesajları
- Top 3 hediye gönderenleri takip

### 8. 🎨 Renkli Konsol Çıktısı
- Olay türüne göre renklendirme
- Emoji desteği
- Zaman damgası
- Okunabilir format

---

## 🎮 Komutlar

### Kullanıcı Komutları

Yayın izleyicileri chat'e şu komutları yazabilir:

| Komut | Açıklama | Örnek Çıktı |
|-------|----------|-------------|
| `!stats` | Yayın istatistiklerini gösterir | 📊 İstatistikler: 💬 45 yorum \| ❤️ 230 beğeni \| 🎁 12 hediye \| 👥 156 izleyici |
| `!top` | En aktif 3 kullanıcıyı gösterir | 🏆 En Aktif Kullanıcılar: 1. Ali (15) 2. Ayşe (12) 3. Mehmet (8) |
| `!hediye` | En çok hediye gönderen 3 kişiyi gösterir | 💝 En Çok Hediye Göndernler: 1. Ali (25 hediye) 2. Ayşe (18 hediye) |
| `!komutlar` | Tüm komutları listeler | Mevcut komutlar: !komutlar, !stats, !top, !hediye, !yardım |
| `!yardım` | Yardım mesajı gösterir | Yardım için komutları görmek isterseniz !komutlar yazın. |

### Yeni Komut Ekleme

`config.json` dosyasına yeni komutlar ekleyebilirsiniz:

```json
"commands": {
    "!discord": "Discord sunucumuz: discord.gg/example",
    "!instagram": "Instagram: @example",
    "!youtube": "YouTube: youtube.com/@example",
    "!bağış": "Bağış için: patreon.com/example"
}
```

---

## 🔧 Sorun Giderme

### Sorun 1: "Kullanıcı canlı yayında değil" Hatası

**Çözüm:**
1. TikTok kullanıcı adının doğru olduğundan emin olun
2. Kullanıcının gerçekten canlı yayında olduğunu kontrol edin
3. `config.json` dosyasında `unique_id` alanını kontrol edin

### Sorun 2: "ModuleNotFoundError: No module named 'TikTokLive'"

**Çözüm:**
```cmd
pip install TikTokLive --upgrade
```

### Sorun 3: "ModuleNotFoundError: No module named 'colorama'"

**Çözüm:**
```cmd
pip install colorama
```

### Sorun 4: Renkli Çıktı Görünmüyor

**Çözüm:**
1. Windows'ta: Windows Terminal veya PowerShell kullanın (CMD yerine)
2. `config.json` dosyasında `colored_output` ayarını kontrol edin:
```json
"display": {
    "colored_output": true
}
```

### Sorun 5: "config.json dosyası bulunamadı"

**Çözüm:**
1. `config.json` dosyasının `main.py` ile aynı klasörde olduğundan emin olun
2. Dosya adının tam olarak `config.json` olduğunu kontrol edin (büyük/küçük harf duyarlı)

### Sorun 6: Bağlantı Hataları

**Çözüm:**
1. İnternet bağlantınızı kontrol edin
2. Firewall/Antivirus ayarlarını kontrol edin
3. VPN kullanıyorsanız kapatmayı deneyin
4. Birkaç dakika bekleyip tekrar deneyin

### Sorun 7: "JSONDecodeError"

**Çözüm:**
1. `config.json` dosyasının geçerli JSON formatında olduğundan emin olun
2. Virgül, tırnak işaretleri ve parantezleri kontrol edin
3. [JSONLint](https://jsonlint.com/) ile dosyayı doğrulayın

### Sorun 8: İstatistikler Kaydedilmiyor

**Çözüm:**
1. Yazma izinlerinizi kontrol edin
2. `config.json` dosyasında ayarı kontrol edin:
```json
"statistics": {
    "save_to_file": true
}
```

---

## ❓ SSS (Sık Sorulan Sorular)

### S1: Ajan kendi yayınımda çalışır mı?
**C:** Evet! Kendi TikTok kullanıcı adınızı `config.json` dosyasına yazarak kendi yayınınızda kullanabilirsiniz.

### S2: Birden fazla yayını aynı anda takip edebilir miyim?
**C:** Hayır, bir ajan bir yayını takip eder. Birden fazla yayın için birden fazla ajan çalıştırmanız gerekir.

### S3: Ajan otomatik olarak yorum yazabilir mi?
**C:** Hayır, bu versiyon sadece yayını dinler ve konsola çıktı verir. Yorum yazma özelliği TikTok'un kurallarına aykırı olabilir.

### S4: İstatistikler nereye kaydediliyor?
**C:** İstatistikler, ajan klasöründe `stats_TARIH_SAAT.json` formatında kaydedilir.

### S5: Moderasyon otomatik olarak kullanıcıları engelliyor mu?
**C:** Hayır, moderasyon sadece spam ve kötü kelimeleri tespit eder ve konsola bildirir. Engelleme yapmaz.

### S6: Hangi TikTok hesaplarında çalışır?
**C:** Tüm açık (public) TikTok hesaplarında çalışır. Özel (private) hesaplarda çalışmaz.

### S7: Ajan ne kadar kaynak kullanır?
**C:** Çok az! Ortalama 50-100 MB RAM ve minimal CPU kullanır.

### S8: Mobil cihazda çalışır mı?
**C:** Hayır, Python ve masaüstü ortamı gerektirir. Windows, macOS veya Linux gereklidir.

### S9: Ajanı arka planda çalıştırabilir miyim?
**C:** Evet! 
- **Windows:** `pythonw main.py` komutu ile
- **Linux/macOS:** `nohup python3 main.py &` komutu ile

### S10: Güvenli mi?
**C:** Evet! Ajan sadece herkese açık yayın verilerini okur. Hiçbir şifre veya kişisel bilgi gerektirmez.

---

## 📞 Destek

### Sorun Bildirme
Bir hata bulduysanız veya öneriniz varsa:
1. Hata mesajını kaydedin
2. `config.json` dosyanızı kontrol edin
3. Sorun giderme bölümünü inceleyin

### Güncellemeler
Yeni özellikler ve hata düzeltmeleri için projeyi düzenli olarak güncelleyin:
```cmd
pip install TikTokLive --upgrade
```

---

## 📝 Notlar

### Önemli Uyarılar:
- ⚠️ TikTok'un kullanım şartlarına uygun kullanın
- ⚠️ Spam yapmayın
- ⚠️ Başkalarının gizliliğine saygı gösterin
- ⚠️ Ajanı kötüye kullanmayın

### İpuçları:
- 💡 İlk kez kullanıyorsanız tüm özellikleri açık bırakın
- 💡 Moderasyon ayarlarını yayınınıza göre özelleştirin
- 💡 İstatistikleri düzenli olarak kontrol edin
- 💡 Özel mesajlar ekleyerek ajanı kişiselleştirin

---

## 🎉 Başarılar!

Artık TikTok Canlı Yayın Ajanınız kullanıma hazır! İyi yayınlar! 🚀

---

**Versiyon:** 2.0  
**Son Güncelleme:** 2026  
**Lisans:** MIT
