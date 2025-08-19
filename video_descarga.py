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

class YTDLPWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()
    current_progress = pyqtSignal(str)

    def __init__(self, commands, output_dir):
        super().__init__()
        self.commands = commands
        self.output_dir = output_dir
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
                    # Limpiar archivos temporales en caso de error
                    self.cleanup_temp_files(self.output_dir)
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

    def cleanup_temp_files(self, output_dir):
        """Limpiar archivos temporales (.part, .part-Frag, etc.)"""
        try:
            import glob
            temp_patterns = [
                os.path.join(output_dir, "*.part"),
                os.path.join(output_dir, "*.part-Frag*"),
                os.path.join(output_dir, "*.ytdl"),
                os.path.join(output_dir, "*.temp"),
            ]
            
            for pattern in temp_patterns:
                for temp_file in glob.glob(pattern):
                    try:
                        os.remove(temp_file)
                        self.log.emit(f"🗑️ Archivo temporal eliminado: {os.path.basename(temp_file)}")
                    except:
                        pass  # Ignorar errores al eliminar archivos temporales
        except Exception:
            pass  # Ignorar errores en la limpieza

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
            # Intentar usar yt-dlp del entorno virtual primero
            ytdlp_path = os.path.join(os.path.dirname(__file__), "modules", "Scripts", "yt-dlp.exe")
            if os.path.exists(ytdlp_path):
                self.ytdlp_cmd = ytdlp_path
            else:
                self.ytdlp_cmd = "yt-dlp"
                
            result = subprocess.run([self.ytdlp_cmd, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.ytdlp_available = True
                self.ytdlp_version = result.stdout.strip()
            else:
                self.ytdlp_available = False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.ytdlp_available = False
            self.ytdlp_cmd = "yt-dlp"

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
        url_help = QLabel("Formato: URL1, URL2:referer_completo, URL3, ...")
        url_help2 = QLabel("Ejemplo: https://player.vimeo.com/video/123:https://escuela.it/cursos/...")
        url_help.setStyleSheet("font-style: italic; color: gray;")
        url_help2.setStyleSheet("font-style: italic; color: #666; font-size: 11px;")
        self.url_input = QTextEdit()
        self.url_input.setMaximumHeight(100)
        self.url_input.setPlaceholderText("https://ejemplo.com/video1, https://player.vimeo.com/video/123:https://referer.com")
        url_layout.addWidget(url_help)
        url_layout.addWidget(url_help2)
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

        # Carpeta de descarga
        options_layout.addWidget(QLabel("Carpeta:"), 1, 2)
        self.output_dir = QLineEdit()
        self.output_dir.setText("./downloads")
        options_layout.addWidget(self.output_dir, 1, 3)

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
            elif ':' in url and not url.startswith(("http://", "https://")) and url.count(':') == 1:
                # Caso simple sin protocolo
                parts = url.split(":", 1)
                url, referer = parts[0].strip(), parts[1].strip()
            
            cmd = [self.ytdlp_cmd, url]
            
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
            
            # Directorio de salida con nombre de archivo más compatible
            safe_filename = "%(title)s.%(ext)s"
            cmd += ["-o", f"{output_dir}/{safe_filename}"]
            
            # Opciones adicionales para mejor compatibilidad en Windows
            cmd += [
                "--no-warnings",
                "--no-check-certificates",
                "--restrict-filenames",  # Usar solo caracteres ASCII seguros
                "--windows-filenames",   # Nombres de archivo compatibles con Windows
                "--fragment-retries", "5",  # Reintentar fragmentos fallidos
                "--retries", "3",        # Reintentar descargas fallidas
                "--file-access-retries", "5",  # Reintentar acceso a archivos
                "--no-continue",         # No continuar descargas parciales para evitar conflictos
            ]
            
            commands.append(cmd)
        
        self.terminal.clear()
        self.terminal.append(f"🚀 Iniciando descarga de {len(commands)} video(s)...\n")
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Descargando {len(commands)} video(s)...")
        
        self.worker = YTDLPWorker(commands, output_dir)
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
