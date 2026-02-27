@echo off
chcp 65001 > nul
echo TikTok Live Agent Kurulum Sihirbazı
echo.

REM Python kontrolü
echo Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadı. Lütfen Python 3.8 veya üzeri bir sürüm kurun.
    echo Python'ı indirmek için: https://www.python.org/downloads/
    echo.
    echo Kurulum sırasında "Add Python to PATH" seçeneğini işaretlediğinizden emin olun!
    pause
    exit /b
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i

echo Python %PYTHON_VERSION% bulundu.
echo.

REM pip kontrolü
echo pip (Python Paket Yöneticisi) kontrol ediliyor...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] pip bulunamadı. Python kurulumunuzda bir sorun olabilir.
    echo Lütfen Python'u yeniden kurmayı deneyin.
    pause
    exit /b
)

echo pip bulundu.
echo.

REM Sanal ortam oluşturma
echo Sanal ortam (venv) oluşturuluyor...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [HATA] Sanal ortam oluşturulamadı.
    pause
    exit /b
)

echo Sanal ortam oluşturuldu.
echo.

REM Sanal ortamı aktive et ve bağımlılıkları kur
echo Bağımlılıklar sanal ortama kuruluyor...
call .venv\Scripts\activate.bat
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [HATA] Bağımlılıklar kurulurken bir hata oluştu.
    echo Lütfen internet bağlantınızı kontrol edin ve tekrar deneyin.
    pause
    exit /b
)

echo.
echo =================================================================
echo                KURULUM BAŞARIYLA TAMAMLANDI!
echo =================================================================
echo.
echo Şimdi 'config.json' dosyasını düzenleyerek kendi ayarlarınızı yapabilirsiniz.
echo.
echo Ayarları yaptıktan sonra "calistir.bat" dosyasını çalıştırarak
echo ajanı başlatabilirsiniz.
echo.
pause
