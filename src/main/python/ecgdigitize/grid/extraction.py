"""Extração de informações da grade do papel milimetrado.

As funções deste módulo analisam imagens binárias para estimar a
distância entre linhas da grade e a frequência espacial, etapas
importantes para a digitalização do ECG.
"""

from typing import List, Optional, Union

import numpy as np

from . import frequency as grid_frequency
from .. import common
from .. import vision
from ..image import BinaryImage


def traceGridlines(binaryImage: BinaryImage, houghThreshold: int = 80) -> Optional[float]:
    """Estimativa da distância entre linhas da grade.

    Usa a Transformada de Hough para detectar linhas verticais e
    horizontais no papel e calcula a moda das distâncias entre elas. O
    menor espaçamento encontrado corresponde ao espaçamento da grade.
    """

    # Detecta todas as linhas fortes na imagem binária.
    lines = vision.houghLines(binaryImage, houghThreshold)

    # Função interna que calcula as distâncias entre linhas com a mesma
    # orientação (0º para horizontais e 90º para verticais).
    def getDistancesBetween(lines: List[int], inDirection: float = 0) -> List[float]:
        orientedLines = sorted(vision.getLinesInDirection(lines, inDirection))
        return common.calculateDistancesBetweenValues(orientedLines)

    verticalDistances = getDistancesBetween(lines=lines, inDirection=90)
    horizontalDistances = getDistancesBetween(lines=lines, inDirection=0)

    verticalGridSpacing = common.mode(verticalDistances) if len(verticalDistances) > 0 else None
    horizontalGridSpacing = common.mode(horizontalDistances) if len(horizontalDistances) > 0 else None

    if verticalGridSpacing is None:
        return horizontalGridSpacing
    elif horizontalGridSpacing is None:
        return verticalGridSpacing
    else:
        # Retorna o menor espaçamento, que normalmente corresponde aos
        # quadrículos menores do papel.
        return min([verticalGridSpacing, horizontalGridSpacing])

    # TODO: Usar mediana em vez de moda?
    # TODO: Tentar algum tipo de clusterização para ignorar espaçamentos fora do padrão.


def estimateFrequencyViaAutocorrelation(binaryImage: np.ndarray) -> Union[float, common.Failure]:
    """Calcula a frequência da grade via autocorrelação.

    A densidade de pixels em cada linha e coluna é autocorrelacionada para
    encontrar picos periódicos. O primeiro pico após zero indica a
    frequência (número de pixels entre linhas) da grade.
    """

    # TODO: Verificar se a imagem fornecida é binária.

    columnDensity = np.sum(binaryImage, axis=0)
    rowDensity = np.sum(binaryImage, axis=1)

    columnFrequencyStrengths = common.autocorrelation(columnDensity)
    rowFrequencyStrengths = common.autocorrelation(rowDensity)

    columnFrequency = grid_frequency._estimateFirstPeakLocation(columnFrequencyStrengths)
    rowFrequency = grid_frequency._estimateFirstPeakLocation(rowFrequencyStrengths)

    if columnFrequency and rowFrequency:
        # Caso tenhamos frequências em ambos os eixos, preferimos a
        # estimativa das colunas (outras estratégias podem ser avaliadas).
        return columnFrequency
    elif rowFrequency:
        return rowFrequency
    elif columnFrequency:
        return columnFrequency
    else:
        return common.Failure(
            "Unable to estimate the frequency of the grid in either directions."
        )



