# video_descarga.py
import sys
import subprocess
import shutil
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QComboBox, QProgressBar, QMessageBox, QCheckBox, QSpinBox, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

def get_ytdlp_path():
    """Obtiene la ruta correcta de yt-dlp, ya sea empaquetado o instalado"""
    # Si estamos en un ejecutable empaquetado, buscar en el directorio del ejecutable
    if getattr(sys, 'frozen', False):
        # Ejecutable empaquetado
        app_dir = os.path.dirname(sys.executable)
        bundled_ytdlp = os.path.join(app_dir, 'yt-dlp.exe')
        if os.path.exists(bundled_ytdlp):
            return bundled_ytdlp
    
    # Buscar en el entorno virtual local
    venv_ytdlp = os.path.join(os.getcwd(), "modules", "Scripts", "yt-dlp.exe")
    if os.path.exists(venv_ytdlp):
        return venv_ytdlp
    
    # Buscar en el PATH del sistema
    try:
        result = subprocess.run(['where', 'yt-dlp'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    # Como último recurso, usar 'yt-dlp' (debe estar en PATH)
    return 'yt-dlp'

class YTDLPWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()
    current_progress = pyqtSignal(str)

    def __init__(self, commands):
        super().__init__()
        self.commands = commands
        self._is_running = True

    def run(self):
        total = len(self.commands)
        for idx, cmd in enumerate(self.commands):
            if not self._is_running:
                break
            try:
                self.current_progress.emit(f"Descargando video {idx + 1} de {total}...")
                self.log.emit(f"Ejecutando: {' '.join(cmd)}\n")
                
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.log.emit(output.strip())
                        # Extraer progreso de descarga de yt-dlp si está disponible
                        if '[download]' in output and '%' in output:
                            try:
                                percent_match = re.search(r'(\d+\.?\d*)%', output)
                                if percent_match:
                                    video_progress = float(percent_match.group(1))
                                    total_progress = ((idx * 100) + video_progress) / total
                                    self.progress.emit(int(total_progress))
                            except:
                                pass
                
                process.wait()
                if process.returncode != 0:
                    self.error.emit(f"Error en descarga del video {idx + 1}: Código de salida {process.returncode}")
                else:
                    self.log.emit(f"✓ Video {idx + 1} descargado exitosamente\n")
                    
            except FileNotFoundError:
                self.error.emit("yt-dlp no encontrado. Asegúrate de que esté instalado y en el PATH.")
                break
            except Exception as e:
                self.error.emit(f"Error inesperado en video {idx + 1}: {str(e)}")
            
            # Actualizar progreso por video completado
            self.progress.emit(int((idx + 1) / total * 100))
            
        self.finished.emit()

    def stop(self):
        self._is_running = False

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Descargador de videos con yt-dlp")
        self.setGeometry(100, 100, 900, 700)
        self.worker = None
        self.check_ytdlp()
        self.init_ui()

    def check_ytdlp(self):
        """Verificar si yt-dlp está disponible"""
        try:
            ytdlp_path = get_ytdlp_path()
            result = subprocess.run([ytdlp_path, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.ytdlp_available = True
                self.ytdlp_version = result.stdout.strip()
                self.ytdlp_path = ytdlp_path
            else:
                self.ytdlp_available = False
                self.ytdlp_path = 'yt-dlp'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.ytdlp_available = False
            self.ytdlp_path = 'yt-dlp'

    def init_ui(self):
        layout = QVBoxLayout()

        # Información de yt-dlp
        if not self.ytdlp_available:
            warning_label = QLabel("⚠️ yt-dlp no está disponible. Instálalo con: pip install yt-dlp")
            warning_label.setStyleSheet("color: red; font-weight: bold; padding: 10px; background-color: #ffe6e6; border: 1px solid red;")
            layout.addWidget(warning_label)
        else:
            info_label = QLabel(f"✓ yt-dlp disponible: {self.ytdlp_version}")
            info_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
            layout.addWidget(info_label)

        # Campo de URLs
        url_group = QGroupBox("URLs para descargar")
        url_layout = QVBoxLayout()
        url_help = QLabel("Formato: URL1, URL2:referer, URL3, ...")
        url_help.setStyleSheet("font-style: italic; color: gray;")
        self.url_input = QTextEdit()
        self.url_input.setMaximumHeight(100)
        self.url_input.setPlaceholderText("https://ejemplo.com/video1, https://ejemplo.com/video2:https://referer.com")
        url_layout.addWidget(url_help)
        url_layout.addWidget(self.url_input)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Opciones en grid
        options_group = QGroupBox("Opciones de descarga")
        options_layout = QGridLayout()
        
        # Formato
        options_layout.addWidget(QLabel("Formato:"), 0, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "webm", "mkv", "avi", "best", "worst"])
        options_layout.addWidget(self.format_combo, 0, 1)

        # Calidad
        options_layout.addWidget(QLabel("Calidad:"), 0, 2)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "worst", "720p", "480p", "360p", "bestvideo+bestaudio"])
        options_layout.addWidget(self.quality_combo, 0, 3)

        # Subtítulos
        self.subs_checkbox = QCheckBox("Descargar subtítulos")
        options_layout.addWidget(self.subs_checkbox, 1, 0)

        # Audio only
        self.audio_only_checkbox = QCheckBox("Solo audio")
        options_layout.addWidget(self.audio_only_checkbox, 1, 1)

        # Playlist option
        self.no_playlist_checkbox = QCheckBox("Solo video individual (no playlist)")
        self.no_playlist_checkbox.setChecked(True)  # Marcado por defecto
        self.no_playlist_checkbox.setToolTip("Si está marcado, solo descarga el video individual aunque sea parte de una playlist")
        options_layout.addWidget(self.no_playlist_checkbox, 2, 0)

        # Carpeta de descarga
        options_layout.addWidget(QLabel("Carpeta:"), 2, 1)
        self.output_dir = QLineEdit()
        self.output_dir.setText("./downloads")
        options_layout.addWidget(self.output_dir, 2, 2, 1, 2)  # Span 2 columns

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Estado actual
        self.status_label = QLabel("Listo para descargar")
        self.status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.status_label)

        # Terminal embebida
        terminal_group = QGroupBox("Progreso de descarga")
        terminal_layout = QVBoxLayout()
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("font-family: Consolas, monospace; background-color: #1e1e1e; color: #ffffff;")
        terminal_layout.addWidget(self.terminal)
        terminal_group.setLayout(terminal_layout)
        layout.addWidget(terminal_group)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        layout.addWidget(self.progress_bar)

        # Botones
        button_layout = QHBoxLayout()
        self.download_btn = QPushButton("🔽 Iniciar Descarga")
        self.download_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;")
        self.download_btn.clicked.connect(self.start_download)
        
        self.stop_btn = QPushButton("⏹️ Detener")
        self.stop_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f44336; color: white; border: none; border-radius: 5px;")
        self.stop_btn.clicked.connect(self.stop_download)
        self.stop_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("🗑️ Limpiar Terminal")
        self.clear_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #2196F3; color: white; border: none; border-radius: 5px;")
        self.clear_btn.clicked.connect(self.terminal.clear)
        
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.clear_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def start_download(self):
        if not self.ytdlp_available:
            QMessageBox.critical(self, "Error", "yt-dlp no está disponible. Instálalo primero con: pip install yt-dlp")
            return
            
        urls_raw = self.url_input.toPlainText().strip()
        if not urls_raw:
            QMessageBox.warning(self, "Error", "Debes ingresar al menos una URL.")
            return
            
        # Crear directorio de descarga si no existe
        output_dir = self.output_dir.text().strip() or "./downloads"
        os.makedirs(output_dir, exist_ok=True)
        
        urls = [u.strip() for u in urls_raw.replace('\n', ',').split(",") if u.strip()]
        format_opt = self.format_combo.currentText()
        quality_opt = self.quality_combo.currentText()
        subs_opt = self.subs_checkbox.isChecked()
        audio_only = self.audio_only_checkbox.isChecked()
        no_playlist = self.no_playlist_checkbox.isChecked()
        
        commands = []
        for url in urls:
            referer = None
            # Verificar si hay referer después de los dos puntos
            # Solo dividir si hay ":http" que no sea parte del protocolo inicial
            if url.count(':') > 2:  # Más de 2 dos puntos (protocolo + puerto/referer)
                # Buscar el último ":" que no sea parte de "https://"
                if ':http' in url[8:]:  # Buscar después de "https://"
                    last_colon_pos = url.rfind(':http')
                    if last_colon_pos > 8:  # Asegurar que no sea el protocolo inicial
                        referer = url[last_colon_pos + 1:].strip()
                        url = url[:last_colon_pos].strip()
                        
                        # CORRECCIÓN ESPECIAL PARA VIMEO EMBEDS
                        if 'player.vimeo.com/video/' in url:
                            # Para Vimeo embebido, usar la URL de Vimeo como principal
                            # y la página del curso como referer
                            self.terminal.append(f"🎬 Vimeo embed detectado: usando URL de Vimeo como principal")
                            self.terminal.append(f"📺 URL de Vimeo: {url}")
                            self.terminal.append(f"🌐 Referer (página del curso): {referer}")
                            # url y referer ya están en la posición correcta
                        elif 'vimeo.com' in url and 'vimeo.com' in referer:
                            # Para otros casos de Vimeo, usar referer normalmente
                            self.terminal.append(f"🎬 Vimeo URL con referer: {url}")
                            self.terminal.append(f"🌐 Referer: {referer}")
                            
            elif ':' in url and not url.startswith(("http://", "https://")) and url.count(':') == 1:
                # Caso simple sin protocolo
                parts = url.split(":", 1)
                url, referer = parts[0].strip(), parts[1].strip()
            
            cmd = [self.ytdlp_path, url]
            
            # Formato y calidad
            if audio_only:
                cmd += ["-f", "bestaudio/best", "--extract-audio", "--audio-format", "mp3"]
            else:
                cmd += ["-f", quality_opt]
                if format_opt != "best":
                    cmd += ["--recode-video", format_opt]
            
            # Subtítulos
            if subs_opt:
                cmd += ["--write-subs", "--sub-lang", "all"]
            
            # Referer
            if referer:
                cmd += ["--referer", referer]
            
            # Directorio de salida
            cmd += ["-o", f"{output_dir}/%(title)s.%(ext)s"]
            
            # Opciones adicionales para mejor compatibilidad
            additional_options = [
                "--no-warnings", 
                "--no-check-certificates",
                "--restrict-filenames",
                "--windows-filenames",
                "--fragment-retries", "5",
                "--retries", "3",
                "--file-access-retries", "5",
                "--no-continue"
            ]
            
            # Solo agregar --no-playlist si la opción está marcada
            if no_playlist:
                additional_options.append("--no-playlist")
                
            cmd += additional_options
            
            commands.append(cmd)
        
        self.terminal.clear()
        self.terminal.append(f"🚀 Iniciando descarga de {len(commands)} video(s)...\n")
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Descargando {len(commands)} video(s)...")
        
        self.worker = YTDLPWorker(commands)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.log.connect(self.append_terminal)
        self.worker.error.connect(self.show_error)
        self.worker.finished.connect(self.download_finished)
        self.worker.current_progress.connect(self.status_label.setText)
        
        self.download_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.worker.start()

    def stop_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.terminate()
            self.terminal.append("\n⏹️ Descarga detenida por el usuario\n")
            self.download_finished()

    def append_terminal(self, text):
        self.terminal.append(text)
        # Auto-scroll al final
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_error(self, msg):
        self.terminal.append(f"❌ ERROR: {msg}\n")
        if "yt-dlp no encontrado" in msg:
            QMessageBox.critical(self, "Error", f"{msg}\n\nPor favor instala yt-dlp usando: pip install yt-dlp")
        else:
            QMessageBox.warning(self, "Error de descarga", msg)

    def download_finished(self):
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Descarga completada")
        self.terminal.append("\n✅ Todas las descargas han finalizado.\n")
        QMessageBox.information(self, "Descarga finalizada", "Todas las descargas han terminado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
