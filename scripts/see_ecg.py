"""Exibe graficamente todos os leads de um arquivo de ECG.

O script lê um arquivo contendo sinais de ECG e cria um gráfico separado
para cada lead disponível no registro.
"""

import os
import sys
import matplotlib.pyplot as plt

import signal_loader


# Verificação de sistema para evitar problemas em plataformas não POSIX.
if os.name != "posix":
    print("Julian não entende Windows :( desculpe")

# É necessário pelo menos um argumento: o caminho do arquivo de ECG.
if len(sys.argv) < 2:
    print("Erro!")
    print(f"Uso: python {sys.argv[0]} ARQUIVO_ECG")
    exit(1)

file = sys.argv[1]

# Carrega a matriz de leads; cada linha corresponde a um canal do ECG.
leads = signal_loader.load(file)

# `leads` possui formato (n_leads, duração). Extraímos a quantidade de leads
# e o número de amostras para compor o eixo do tempo.
leadCount, duration = leads.shape
times = list(range(duration))

plotNumber = 0

# Cria um gráfico para cada lead do ECG.
fig, ax = plt.subplots(nrows=leadCount, ncols=1)
for row in ax:
    # Plota o lead correspondente ao gráfico atual.
    row.plot(times, leads[plotNumber])
    plotNumber += 1

# Exibe os gráficos.
plt.show()

