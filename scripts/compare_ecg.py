"""Compara graficamente dois arquivos de sinais de ECG.

O script recebe dois caminhos de arquivos contendo sinais de ECG e plota
cada par de leads lado a lado para facilitar a comparação visual.
"""

import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

import signal_loader


# Verificação simples de sistema operacional para evitar problemas com links
# simbólicos em ambientes não POSIX.
if os.name != "posix":
    print("Julian não entende links do Windows :( desculpe")

# Garante que dois argumentos (arquivos de ECG) foram fornecidos.
if len(sys.argv) < 3:
    print("Erro! Poucos argumentos")
    exit(1)

# Converte os argumentos em objetos Path para facilitar a manipulação de
# caminhos de arquivo.
firstPath = Path(sys.argv[1])
secondPath = Path(sys.argv[2])

# Confirma que ambos os arquivos existem antes de prosseguir.
assert firstPath.exists(), f"{firstPath} não foi encontrado!"
assert secondPath.exists(), f"{secondPath} não foi encontrado!"

# Carrega os dados de cada ECG; o resultado é uma matriz onde cada linha
# representa um lead.
firstECG = signal_loader.load(firstPath)
secondECG = signal_loader.load(secondPath)

# Determina quantos leads podem ser comparados (o menor número entre os dois
# arquivos).
numberOfComparisons = min(len(firstECG), len(secondECG))

# Cria uma figura com um gráfico para cada par de leads.
fig, ax = plt.subplots(nrows=numberOfComparisons, ncols=1)
for index, row in enumerate(ax if isinstance(ax, (list, np.ndarray)) else [ax]):
    # Plota os dois sinais no mesmo gráfico para inspeção visual.
    row.plot(firstECG[index])
    row.plot(secondECG[index])

# Exibe todos os gráficos na tela.
plt.show()

