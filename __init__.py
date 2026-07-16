"""
PRA Divider Plugin
Inicializador do plugin para QGIS
"""

def classFactory(iface):
    """
    Carrega a classe PRADivider do arquivo pra_divider.py
    
    :param iface: Interface do QGIS (QgsInterface)
    """
    from .pra_divider import PRADivider
    return PRADivider(iface)
