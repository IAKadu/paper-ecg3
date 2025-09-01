"""Carrega sinais de ECG a partir de arquivos de texto.

Cada linha do arquivo de entrada representa um instante de tempo e contém
os valores dos leads separados por tabulação, vírgula ou espaço.
"""

import numpy as np
from utility import allTrue, isFloat


# Classe deixada como referência futura para estrutura de dados de sinais.
class SignalData:
    I = None
    II = None
    III = None
    aVR = None
    aVL = None
    aVF = None

    V1 = None
    V2 = None
    V4 = None
    V3 = None
    V5 = None
    V6 = None


def leadValues(text: str, conversion) -> list | None:
    """Converte uma linha de texto em uma lista de valores numéricos.

    A linha pode estar separada por tabulações, vírgulas ou espaços. Caso
    algum dos elementos não seja um número válido, `None` é retornado.
    """

    # Identifica o separador utilizado na linha.
    if "\t" in text:
        words = text.split("\t")
    elif "," in text:
        words = text.split(",")
    else:
        words = text.split(" ")

    # Verifica se todos os campos podem ser interpretados como números.
    areFloats = list(map(isFloat, words))

    if not allTrue(areFloats):
        print("Nem todos são números:", words)
        return None

    # Converte os valores para o tipo desejado.
    values = list(map(conversion, words))
    return values


def load(fileName: str) -> np.ndarray:
    """Lê um arquivo de sinais e retorna um array NumPy organizado por lead."""

    values = []

    # Percorre cada linha do arquivo e converte para valores numéricos.
    with open(fileName, "r") as file:
        for line in file.readlines():
            text = line.strip()
            # TODO: ver se a conversão para float é sempre adequada
            valuesAtTime = leadValues(text, float)

            if valuesAtTime is not None:
                values.append(valuesAtTime)

    # Transpõe a matriz para obter formato (n_leads, duração).
    leads = np.swapaxes(np.array(values), 0, 1)

    print("Leads carregados:", leads.shape)

    return leads

