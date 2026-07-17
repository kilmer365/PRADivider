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

            # Validar sistema de coordenadas UTM
            crs = layer.crs()
            if not crs.isValid():
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    "Erro - Sistema de Coordenadas",
                    "A camada não possui um sistema de coordenadas válido!"
                )
                return

            # Verificar se é UTM
            if not self.is_utm_crs(crs):
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    "Erro - Sistema de Coordenadas Inválido",
                    f"<b>Esta camada NÃO está em UTM!</b><br><br>"
                    f"Sistema atual: <b>{crs.authid()}</b> - {crs.description()}<br><br>"
                    f"<b>O plugin requer camadas em coordenadas UTM (projetadas).</b><br><br>"
                    f"Sistemas geográficos (latitude/longitude) não são aceitos.<br><br>"
                    f"<b>Solução:</b><br>"
                    f"1. Clique com botão direito na camada<br>"
                    f"2. Exportar > Salvar Feições Como...<br>"
                    f"3. Escolha um SRC UTM apropriado (ex: SIRGAS 2000 / UTM zone 22S)<br>"
                    f"4. Execute o plugin novamente com a camada reprojetada"
                )
                return

            # Mostrar barra de progresso
            self.dlg.show_progress(True)
            self.dlg.set_progress(10, "Validando geometrias...")

            # Executar algoritmo
            algorithm = PRADividerAlgorithm(self.iface, layer, division_type, self.dlg)
            self.dlg.set_progress(20, "Iniciando processamento...")

            success, message = algorithm.execute()

            self.dlg.set_progress(100, "Concluído!")
            self.dlg.show_progress(False)

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
            self.dlg.show_progress(False)
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Erro",
                f"Erro ao processar divisão: {str(e)}"
            )

    def is_utm_crs(self, crs):
        """Verificar se o sistema de coordenadas é UTM"""
        # Verificar se é projetado (não geográfico)
        if crs.isGeographic():
            return False

        # Verificar se contém "UTM" no nome ou descrição
        description = crs.description().upper()
        auth_id = crs.authid().upper()

        if "UTM" in description or "UTM" in auth_id:
            return True

        # Verificar códigos EPSG conhecidos de UTM (31001-33060 para WGS84/SIRGAS)
        if crs.authid().startswith("EPSG:"):
            try:
                epsg_code = int(crs.authid().split(":")[1])
            except (ValueError, IndexError):
                return False
            # EPSG para UTM WGS84: 32601-32660 (Norte) e 32701-32760 (Sul)
            # EPSG para UTM SIRGAS 2000: 31965-31985
            if (32601 <= epsg_code <= 32660 or
                32701 <= epsg_code <= 32760 or
                31965 <= epsg_code <= 31985):
                return True

        return False
