"""
PRA Divider - Plugin QGIS para divisão de polígonos
Programa de Regularização Ambiental
"""

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import QgsProject
import os.path

from .pra_divider_dialog import PRADividerDialog
from .processing_algorithm import PRADividerAlgorithm


class PRADivider:
    """Plugin principal para divisão de APP e Reserva Legal"""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Inicializar locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PRADivider_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&PRA Divider')
        self.toolbar = self.iface.addToolBar(u'PRADivider')
        self.toolbar.setObjectName(u'PRADivider')
        
        self.dlg = None

    def tr(self, message):
        """Tradução"""
        return QCoreApplication.translate('PRADivider', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Criar interface do plugin"""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'PRA Divider - APP e Reserva Legal'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Remove o plugin"""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&PRA Divider'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        """Executar plugin"""
        if self.dlg is None:
            self.dlg = PRADividerDialog()
        
        # Atualizar lista de camadas poligonais
        self.dlg.update_layer_list()
        
        # Mostrar dialog
        result = self.dlg.exec_()
        
        if result:
            # Usuário clicou em OK
            self.process_division()
    
    def process_division(self):
        """Processar a divisão dos polígonos"""
        try:
            # Obter parâmetros do dialog
            layer = self.dlg.get_selected_layer()
            division_type = self.dlg.get_division_type()
            
            if not layer:
                QMessageBox.warning(
                    self.iface.mainWindow(),
                    "Aviso",
                    "Selecione uma camada válida!"
                )
                return
            
            # Executar algoritmo
            algorithm = PRADividerAlgorithm(self.iface, layer, division_type)
            success, message = algorithm.execute()
            
            if success:
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "Sucesso",
                    message
                )
            else:
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    "Erro",
                    message
                )
                
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Erro",
                f"Erro ao processar divisão: {str(e)}"
            )
