@echo off
echo ======================================
echo Video Descarga - Empaquetador para Distribución
echo ======================================

REM Verificar que el ejecutable existe
if not exist "dist\VideoDescarga.exe" (
    echo ❌ ERROR: El ejecutable no existe
    echo Ejecuta primero: install_and_build.bat
    pause
    exit /b 1
)

echo ✅ Ejecutable encontrado

REM Crear directorio de distribución
set DIST_DIR=VideoDescarga_Portable
if exist "%DIST_DIR%" (
    echo 🗑️ Eliminando directorio anterior...
    rmdir /s /q "%DIST_DIR%"
)

echo 📦 Creando paquete de distribución...
mkdir "%DIST_DIR%"

REM Copiar ejecutable
copy "dist\VideoDescarga.exe" "%DIST_DIR%\"
echo ✅ Ejecutable copiado

REM Crear directorio de descargas
mkdir "%DIST_DIR%\downloads"
echo ✅ Directorio de descargas creado

REM Crear archivo README para el usuario final
echo Creando README para usuario final...
(
echo # Video Descarga - Aplicación Portable
echo.
echo ## Instrucciones de Uso
echo.
echo 1. Ejecuta VideoDescarga.exe
echo 2. Pega las URLs de los videos que quieres descargar
echo 3. Configura el formato y calidad deseados
echo 4. Haz clic en "Iniciar Descarga"
echo.
echo ## Características
echo.
echo - ✅ No requiere instalación adicional
echo - ✅ FFmpeg incluido automáticamente
echo - ✅ Soporte para múltiples formatos
echo - ✅ Descarga desde YouTube, Vimeo, y más de 1000 sitios
echo.
echo ## Formatos de URL Soportados
echo.
echo ```
echo # URL simple
echo https://youtube.com/watch?v=video_id
echo.
echo # URL con referer ^(para sitios protegidos^)
echo https://video-url.com/video:https://referer-page.com
echo.
echo # Múltiples URLs
echo https://url1.com, https://url2.com:https://referer.com
echo ```
echo.
echo ## Solución de Problemas
echo.
echo - Si Windows Defender bloquea el archivo, agregarlo a excepciones
echo - Para sitios protegidos, usar el formato URL:REFERER
echo - Los videos se guardan en la carpeta "downloads"
echo.
echo ## Nota Legal
echo.
echo Respeta los términos de servicio de los sitios web y las leyes de derechos de autor.
) > "%DIST_DIR%\README.txt"

echo ✅ README creado

REM Crear script de ejemplo
(
echo @echo off
echo echo Ejecutando Video Descarga...
echo start VideoDescarga.exe
) > "%DIST_DIR%\Ejecutar.bat"

echo ✅ Script de ejecución creado

REM Mostrar información del paquete
echo.
echo ==========================================
echo ✅ ¡Paquete de distribución creado!
echo ==========================================
echo 📁 Directorio: %DIST_DIR%
echo 📦 Contenido:
dir "%DIST_DIR%" /b
echo.

REM Calcular tamaño total
for /f "tokens=3" %%a in ('dir "%DIST_DIR%" /s ^| find "bytes"') do set size=%%a
echo 📊 Tamaño total: %size% bytes

echo.
echo 💡 Puedes comprimir la carpeta "%DIST_DIR%" y distribuirla
echo 🚀 El usuario final solo necesita extraer y ejecutar VideoDescarga.exe

echo.
echo Presiona cualquier tecla para salir...
pause >nul
