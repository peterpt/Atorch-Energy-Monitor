import sys
import time
import struct
import hid
# base64 is no longer needed
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QLabel, QCheckBox, QGroupBox, QPushButton, QComboBox,
                             QMessageBox, QDialog, QDialogButtonBox)
from PyQt5.QtGui import QFont, QColor, QPainter, QPixmap
from PyQt5.QtCore import QThread, QObject, pyqtSignal, Qt, QDateTime
from PyQt5.QtChart import (QChart, QChartView, QLineSeries, QValueAxis,
                         QDateTimeAxis, QLegend)

# --- CONFIGURAÇÃO ---
# ATORCH_VID = 0x0483  # Removed - will be auto-detected
# ATORCH_PID = 0x5750  # Removed - will be auto-detected
V_MAX_BATTERY = 14.8
COMMAND_REQUEST_DATA = bytes([
    0x55, 0x05, 0x01, 0x05, 0x0B, 0x00, 0x8C, 0xEE, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])

# --- TRADUÇÕES COMPLETAS ---
TRANSLATIONS = {
    "pt": {"window_title":"Monitor de Energia ATORCH","about":"Sobre","about_title":"Sobre o Monitor ATORCH","dev_by":"Código desenvolvido por:","device_selection":"Seleção de Dispositivo","devices":"Dispositivos:","refresh":"Atualizar","connect":"Conectar","disconnect":"Desconectar","no_device_found":"Nenhum dispositivo ATORCH encontrado","error":"Erro","no_device_selected":"Nenhum dispositivo válido selecionado","realtime_measurements":"Medições em Tempo Real","voltage":"Voltagem:","current":"Corrente:","power":"Potência:","resistance":"Resistência:","energy":"Energia:","temperature":"Temperatura:","battery":"Bateria:","chart_control":"Controlo do Gráfico","reset_zoom":"Reset Zoom","language":"Idioma:","chart_title":"Dados em Tempo Real","time":"Tempo","voltage_axis":"Voltagem (V)","current_power_axis":"Corrente (A) / Potência (W)","comm_error":"Erro de Comunicação","disconnected_message":"{max_failures} leituras consecutivas falharam. Dispositivo desconectado.", "refresh_rate":"Taxa de Atualização:"},
    "en": {"window_title":"ATORCH Energy Monitor","about":"About","about_title":"About ATORCH Monitor","dev_by":"Code developed by:","device_selection":"Device Selection","devices":"Devices:","refresh":"Refresh","connect":"Connect","disconnect":"Disconnect","no_device_found":"No ATORCH device found","error":"Error","no_device_selected":"No valid device selected","realtime_measurements":"Real-Time Measurements","voltage":"Voltage:","current":"Current:","power":"Power:","resistance":"Resistance:","energy":"Energy:","temperature":"Temperature:","battery":"Battery:","chart_control":"Chart Control","reset_zoom":"Reset Zoom","language":"Language:","chart_title":"Real-Time Data","time":"Time","voltage_axis":"Voltage (V)","current_power_axis":"Current (A) / Power (W)","comm_error":"Communication Error","disconnected_message":"{max_failures} consecutive read failures. Device disconnected.", "refresh_rate":"Refresh Rate:"},
    "de": {"window_title":"ATORCH Energiemonitor","about":"Über","about_title":"Über ATORCH Monitor","dev_by":"Code entwickelt von:","device_selection":"Geräteauswahl","devices":"Geräte:","refresh":"Aktualisieren","connect":"Verbinden","disconnect":"Trennen","no_device_found":"Kein ATORCH-Gerät gefunden","error":"Fehler","no_device_selected":"Kein gültiges Gerät ausgewählt","realtime_measurements":"Echtzeitmessungen","voltage":"Spannung:","current":"Strom:","power":"Leistung:","resistance":"Widerstand:","energy":"Energie:","temperature":"Temperatur:","battery":"Batterie:","chart_control":"Diagrammsteuerung","reset_zoom":"Zoom zurücksetzen","language":"Sprache:","chart_title":"Echtzeitdaten","time":"Zeit","voltage_axis":"Spannung (V)","current_power_axis":"Strom (A) / Leistung (W)","comm_error":"Kommunikationsfehler","disconnected_message":"{max_failures} aufeinanderfolgende Lesefehler. Gerät getrennt.", "refresh_rate":"Aktualisierungsrate:"},
    "fr": {"window_title":"Moniteur d'Énergie ATORCH","about":"À propos","about_title":"À propos de ATORCH Monitor","dev_by":"Code développé par:","device_selection":"Sélection de l'appareil","devices":"Appareils:","refresh":"Actualiser","connect":"Connecter","disconnect":"Déconnecter","no_device_found":"Aucun appareil ATORCH trouvé","error":"Erreur","no_device_selected":"Aucun appareil valide sélectionné","realtime_measurements":"Mesures en temps réel","voltage":"Tension:","current":"Courant:","power":"Puissance:","resistance":"Résistance:","energy":"Énergie:","temperature":"Température:","battery":"Batterie:","chart_control":"Contrôle du graphique","reset_zoom":"Réinitialiser le zoom","language":"Langue:","chart_title":"Données en temps réel","time":"Temps","voltage_axis":"Tension (V)","current_power_axis":"Courant (A) / Puissance (W)","comm_error":"Erreur de communication","disconnected_message":"{max_failures} échecs de lecture consécutifs. Appareil déconnecté.", "refresh_rate":"Taux de rafraîchissement:"},
    "es": {"window_title":"Monitor de Energía ATORCH","about":"Acerca de","about_title":"Acerca de ATORCH Monitor","dev_by":"Código desarrollado por:","device_selection":"Selección de Dispositivo","devices":"Dispositivos:","refresh":"Actualizar","connect":"Conectar","disconnect":"Desconectar","no_device_found":"No se encontró ningún dispositivo ATORCH","error":"Error","no_device_selected":"No se ha seleccionado ningún dispositivo válido","realtime_measurements":"Mediciones en Tiempo Real","voltage":"Voltaje:","current":"Corriente:","power":"Potencia:","resistance":"Resistencia:","energy":"Energía:","temperature":"Temperatura:","battery":"Batería:","chart_control":"Control del Gráfico","reset_zoom":"Restablecer Zoom","language":"Idioma:","chart_title":"Datos en Tiempo Real","time":"Tiempo","voltage_axis":"Voltaje (V)","current_power_axis":"Corriente (A) / Potencia (W)","comm_error":"Error de Comunicación","disconnected_message":"{max_failures} fallos de lectura consecutivos. Dispositivo desconectado.", "refresh_rate":"Tasa de Refresco:"},
    "it": {"window_title":"Monitor di Energia ATORCH","about":"Informazioni","about_title":"Informazioni su ATORCH Monitor","dev_by":"Codice sviluppato da:","device_selection":"Selezione Dispositivo","devices":"Dispositivi:","refresh":"Aggiorna","connect":"Connetti","disconnect":"Disconnetti","no_device_found":"Nessun dispositivo ATORCH trovato","error":"Errore","no_device_selected":"Nessun dispositivo valido selezionato","realtime_measurements":"Misure in Tempo Reale","voltage":"Tensione:","current":"Corrente:","power":"Potenza:","resistance":"Resistenza:","energy":"Energia:","temperature":"Temperatura:","battery":"Batteria:","chart_control":"Controllo Grafico","reset_zoom":"Ripristina Zoom","language":"Lingua:","chart_title":"Dati in Tempo Reale","time":"Tempo","voltage_axis":"Tensione (V)","current_power_axis":"Corrente (A) / Potenza (W)","comm_error":"Errore di Comunicazione","disconnected_message":"{max_failures} letture consecutive fallite. Dispositivo disconnesso.", "refresh_rate":"Frequenza di Aggiornamento:"},
    "ru": {"window_title":"Монитор энергии ATORCH","about":"О программе","about_title":"О ATORCH Monitor","dev_by":"Код разработан:","device_selection":"Выбор устройства","devices":"Устройства:","refresh":"Обновить","connect":"Подключить","disconnect":"Отключить","no_device_found":"Устройство ATORCH не найдено","error":"Ошибка","no_device_selected":"Не выбрано допустимое устройство","realtime_measurements":"Измерения в realльном времени","voltage":"Напряжение:","current":"Ток:","power":"Мощность:","resistance":"Сопротивление:","energy":"Энергия:","temperature":"Температура:","battery":"Батарея:","chart_control":"Управление графиком","reset_zoom":"Сбросить масштаб","language":"Язык:","chart_title":"Данные в реальном времени","time":"Время","voltage_axis":"Напряжение (В)","current_power_axis":"Ток (А) / Мощность (Вт)","comm_error":"Ошибка связи","disconnected_message":"{max_failures} последовательных сбоев чтения. Устройство отключено.", "refresh_rate":"Частота обновления:"},
    "zh": {"window_title":"ATORCH 能量监视器","about":"关于","about_title":"关于 ATORCH 监视器","dev_by":"代码开发者:","device_selection":"选择设备","devices":"设备:","refresh":"刷新","connect":"连接","disconnect":"断开","no_device_found":"未找到ATORCH设备","error":"错误","no_device_selected":"未选择有效设备","realtime_measurements":"实时测量","voltage":"电压:","current":"电流:","power":"功率:","resistance":"电阻:","energy":"电能:","temperature":"温度:","battery":"电池:","chart_control":"图表控制","reset_zoom":"重置缩放","language":"语言:","chart_title":"实时数据","time":"时间","voltage_axis":"电压 (V)","current_power_axis":"电流 (A) / 功率 (W)","comm_error":"通信错误","disconnected_message":"{max_failures} 次连续读取失败。设备已断开。", "refresh_rate":"刷新率:"}
}

class AtorchWorker(QObject):
    data_updated = pyqtSignal(dict)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, device_path, refresh_rate=1):
        super().__init__()
        self.running = True
        self.h = None
        self.device_path = device_path
        self.failure_count = 0
        self.max_failures = 5
        self.refresh_rate = refresh_rate

    def run(self):
        try:
            self.h = hid.device()
            self.h.open_path(self.device_path)
        except IOError as e:
            self.error.emit(f"Could not open device. Error: {e}")
            self.finished.emit()
            return

        while self.running:
            data_received = False
            try:
                self.h.write(COMMAND_REQUEST_DATA)
                data = self.h.read(64, timeout_ms=1000)

                if data and len(data) >= 64 and data[0] == 0xAA and data[3] == 0x05:
                    self.failure_count = 0
                    data_received = True
                    voltage_raw = struct.unpack_from('<i', bytearray(data), 8)[0]
                    current_raw = struct.unpack_from('<i', bytearray(data), 12)[0]
                    power_raw = struct.unpack_from('<i', bytearray(data), 16)[0]
                    resistance_raw = struct.unpack_from('<i', bytearray(data), 20)[0]
                    energy_raw = struct.unpack_from('<i', bytearray(data), 24)[0]
                    temp_raw = struct.unpack_from('<i', bytearray(data), 32)[0]

                    output_data = {
                        "voltage": voltage_raw / 1000.0, "current": current_raw / 1000.0,
                        "power": power_raw / 1000.0, "resistance": resistance_raw / 1000.0,
                        "energy": energy_raw / 100.0, "temp": temp_raw / 1000.0,
                        "timestamp": QDateTime.currentDateTime()
                    }
                    self.data_updated.emit(output_data)

            except OSError as e:
                print(f"Read error: {e}")

            if not data_received:
                self.failure_count += 1

            if self.failure_count >= self.max_failures:
                self.error.emit(str(self.max_failures))
                break
            
            time.sleep(self.refresh_rate)

        if self.h:
            self.h.close()
        self.finished.emit()

    def stop(self):
        self.running = False


class DataLabel(QWidget):
    def __init__(self, label_text_key, initial_value, color):
        super().__init__()
        self.label_text_key = label_text_key
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.label = QLabel(self.label_text_key)
        self.label.setFont(QFont('Arial', 12, QFont.Bold)) 
        self.label.setStyleSheet("color: white;")
        self.value = QLabel(initial_value)
        self.value.setFont(QFont('Consolas', 16, QFont.Bold))
        self.value.setStyleSheet(f"color: {color};")
        layout.addWidget(self.label)
        layout.addWidget(self.value, 1, Qt.AlignRight)
    
    def setText(self, text):
        self.value.setText(text)
    
    def translate(self, lang_dict):
        self.label.setText(lang_dict.get(self.label_text_key, self.label_text_key))


class AboutDialog(QDialog):
    def __init__(self, lang_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang_dict.get("about_title", "About"))
        self.setStyleSheet("QDialog { background-color: #3c3c3c; } QLabel { color: white; }")
        self.setFixedSize(350, 220)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        pixmap = QPixmap("gemini.png")
        if pixmap.isNull():
            logo_label.setText("[logo image: gemini.png not found]")
        else:
            logo_label.setPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        credit_label = QLabel(f"{lang_dict.get('dev_by', 'Code developed by:')}\n<b>Gemini (Google AI Model)</b>")
        credit_label.setTextFormat(Qt.RichText)
        credit_label.setAlignment(Qt.AlignCenter)
        credit_label.setFont(QFont('Arial', 10))
        layout.addWidget(credit_label)
        
        layout.addStretch()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "pt"
        self.setWindowTitle("ATORCH Energy Monitor")
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("QMainWindow { background-color: #3c3c3c; }")
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        self.thread = None; self.worker = None

        left_panel = QWidget(); left_layout = QVBoxLayout(left_panel); left_panel.setFixedWidth(320)
        group_style = "QGroupBox{color:white;font-weight:bold;border:1px solid #555;border-radius:5px;margin-top:1ex} QGroupBox::title{subcontrol-origin:margin;subcontrol-position:top center;padding:0 3px} QLabel{color:white;background-color:transparent} QPushButton{color:white;background-color:#555;border:1px solid #777;border-radius:3px;padding:5px} QPushButton:hover{background-color:#666} QComboBox{color:black;background-color:white} QCheckBox{color:white} QCheckBox::indicator{border:1px solid #999;background-color:#ddd;border-radius:3px;width:13px;height:13px} QCheckBox::indicator:checked{background-color:#70a1ff}"
        
        self.device_group = QGroupBox(); self.device_group.setStyleSheet(group_style)
        device_layout = QGridLayout(self.device_group)
        self.device_combo = QComboBox()
        self.device_label = QLabel(); self.refresh_button = QPushButton()
        self.connect_button = QPushButton(); self.connect_button.setStyleSheet("color:white;background-color:green;")
        device_layout.addWidget(self.device_label,0,0); device_layout.addWidget(self.refresh_button,0,1)
        device_layout.addWidget(self.device_combo,1,0,1,2); device_layout.addWidget(self.connect_button,2,0,1,2)
        left_layout.addWidget(self.device_group)

        self.data_group = QGroupBox(); self.data_group.setStyleSheet(group_style)
        data_layout = QGridLayout(self.data_group)
        self.volt_display = DataLabel("voltage", "--- V", "yellow"); self.curr_display = DataLabel("current", "--- A", "lightgreen")
        self.pwr_display = DataLabel("power", "--- W", "#ff4757"); self.res_display = DataLabel("resistance", "--- Ω", "#ffa502")
        self.ene_display = DataLabel("energy", "--- Wh", "#70a1ff"); self.temp_display = DataLabel("temperature", "--- °C", "#5352ed")
        self.batt_display = DataLabel("battery", "--- %", "cyan")
        
        data_layout.addWidget(self.volt_display,0,0)
        data_layout.addWidget(self.curr_display,1,0)
        data_layout.addWidget(self.pwr_display,2,0)
        data_layout.addWidget(self.res_display,3,0)
        data_layout.addWidget(self.ene_display,4,0)
        data_layout.addWidget(self.temp_display,5,0)
        data_layout.addWidget(self.batt_display,6,0)
        left_layout.addWidget(self.data_group)

        self.chart_control_group = QGroupBox(); self.chart_control_group.setStyleSheet(group_style)
        control_layout = QVBoxLayout(self.chart_control_group)
        self.volt_check = QCheckBox(); self.curr_check = QCheckBox(); self.pwr_check = QCheckBox()
        self.reset_zoom_button = QPushButton()
        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Português", "English", "Deutsch", "Français", "Español", "Italiano", "Русский", "中文"])
        self.lang_map = {"Português":"pt","English":"en","Deutsch":"de","Français":"fr","Español":"es","Italiano":"it","Русский":"ru","中文":"zh"}
        
        self.about_button = QPushButton()
        self.refresh_rate_label = QLabel()
        # --- FIX 1 START: Style the refresh rate label ---
        self.refresh_rate_label.setStyleSheet("color: white; font-weight: bold;")
        # --- FIX 1 END ---
        self.refresh_rate_combo = QComboBox()
        self.refresh_rate_combo.addItems(["1s", "3s", "5s"])
        
        control_layout.addWidget(self.volt_check); control_layout.addWidget(self.curr_check); control_layout.addWidget(self.pwr_check)
        control_layout.addSpacing(10); control_layout.addWidget(self.reset_zoom_button)
        control_layout.addSpacing(10); control_layout.addWidget(self.language_label); control_layout.addWidget(self.language_combo)
        left_layout.addWidget(self.chart_control_group); left_layout.addStretch()
        
        right_panel = QWidget(); right_layout = QVBoxLayout(right_panel)

        top_controls_widget = QWidget()
        top_controls_layout = QHBoxLayout(top_controls_widget)
        top_controls_layout.setContentsMargins(0,0,10,0)
        top_controls_layout.addWidget(self.refresh_rate_label)
        top_controls_layout.addWidget(self.refresh_rate_combo)
        top_controls_layout.addStretch()
        top_controls_layout.addWidget(self.about_button)
        right_layout.addWidget(top_controls_widget)

        self.chart = QChart(); self.chart.setTheme(QChart.ChartThemeDark); self.chart.setBackgroundBrush(QColor("#2c2c2c"))
        self.chart.legend().setLabelColor(QColor("white")); self.chart.setTitleBrush(QColor("white"))
        self.series_volt = QLineSeries(); self.series_volt.setColor(QColor("yellow")); self.series_curr = QLineSeries(); self.series_curr.setColor(QColor("lightgreen")); self.series_pwr = QLineSeries(); self.series_pwr.setColor(QColor("#ff4757"))
        self.chart.addSeries(self.series_volt); self.chart.addSeries(self.series_curr); self.chart.addSeries(self.series_pwr)
        self.axis_x = QDateTimeAxis(); self.axis_x.setFormat("hh:mm:ss"); self.axis_x.setLabelsColor(QColor("white"))
        self.axis_y1 = QValueAxis(); self.axis_y1.setLinePenColor(QColor("yellow")); self.axis_y1.setLabelsColor(QColor("white"))
        self.axis_y2 = QValueAxis(); self.axis_y2.setLinePenColor(QColor("lightgreen")); self.axis_y2.setLabelsColor(QColor("white"))
        self.chart.addAxis(self.axis_x, Qt.AlignBottom); self.chart.addAxis(self.axis_y1, Qt.AlignLeft); self.chart.addAxis(self.axis_y2, Qt.AlignRight)
        self.series_volt.attachAxis(self.axis_x); self.series_volt.attachAxis(self.axis_y1); self.series_curr.attachAxis(self.axis_x); self.series_curr.attachAxis(self.axis_y2)
        self.series_pwr.attachAxis(self.axis_x); self.series_pwr.attachAxis(self.axis_y2)
        self.chart_view = QChartView(self.chart); self.chart_view.setRenderHint(QPainter.Antialiasing); self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
        
        right_layout.addWidget(self.chart_view)
        
        main_layout.addWidget(left_panel); main_layout.addWidget(right_panel, 1)
        
        self.refresh_button.clicked.connect(self.populate_devices); self.connect_button.clicked.connect(self.toggle_connection); self.reset_zoom_button.clicked.connect(self.reset_chart_zoom)
        self.volt_check.stateChanged.connect(lambda: self.series_volt.setVisible(self.volt_check.isChecked()))
        self.curr_check.stateChanged.connect(lambda: self.series_curr.setVisible(self.curr_check.isChecked()))
        self.pwr_check.stateChanged.connect(lambda: self.series_pwr.setVisible(self.pwr_check.isChecked()))
        self.language_combo.currentTextChanged.connect(lambda text: self.change_language(self.lang_map.get(text, "en")))
        self.about_button.clicked.connect(self.open_about_dialog)
        
        self.populate_devices(); self.translate_ui()

    def open_about_dialog(self):
        lang_dict = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        dialog = AboutDialog(lang_dict, self); dialog.exec_()
    def calculate_percentage(self, current_v, max_v=V_MAX_BATTERY):
        if max_v <= 0: return 0
        percentage = (current_v / max_v) * 100
        if percentage > 100: percentage = 100
        if percentage < 0: percentage = 0
        return int(round(percentage, 0))
    def change_language(self, lang_code):
        self.current_lang = lang_code; self.translate_ui()
    def translate_ui(self):
        d = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        self.setWindowTitle(d.get("window_title")); self.device_group.setTitle(d.get("device_selection"))
        self.device_label.setText(d.get("devices")); self.refresh_button.setText(d.get("refresh"))
        if self.thread and self.thread.isRunning(): self.connect_button.setText(d.get("disconnect"))
        else: self.connect_button.setText(d.get("connect"))
        self.data_group.setTitle(d.get("realtime_measurements"))
        for widget in [self.volt_display, self.curr_display, self.pwr_display, self.res_display, self.ene_display, self.temp_display, self.batt_display]:
            widget.translate(d)
        self.chart_control_group.setTitle(d.get("chart_control"))
        self.volt_check.setText(f'{d.get("voltage", "Voltage")} (V)'); self.curr_check.setText(f'{d.get("current", "Current")} (A)'); self.pwr_check.setText(f'{d.get("power", "Power")} (W)')
        self.reset_zoom_button.setText(d.get("reset_zoom"))
        self.refresh_rate_label.setText(d.get("refresh_rate"))
        self.language_label.setText(d.get("language")); self.about_button.setText(d.get("about", "About"))
        self.chart.setTitle(d.get("chart_title")); self.series_volt.setName(f'{d.get("voltage")} (V)'); self.series_curr.setName(f'{d.get("current")} (A)'); self.series_pwr.setName(f'{d.get("power")} (W)')
        self.axis_x.setTitleText(d.get("time")); self.axis_y1.setTitleText(d.get("voltage_axis")); self.axis_y2.setTitleText(d.get("current_power_axis"))
    def wheelEvent(self, event):
        if self.chart_view.underMouse(): factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2; self.chart.zoom(factor)
        
    # --- FIX 2 START: Correct the reset zoom logic ---
    def reset_chart_zoom(self):
        self.chart.zoomReset()
    # --- FIX 2 END ---

    def populate_devices(self):
        d = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        self.device_combo.clear(); self.devices = hid.enumerate()
        found_atorch = False
        if not self.devices:
            self.device_combo.addItem(d.get("no_device_found")); self.connect_button.setEnabled(False)
        else:
            for i, dev in enumerate(self.devices):
                if "ATORCH" in dev.get('product_string', '').upper():
                    self.device_combo.addItem(f"Dispositivo {i+1}: {dev['product_string']}", dev['path'])
                    found_atorch = True
            if not found_atorch:
                self.device_combo.addItem(d.get("no_device_found")); self.connect_button.setEnabled(False)
            else:
                self.connect_button.setEnabled(True)
    def toggle_connection(self):
        d = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        if self.thread and self.thread.isRunning(): self.worker.stop()
        else:
            selected_path = self.device_combo.currentData()
            if not selected_path: QMessageBox.warning(self, d.get("error"), d.get("no_device_selected")); return
            
            rate_text = self.refresh_rate_combo.currentText()
            rate_value = int(rate_text.replace('s', ''))
            self.thread = QThread()
            self.worker = AtorchWorker(selected_path, rate_value)
            
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run); self.worker.finished.connect(self.on_worker_finished)
            self.worker.data_updated.connect(self.update_ui); self.worker.error.connect(self.show_error)
            self.connect_button.setText(d.get("disconnect")); self.connect_button.setStyleSheet("color:white;background-color:red;")
            
            self.refresh_button.setEnabled(False); self.device_combo.setEnabled(False); self.refresh_rate_combo.setEnabled(False)
            
            self.thread.start()
            
    def on_worker_finished(self):
        d = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        if self.thread: self.thread.quit(); self.thread.wait()
        self.connect_button.setText(d.get("connect")); self.connect_button.setStyleSheet("color:white;background-color:green;")
        
        self.refresh_button.setEnabled(True); self.device_combo.setEnabled(True); self.refresh_rate_combo.setEnabled(True)
        
    def update_ui(self, data):
        self.last_data = data; timestamp = data.get("timestamp");
        if not timestamp: return
        voltage = data.get('voltage', 0)
        self.volt_display.setText(f"{voltage:.3f} V"); self.curr_display.setText(f"{data.get('current', 0):.3f} A")
        self.pwr_display.setText(f"{data.get('power', 0):.3f} W"); self.res_display.setText(f"{data.get('resistance', 0):.3f} Ω")
        self.ene_display.setText(f"{data.get('energy', 0):.2f} Wh"); self.temp_display.setText(f"{data.get('temp', 0):.1f} °C")
        self.batt_display.setText(f"{self.calculate_percentage(voltage)} %")
        ms_timestamp = timestamp.toMSecsSinceEpoch()
        self.series_volt.append(ms_timestamp, voltage); self.series_curr.append(ms_timestamp, data.get('current', 0)); self.series_pwr.append(ms_timestamp, data.get('power', 0))
        if self.series_volt.count() > 300: self.series_volt.remove(0); self.series_curr.remove(0); self.series_pwr.remove(0)
        if not self.chart.isZoomed():
            self.axis_x.setRange(timestamp.addSecs(-60), timestamp)
            points_v=[p.y() for p in self.series_volt.pointsVector()]; points_c=[p.y() for p in self.series_curr.pointsVector()]; points_p=[p.y() for p in self.series_pwr.pointsVector()]
            max_v=max(points_v) if points_v else 1; max_cp=max(points_c+points_p) if (points_c or points_p) else 1
            self.axis_y1.setRange(0, max_v*1.2 if max_v>0 else 1); self.axis_y2.setRange(0, max_cp*1.2 if max_cp>0 else 1)
            
    def show_error(self, message):
        d = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        try:
            max_failures = int(message)
            msg = d.get("disconnected_message").format(max_failures=max_failures)
            QMessageBox.critical(self, d.get("comm_error"), msg)
        except ValueError:
            QMessageBox.critical(self, d.get("comm_error"), message)
        
        self.on_worker_finished()

    def closeEvent(self, event):
        if hasattr(self, 'thread') and self.thread and self.thread.isRunning(): 
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = MainWindow(); window.show(); sys.exit(app.exec_())
