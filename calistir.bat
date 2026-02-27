@echo off
chcp 65001 > nul
echo TikTok Live Agent Başlatılıyor...
echo.

REM Sanal ortamın varlığını kontrol et
if not exist .venv\ (
    echo [HATA] Sanal ortam bulunamadı.
    echo Lütfen önce "install.bat" dosyasını çalıştırarak kurulumu tamamlayın.
    pause
    exit /b
)

REM Sanal ortamı aktive et
call .venv\Scripts\activate.bat

REM Ana betiği çalıştır
echo Kontrol Paneli: http://localhost:8080
python main.py

echo.
echo Ajan durduruldu. Kapatmak için bir tuşa basın.
pause
