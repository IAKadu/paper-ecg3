# Análise dos Códigos

Este documento descreve o propósito de cada arquivo Python presente no repositório.

## scripts/compare_ecg.py
Carrega um arquivo de ECG e exibe todos os canais disponíveis em gráficos separados.

## scripts/signal_loader.py
Lê arquivos de texto contendo valores de ECG, converte cada linha em números e retorna uma matriz com os canais.

## scripts/utility.py
Funções auxiliares para validação de números em formato de texto e para verificação de listas booleanas.

## src/main/icons/updateIcon.py
Gera automaticamente ícones em diversos tamanhos a partir de uma imagem base, incluindo um arquivo .ico.

## src/main/python/Main.py
Ponto de entrada da aplicação PyQt, inicializando o `ApplicationContext` e o controlador principal.

## src/main/python/controllers/MainController.py
Controla a janela principal: abertura e fechamento de imagens, processamento dos sinais e salvamento de anotações.

## src/main/python/model/InputParameters.py
Define os parâmetros de entrada usados na digitalização, como rotação, escalas e regiões de leads.

## src/main/python/model/EcgModel.py
Modelo simples que representa um ECG completo, armazenando leads e escalas padrão de grade.

## src/main/python/model/Lead.py
Enumeração e estrutura de dados para representar cada lead do ECG e sua posição na imagem.

## src/main/python/Annotation.py
Estruturas para salvar e carregar metadados de anotações feitas pelo usuário, incluindo cortes e escalas.

## src/main/python/QtWrapper.py
Conjunto de utilitários para facilitar a criação e o vínculo de widgets do Qt com classes Python.

## src/main/python/ImageUtilities.py
Funções de leitura de imagem e conversão entre formatos OpenCV e Qt.

## src/main/python/Conversion.py
Funções que recortam leads da imagem, digitizam sinais, estimam a grade e exportam os resultados em arquivo.

## src/main/python/ecgdigitize/__init__.py
Expõe funções principais do módulo `ecgdigitize`, como estimativa de rotação e digitalização de sinais e grade.

## src/main/python/ecgdigitize/common.py
Utilitários genéricos usados em todo o módulo, como operações matemáticas, filtros e manipulação de listas.

## src/main/python/ecgdigitize/ecgdigitize.py
Implementa o fluxo de digitalização: detecção e extração de sinais e da grade de fundo.

## src/main/python/ecgdigitize/otsu.py
Implementa o método de limiarização de Otsu e uma rotina de otimização simples.

## src/main/python/ecgdigitize/image.py
Abstrações para imagens coloridas, em tons de cinza e binárias, com operações de rotação, corte e conversão.

## src/main/python/ecgdigitize/vision.py
Funções de processamento de imagem baseadas em OpenCV, como Hough lines e filtros básicos.

## src/main/python/ecgdigitize/visualization.py
Rotinas para exibir imagens e sobrepor sinais ou linhas detectadas sobre imagens originais.

## src/main/python/ecgdigitize/signal/__init__.py
Reexporta funções relacionadas ao processamento de sinais de ECG.

## src/main/python/ecgdigitize/signal/detection.py
Converte uma imagem de lead em máscara binária do traçado, com métodos baseados em Otsu e heurísticas adaptativas.

## src/main/python/ecgdigitize/signal/extraction/__init__.py
Arquivo de inicialização vazio para o submódulo de extração de sinais.

## src/main/python/ecgdigitize/signal/extraction/extraction.py
Espaço reservado para estratégias de extração de sinais; atualmente contém apenas um cabeçalho.

## src/main/python/ecgdigitize/signal/extraction/naive.py
Extrai o sinal usando um método simples que encontra o centro das regiões ativas em cada coluna.

## src/main/python/ecgdigitize/signal/extraction/viterbi.py
Aplica uma versão do algoritmo de Viterbi para rastrear o caminho do traçado do sinal em uma imagem binária.

## src/main/python/ecgdigitize/signal/signal.py
Transforma imagens de leads em sinais numéricos e executa escalonamento e alinhamento temporal.

## src/main/python/ecgdigitize/grid/__init__.py
Arquivo de inicialização vazio para o submódulo de grade.

## src/main/python/ecgdigitize/grid/frequency.py
Estimativa da frequência da grade a partir de autocorrelação e interpolação de picos.

## src/main/python/ecgdigitize/grid/detection.py
Gera máscaras binárias da grade do papel usando limiarização e operações morfológicas.

## src/main/python/ecgdigitize/grid/extraction.py
Calcula o espaçamento da grade com base em análise de linhas e autocorrelação das densidades de pixels.

## src/main/python/views/MessageDialog.py
Janela de diálogo simples para exibir mensagens ao usuário com um botão OK.

## src/main/python/views/ExportFileDialog.py
Interface de exportação que permite escolher formato, delimitador e visualizar prévias dos leads digitalizados.

## src/main/python/views/MainWindow.py
Janela principal da aplicação, contendo menus, atalhos e integração com o editor de leads.

## src/main/python/views/ImagePreviewDialog.py
Exibe uma visualização de imagem recortada de um lead específico.

## src/main/python/views/ROIView.py
Implementa a área de seleção (ROI) com redimensionamento e movimentação para definir regiões de cada lead.

## src/main/python/views/EditPanelGlobalView.py
Painel com controles globais como rotação, escalas de tempo/voltagem e botões de processamento e salvamento.

## src/main/python/views/EditPanelLeadView.py
Painel para edição de um lead específico, permitindo ajustar o tempo inicial e excluir a ROI.

## src/main/python/views/ImageView.py
Componente de visualização de imagem com suporte a zoom, rotação, seleção de ROIs e atalhos.

## src/main/python/views/EditorWidget.py
Widget principal do editor que coordena a visualização da imagem, painéis de controle e gerenciamento das ROIs.

