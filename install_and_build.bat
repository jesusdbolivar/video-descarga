@echo off
echo ======================================
echo Video Descarga - Instalador y Constructor
echo ======================================

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor, instala Python desde https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Crear entorno virtual si no existe
if not exist ".venv" (
    echo 📦 Creando entorno virtual...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual encontrado
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Actualizar pip
echo 📦 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas

REM Construir ejecutable
echo 🔨 Construyendo ejecutable...
python build_exe.py
if %errorlevel% neq 0 (
    echo ❌ Error construyendo ejecutable
    pause
    exit /b 1
)

echo ✅ ¡Construcción completada!
echo 📦 El ejecutable está en: dist\VideoDescarga.exe
echo 💡 Puedes distribuir este archivo sin necesidad de instalar Python ni FFmpeg

echo.
echo Presiona cualquier tecla para salir...
pause >nul
