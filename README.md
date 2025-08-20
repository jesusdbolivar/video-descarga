# Video Descarga

Una aplicación de escritorio con interfaz gráfica para descargar videos usando yt-dlp, con FFmpeg integrado para conversión y procesamiento de videos.

## Características

- ✅ **Interfaz gráfica intuitiva** con PyQt5
- ✅ **FFmpeg incluido automáticamente** en el ejecutable
- ✅ **Soporte para múltiples formatos** (MP4, WebM, MKV, AVI)
- ✅ **Descarga de subtítulos** automática
- ✅ **Extracción de audio** a MP3
- ✅ **Soporte para referers** y páginas protegidas
- ✅ **Progreso en tiempo real** de las descargas
- ✅ **Executable autónomo** - no requiere instalaciones adicionales

## Instalación Rápida

### Opción 1: Usar el script automático (Recomendado)

1. Clona o descarga este repositorio
2. Ejecuta `install_and_build.bat`
3. ¡Listo! El ejecutable estará en `dist/VideoDescarga.exe`

### Opción 2: Instalación manual

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual
.venv\Scripts\activate  # Windows
# source .venv/Scripts/activate  # Git Bash/Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Construir ejecutable
python build_exe.py
```

## Características del Ejecutable

El ejecutable generado incluye:

- ✅ **yt-dlp** - Para descargar videos de múltiples plataformas
- ✅ **FFmpeg** - Descargado automáticamente para conversión de videos
- ✅ **Todas las dependencias de Python** - PyQt5, etc.
- ✅ **Completamente portable** - Un solo archivo .exe

### FFmpeg Integrado

El script de construcción:
1. Detecta si FFmpeg está instalado en el sistema
2. Si no está instalado, descarga automáticamente la versión más reciente desde GitHub
3. Incluye FFmpeg dentro del ejecutable final
4. Configura yt-dlp para usar el FFmpeg integrado

## Uso

### Desde el ejecutable
1. Ejecuta `VideoDescarga.exe`
2. Pega las URLs de los videos que quieres descargar
3. Configura el formato y calidad deseados
4. Haz clic en "Iniciar Descarga"

### Formatos de URL soportados

```
# URL simple
https://youtube.com/watch?v=video_id

# URL con referer (para sitios protegidos)
https://video-url.com/video:https://referer-page.com

# Múltiples URLs
https://url1.com, https://url2.com:https://referer.com, https://url3.com
```

### Funciones Principales

- **Formato**: MP4, WebM, MKV, AVI, o automático
- **Calidad**: Desde 360p hasta la mejor calidad disponible
- **Audio**: Extracción de audio a MP3
- **Subtítulos**: Descarga automática si están disponibles
- **Playlists**: Opción para descargar solo el video individual

## Plataformas Soportadas

Gracias a yt-dlp, soporta más de 1000 sitios web, incluyendo:

- YouTube
- Vimeo
- Facebook
- Instagram
- TikTok
- Twitter
- Y muchos más...

## Desarrollo

### Estructura del Proyecto

```
video-descarga/
├── video_descarga.py      # Aplicación principal
├── build_exe.py           # Script de construcción
├── requirements.txt       # Dependencias Python
├── install_and_build.bat  # Script de instalación automática
├── README.md              # Este archivo
└── .venv/                 # Entorno virtual (se crea automáticamente)
```

### Requisitos de Desarrollo

- Python 3.7+
- PyQt5
- yt-dlp
- PyInstaller

### Construir desde Código

```bash
# Con entorno virtual activado
python build_exe.py
```

El script de construcción automáticamente:
1. Verifica las dependencias
2. Descarga FFmpeg si es necesario
3. Empaqueta todo en un ejecutable
4. Limpia archivos temporales

## Solución de Problemas

### El ejecutable no funciona
- Asegúrate de que Windows Defender no esté bloqueando el archivo
- Verifica que tengas permisos de ejecución
- Ejecuta desde la línea de comandos para ver errores

### Error de FFmpeg
- El script descarga FFmpeg automáticamente
- Si hay problemas, elimina el directorio `additional_data` y vuelve a construir

### Problemas de descarga
- Verifica tu conexión a internet
- Algunas páginas pueden requerir referer (usar formato URL:REFERER)
- Verifica que la URL sea válida

## Licencia

Este proyecto es de código abierto. Usa yt-dlp y FFmpeg bajo sus respectivas licencias.

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu función
3. Envía un pull request

## Notas Técnicas

- El ejecutable incluye FFmpeg estático (no requiere instalación)
- Usa PyInstaller con modo `--onefile` para portabilidad máxima
- El FFmpeg se descarga desde las builds oficiales de BtbN en GitHub
- Compatible con Windows 10/11 (64-bit)
# Configuración actualizada - FFmpeg integrado
