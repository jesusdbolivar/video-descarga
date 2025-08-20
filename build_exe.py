# build_exe.py
import PyInstaller.__main__
import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import tempfile

def get_yt_dlp_location():
    """Encuentra la ubicación de yt-dlp"""
    try:
        # Buscar en el entorno virtual
        venv_path = os.path.join(os.getcwd(), ".venv", "Scripts", "yt-dlp.exe")
        if os.path.exists(venv_path):
            return venv_path
        
        # Buscar en el sistema
        result = subprocess.run(['where', 'yt-dlp'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
        
        # Alternativo con which en sistemas Unix-like
        result = subprocess.run(['which', 'yt-dlp'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

def download_ffmpeg():
    """Descarga FFmpeg desde la fuente oficial"""
    print("🔽 Descargando FFmpeg...")
    
    # URL de FFmpeg para Windows (versión estática)
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "ffmpeg.zip")
    
    try:
        # Descargar FFmpeg
        print("📥 Descargando desde GitHub...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        # Extraer el archivo ZIP
        print("📦 Extrayendo FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Buscar el ejecutable ffmpeg.exe
        ffmpeg_exe = None
        for root, dirs, files in os.walk(temp_dir):
            if 'ffmpeg.exe' in files:
                ffmpeg_exe = os.path.join(root, 'ffmpeg.exe')
                break
        
        if ffmpeg_exe and os.path.exists(ffmpeg_exe):
            print(f"✅ FFmpeg encontrado: {ffmpeg_exe}")
            return ffmpeg_exe
        else:
            print("❌ ERROR: No se encontró ffmpeg.exe en el archivo descargado")
            return None
            
    except Exception as e:
        print(f"❌ ERROR descargando FFmpeg: {e}")
        return None
    finally:
        # Limpiar archivos temporales
        try:
            os.remove(zip_path)
        except:
            pass

def get_or_download_ffmpeg():
    """Obtiene FFmpeg, descargándolo si es necesario"""
    # Primero intentar encontrar FFmpeg instalado
    try:
        result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            ffmpeg_path = result.stdout.strip().split('\n')[0]
            print(f"✅ FFmpeg encontrado en el sistema: {ffmpeg_path}")
            return ffmpeg_path
    except:
        pass
    
    # Si no está instalado, descargarlo
    print("⚠️ FFmpeg no encontrado en el sistema, descargando...")
    return download_ffmpeg()

def build_executable():
    """Construye el ejecutable con todas las dependencias"""
    print("🔨 Iniciando construcción del ejecutable...")
    
    # Verificar que yt-dlp esté disponible
    yt_dlp_path = get_yt_dlp_location()
    if not yt_dlp_path:
        print("❌ ERROR: yt-dlp no encontrado. Instalando...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
            yt_dlp_path = get_yt_dlp_location()
        except:
            print("❌ Error instalando yt-dlp")
            return False
    
    print(f"✅ yt-dlp encontrado en: {yt_dlp_path}")
    
    # Obtener FFmpeg
    ffmpeg_path = get_or_download_ffmpeg()
    if not ffmpeg_path:
        print("❌ ERROR: No se pudo obtener FFmpeg")
        return False
    
    print(f"✅ FFmpeg disponible: {ffmpeg_path}")
    
    # Crear directorio de datos adicionales
    data_dir = "additional_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Copiar yt-dlp al directorio de datos
    if yt_dlp_path:
        yt_dlp_dest = os.path.join(data_dir, "yt-dlp.exe")
        shutil.copy2(yt_dlp_path, yt_dlp_dest)
        print(f"✅ yt-dlp copiado a {yt_dlp_dest}")
    
    # Copiar FFmpeg al directorio de datos
    if ffmpeg_path:
        ffmpeg_dest = os.path.join(data_dir, "ffmpeg.exe")
        shutil.copy2(ffmpeg_path, ffmpeg_dest)
        print(f"✅ FFmpeg copiado a {ffmpeg_dest}")
    
    # Preparar argumentos para PyInstaller
    yt_dlp_full_path = os.path.abspath(os.path.join(data_dir, "yt-dlp.exe"))
    ffmpeg_full_path = os.path.abspath(os.path.join(data_dir, "ffmpeg.exe"))
    args = [
        '--name=VideoDescarga',
        '--windowed',  # No mostrar consola
        '--onefile',   # Un solo archivo ejecutable
        '--icon=NONE', # Sin icono por ahora
        '--distpath=./dist',
        '--workpath=./build',
        '--specpath=./build',
        '--clean',
        '--noconfirm',
        # Incluir módulos necesarios
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=subprocess',
        '--hidden-import=shutil',
        '--hidden-import=os',
        '--hidden-import=sys',
        '--hidden-import=re',
        # Incluir datos adicionales (yt-dlp y ffmpeg)
        f'--add-data={yt_dlp_full_path}{os.pathsep}.',
        f'--add-data={ffmpeg_full_path}{os.pathsep}.',
        # Opciones de Windows
        '--noupx',
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        # Archivo principal
        'video_descarga.py'
    ]
    
    try:
        print("🔧 Ejecutando PyInstaller...")
        PyInstaller.__main__.run(args)
        
        # Verificar que el ejecutable se creó
        exe_path = "./dist/VideoDescarga.exe"
        if os.path.exists(exe_path):
            print(f"✅ Ejecutable creado exitosamente: {exe_path}")
            print(f"📁 Tamaño: {os.path.getsize(exe_path) / 1024 / 1024:.1f} MB")
            
            # Crear directorio de downloads junto al ejecutable
            downloads_dir = "./dist/downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            print(f"✅ Directorio de descargas creado: {downloads_dir}")
            
            return True
        else:
            print("❌ ERROR: El ejecutable no se creó")
            return False
            
    except Exception as e:
        print(f"❌ ERROR durante la construcción: {e}")
        return False

def cleanup_temp_files():
    """Limpia archivos temporales"""
    temp_dirs = ['build', 'additional_data']
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"🗑️ Directorio temporal eliminado: {temp_dir}")
            except:
                print(f"⚠️ No se pudo eliminar: {temp_dir}")
    
    # Limpiar archivos temporales de FFmpeg si existen
    temp_files = ['ffmpeg.zip', 'ffmpeg_temp']
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            try:
                if os.path.isdir(temp_file):
                    shutil.rmtree(temp_file)
                else:
                    os.remove(temp_file)
                print(f"🗑️ Archivo temporal eliminado: {temp_file}")
            except:
                print(f"⚠️ No se pudo eliminar: {temp_file}")

if __name__ == "__main__":
    print("🚀 Video Descarga - Constructor de Ejecutable")
    print("=" * 50)
    
    success = build_executable()
    
    if success:
        print("\n✅ ¡Construcción completada exitosamente!")
        print("📦 El ejecutable está en: ./dist/VideoDescarga.exe")
        print("💡 Puedes distribuir el archivo .exe sin necesidad de instalar Python")
        
        # Preguntar sobre limpieza
        response = input("\n🗑️ ¿Eliminar archivos temporales? (s/n): ").lower().strip()
        if response in ['s', 'si', 'y', 'yes']:
            cleanup_temp_files()
    else:
        print("\n❌ La construcción falló")
        cleanup_temp_files()
    
    print("\n🏁 Proceso terminado")
