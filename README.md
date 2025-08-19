# 🎥 Descargador de Videos con yt-dlp

Una aplicación de escritorio en Python con interfaz gráfica para descargar videos usando yt-dlp.

## ✨ Características

- 🖥️ **Interfaz gráfica intuitiva** con PyQt5
- 🔗 **Múltiples URLs** separadas por comas
- 🌐 **Soporte para referer** (formato: `URL:referer`)
- 📱 **Múltiples formatos** (MP4, WebM, MKV, AVI)
- 🎵 **Descarga solo audio** (MP3)
- 📝 **Subtítulos automáticos** cuando están disponibles
- 📊 **Barra de progreso** en tiempo real
- 🖥️ **Terminal embebida** para ver el progreso detallado
- ⏹️ **Control de descarga** (iniciar/detener)
- 🗑️ **Limpieza automática** de archivos temporales
- 🔄 **Reintentos automáticos** para mayor confiabilidad

## 🚀 Instalación y Uso

### Requisitos previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Clona o descarga** este repositorio
2. **Navega** a la carpeta del proyecto
3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

### Ejecución

```bash
python video_descarga.py
```

## 📖 Guía de Uso

### Formato de URLs
- **URLs simples**: Separa múltiples URLs con comas
  ```
  https://ejemplo.com/video1, https://ejemplo.com/video2
  ```

- **URLs con referer**: Agrega el referer después de dos puntos
  ```
  https://player.vimeo.com/video/123:https://escuela.it/cursos/...
  ```

### Opciones disponibles
- **Formato**: MP4, WebM, MKV, AVI, best, worst
- **Calidad**: best, worst, 720p, 480p, 360p, bestvideo+bestaudio
- **Solo audio**: Extrae solo el audio en formato MP3
- **Subtítulos**: Descarga subtítulos en todos los idiomas disponibles
- **Carpeta de descarga**: Personalizable (por defecto: `./downloads`)

## 🛠️ Compilar a Ejecutable

Para crear un archivo ejecutable independiente:

1. **Instala PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Compila la aplicación**:
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico video_descarga.py
   ```

3. El ejecutable estará en la carpeta `dist/`

## 🔧 Solución de Problemas

### Error: "yt-dlp no encontrado"
- Asegúrate de que yt-dlp esté instalado: `pip install yt-dlp`
- La aplicación verificará automáticamente la instalación

### Errores de fragmentos en Windows
- La aplicación incluye opciones optimizadas para Windows
- Se limpian automáticamente los archivos temporales en caso de error

### Caracteres especiales en nombres
- Se usan nombres de archivo compatibles con Windows automáticamente
- Se restringen caracteres problemáticos

## 📁 Estructura del Proyecto

```
video-descarga/
├── video_descarga.py      # Aplicación principal
├── requirements.txt       # Dependencias
├── .gitignore            # Archivos a ignorar en git
├── README.md             # Este archivo
└── downloads/            # Carpeta de descargas (se crea automáticamente)
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Si encuentras un bug o tienes una mejora:

1. Abre un **Issue** describiendo el problema
2. Haz un **Fork** del repositorio
3. Crea una **rama** para tu feature
4. Haz **commit** de tus cambios
5. Abre un **Pull Request**

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## ⚡ Créditos

- **yt-dlp**: La biblioteca principal para descargar videos
- **PyQt5**: Framework para la interfaz gráfica
- **Python**: Lenguaje de programación

---

*Desarrollado con ❤️ para facilitar la descarga de videos educativos y contenido libre.*
