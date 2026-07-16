"""
Dialog do PRA Divider - Interface Responsiva Premium
Design moderno e adaptável a qualquer tamanho de tela
"""

from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                  QLabel, QComboBox, QRadioButton, 
                                  QPushButton, QGroupBox, QButtonGroup,
                                  QProgressBar, QFrame, QWidget, QScrollArea,
                                  QSizePolicy)
from qgis.PyQt.QtCore import Qt, QTimer, QSize, QEvent
from qgis.PyQt.QtGui import QFont, QPalette, QColor, QIcon
from qgis.core import QgsProject, QgsWkbTypes


class PRADividerDialog(QDialog):
    """Dialog principal do plugin com design responsivo premium"""
    
    def __init__(self, parent=None):
        super(PRADividerDialog, self).__init__(parent)
        self.setWindowTitle("PRA Divider Pro")
        
        # Tamanho inicial responsivo
        self.resize(700, 750)
        self.setMinimumSize(500, 600)
        
        # Permitir redimensionamento
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setup_ui()
        self.apply_premium_style()
        
    def setup_ui(self):
        """Configurar interface responsiva"""
        # Layout principal com scroll
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area para conteúdo responsivo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget de conteúdo
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # ==================== HEADER RESPONSIVO ====================
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(20, 25, 20, 25)
        
        # Logo e Título
        title_label = QLabel("🌳 PRA DIVIDER")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Divisão Profissional • Regularização Ambiental")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setWordWrap(True)
        header_layout.addWidget(subtitle_label)
        
        header_frame.setLayout(header_layout)
        content_layout.addWidget(header_frame)
        
        # ==================== SELEÇÃO DE CAMADA ====================
        layer_card = self.create_card(
            "📍 CAMADA",
            "Selecione a camada vetorial poligonal"
        )
        
        self.layer_combo = QComboBox()
        self.layer_combo.setObjectName("premiumCombo")
        self.layer_combo.setMinimumHeight(45)
        self.layer_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layer_card.layout().addWidget(self.layer_combo)
        
        content_layout.addWidget(layer_card)
        
        # ==================== TIPO DE DIVISÃO ====================
        type_card = self.create_card(
            "⚙️ TIPO",
            "Escolha a configuração de divisão"
        )
        
        # Radio buttons responsivos
        self.button_group = QButtonGroup()
        
        # APP Radio
        self.radio_app = self.create_radio_option(
            "🌊 APP",
            "5 partes • Preservação Permanente",
            False
        )
        type_card.layout().addWidget(self.radio_app)
        
        # RL Radio
        self.radio_rl = self.create_radio_option(
            "🌲 Reserva Legal",
            "10 partes • Propriedades Rurais",
            True
        )
        type_card.layout().addWidget(self.radio_rl)
        
        self.button_group.addButton(self.radio_app.findChild(QRadioButton), 1)
        self.button_group.addButton(self.radio_rl.findChild(QRadioButton), 2)
        
        content_layout.addWidget(type_card)
        
        # ==================== INFORMAÇÕES ====================
        info_card = QFrame()
        info_card.setObjectName("infoCard")
        info_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        info_title = QLabel("ℹ️ REQUISITOS")
        info_title.setObjectName("infoTitle")
        info_layout.addWidget(info_title)
        
        info_text = QLabel(
            "✓ Sistema UTM obrigatório<br>"
            "✓ Geometrias válidas<br>"
            "⚠️ Lat/lon não suportado"
        )
        info_text.setObjectName("infoText")
        info_text.setWordWrap(True)
        info_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        info_layout.addWidget(info_text)
        
        info_card.setLayout(info_layout)
        content_layout.addWidget(info_card)
        
        # ==================== PROGRESSO ====================
        self.progress_container = QFrame()
        self.progress_container.setObjectName("progressContainer")
        self.progress_container.setVisible(False)
        self.progress_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(10)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("premiumProgress")
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_container.setLayout(progress_layout)
        content_layout.addWidget(self.progress_container)
        
        # Espaçador flexível
        content_layout.addStretch()
        
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # ==================== BOTÕES FIXOS NO RODAPÉ ====================
        button_container = QFrame()
        button_container.setObjectName("buttonContainer")
        button_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(20, 15, 20, 15)
        
        self.cancel_button = QPushButton("✕ Cancelar")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        
        self.ok_button = QPushButton("🚀 PROCESSAR")
        self.ok_button.setObjectName("processButton")
        self.ok_button.setMinimumHeight(45)
        self.ok_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setCursor(Qt.PointingHandCursor)
        
        button_layout.addWidget(self.cancel_button, 1)
        button_layout.addWidget(self.ok_button, 2)
        
        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container)
        
        self.setLayout(main_layout)
    
    def create_card(self, title, description):
        """Criar card responsivo"""
        card = QFrame()
        card.setObjectName("card")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("cardDescription")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        card.setLayout(layout)
        return card
    
    def create_radio_option(self, title, subtitle, checked=False):
        """Criar opção de radio responsiva"""
        container = QFrame()
        container.setObjectName("radioContainer")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        radio = QRadioButton()
        radio.setObjectName("premiumRadio")
        radio.setChecked(checked)
        radio.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        
        title_label = QLabel(title)
        title_label.setObjectName("radioTitle")
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("radioSubtitle")
        subtitle_label.setWordWrap(True)
        text_layout.addWidget(subtitle_label)
        
        layout.addWidget(radio)
        layout.addLayout(text_layout, 1)
        
        container.setLayout(layout)
        return container
    
    def apply_premium_style(self):
        """Aplicar estilo premium responsivo"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
            }
            
            #titleLabel {
                color: white;
                font-size: 22pt;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            #subtitleLabel {
                color: rgba(255, 255, 255, 0.95);
                font-size: 9pt;
            }
            
            #card {
                background: white;
                border-radius: 10px;
                border: 1px solid #dee2e6;
            }
            
            #cardTitle {
                color: #2d3748;
                font-size: 11pt;
                font-weight: bold;
            }
            
            #cardDescription {
                color: #718096;
                font-size: 9pt;
            }
            
            #premiumCombo {
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                color: #2d3748;
                font-size: 10pt;
            }
            
            #premiumCombo:hover {
                border-color: #667eea;
            }
            
            #premiumCombo:focus {
                border-color: #667eea;
                background: #f7fafc;
            }
            
            #premiumCombo::drop-down {
                border: none;
                width: 25px;
            }
            
            #premiumCombo::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #667eea;
                margin-right: 8px;
            }
            
            #radioContainer {
                background: #f8f9fa;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin: 3px 0;
            }
            
            #radioContainer:hover {
                background: #fff;
                border-color: #667eea;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
            }
            
            #premiumRadio::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #cbd5e0;
                background: white;
            }
            
            #premiumRadio::indicator:hover {
                border-color: #667eea;
            }
            
            #premiumRadio::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-color: #667eea;
            }
            
            #radioTitle {
                color: #2d3748;
                font-size: 10pt;
                font-weight: bold;
            }
            
            #radioSubtitle {
                color: #718096;
                font-size: 8pt;
            }
            
            #infoCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e3f2fd, stop:1 #f3e5f5);
                border-radius: 10px;
                border: 1px solid #bbdefb;
            }
            
            #infoTitle {
                color: #1565c0;
                font-size: 10pt;
                font-weight: bold;
            }
            
            #infoText {
                color: #424242;
                font-size: 9pt;
                line-height: 1.5;
            }
            
            #progressContainer {
                background: white;
                border-radius: 10px;
                border: 2px solid #667eea;
            }
            
            #statusLabel {
                color: #667eea;
                font-size: 10pt;
                font-weight: bold;
            }
            
            #premiumProgress {
                border: none;
                border-radius: 6px;
                background: #e9ecef;
                text-align: center;
                font-size: 9pt;
                font-weight: bold;
            }
            
            #premiumProgress::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 6px;
            }
            
            #buttonContainer {
                background: white;
                border-top: 1px solid #e2e8f0;
            }
            
            #cancelButton {
                background: white;
                color: #718096;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-weight: bold;
                font-size: 10pt;
            }
            
            #cancelButton:hover {
                background: #f7fafc;
                border-color: #cbd5e0;
                color: #4a5568;
            }
            
            #cancelButton:pressed {
                background: #edf2f7;
            }
            
            #processButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 10pt;
            }
            
            #processButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #6a3f8f);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            
            #processButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a52b8, stop:1 #5a347a);
            }
            
            #processButton:disabled {
                background: #cbd5e0;
                color: #a0aec0;
            }
        """)
    
    def update_layer_list(self):
        """Atualizar lista de camadas poligonais"""
        self.layer_combo.clear()
        
        layers = QgsProject.instance().mapLayers().values()
        polygon_layers = [
            layer for layer in layers 
            if layer.type() == 0 and
            QgsWkbTypes.geometryType(layer.wkbType()) == QgsWkbTypes.PolygonGeometry
        ]
        
        if not polygon_layers:
            self.layer_combo.addItem("⚠️ Nenhuma camada encontrada", None)
        else:
            for layer in polygon_layers:
                self.layer_combo.addItem(f"📐 {layer.name()}", layer)
    
    def get_selected_layer(self):
        """Obter camada selecionada"""
        return self.layer_combo.currentData()
    
    def get_division_type(self):
        """Obter tipo de divisão"""
        # Buscar o radio button marcado dentro dos containers
        for btn_id in [1, 2]:
            btn = self.button_group.button(btn_id)
            if btn and btn.isChecked():
                return 'APP' if btn_id == 1 else 'RL'
        return 'RL'  # Default
    
    def show_progress(self, visible=True):
        """Mostrar/ocultar progresso"""
        self.progress_container.setVisible(visible)
        if visible:
            self.ok_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            self.layer_combo.setEnabled(False)
            for btn_id in [1, 2]:
                btn = self.button_group.button(btn_id)
                if btn:
                    btn.setEnabled(False)
        else:
            self.ok_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
            self.layer_combo.setEnabled(True)
            for btn_id in [1, 2]:
                btn = self.button_group.button(btn_id)
                if btn:
                    btn.setEnabled(True)
    
    def set_progress(self, value, status_text=""):
        """Definir progresso"""
        self.progress_bar.setValue(value)
        if status_text:
            self.status_label.setText(status_text)
