# PRA Divider

Plugin para QGIS que divide automaticamente polígonos em partes iguais para o **Programa de Regularização Ambiental (PRA)**: áreas de **APP** em 5 partes e áreas de **Reserva Legal** em 10 partes.

## Funcionalidades

- Divisão automática de APP (5 partes) e Reserva Legal (10 partes)
- Algoritmo de divisão por faixas com busca binária para equalizar as áreas
- Validação de sistema de coordenadas (exige CRS projetado em UTM)
- Interface gráfica com barra de progresso
- Camada de saída com atributos de área (ha), percentual e tipo

## Requisitos

- QGIS 3.0 ou superior
- Camada vetorial poligonal em sistema de coordenadas UTM (projetado)
- Geometrias válidas

## Instalação

1. Copie a pasta `PRADivider` para o diretório de plugins do QGIS:
   - Windows: `C:\Users\<usuário>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
2. Reinicie o QGIS.
3. Ative o plugin em **Complementos > Gerenciar e Instalar Complementos**.

## Uso

1. Abra o plugin em **Vetor > PRA Divider > PRA Divider - APP e Reserva Legal**.
2. Selecione a camada poligonal desejada (deve estar em UTM).
3. Escolha o tipo de divisão: **APP** (5 partes) ou **Reserva Legal** (10 partes).
4. Clique em **Processar**.
5. Uma nova camada será criada no projeto com as partes divididas e seus atributos.

## Estrutura do projeto

```
PRADivider/
├── __init__.py              # Ponto de entrada do plugin (classFactory)
├── pra_divider.py           # Classe principal do plugin (carregada pelo __init__.py)
├── pra_divider_dialog.py    # Interface gráfica (QDialog)
├── processing_algorithm.py  # Algoritmo de divisão de polígonos
├── metadata.txt             # Metadados do plugin (QGIS)
└── icon.png                 # Ícone do plugin
```

## Autor

Davi Kilmer

## Licença

Este projeto está licenciado sob a licença MIT — veja o arquivo [LICENSE](LICENSE) para detalhes.
