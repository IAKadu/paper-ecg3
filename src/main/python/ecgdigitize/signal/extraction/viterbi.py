"""
Implementa a extração do traçado utilizando o algoritmo de Viterbi.

O objetivo é percorrer a imagem binária do ECG e encontrar, para cada
coluna, o ponto que melhor representa o sinal, minimizando um custo que
leva em conta distância e continuidade angular entre os pontos.
"""
from collections import defaultdict
from functools import partial

from dataclasses import dataclass
from ecgdigitize import signal
from math import isnan, sqrt, asin, pi
from typing import Dict, Iterable, Iterator, List, Optional, Tuple, Union

import numpy as np

from ... import common
from ...common import Numeric
from ...image import BinaryImage


@dataclass(frozen=True)
class Point:
    """Representa um ponto ``(x, y)`` na imagem do ECG."""

    x: Numeric
    y: Numeric

    @property
    def index(self) -> int:
        """Retorna a coordenada *x* arredondada para inteiro."""
        if isinstance(self.x, int):
            return self.x
        else:
            return round(self.x)

    @property
    def values(self) -> Tuple[Numeric, Numeric]:
        """Facilita a extração do par ``(x, y)``."""
        return (self.x, self.y)


def findContiguousRegions(oneDimImage: np.ndarray) -> Iterable[Tuple[int, int]]:
    """Encontra faixas contíguas de pixels ativos em uma linha.

    Exemplo de entrada:
        ``|---###--#-----#####|``  (# indica pixel ligado)
        ``|0123456789...      |``
    Retorna ``[(3,5), (8,8), (14,18)]`` correspondendo aos intervalos.
    """
    locations = []
    start = None
    for index, pixel in enumerate(oneDimImage):
        # Detecta início de um novo segmento de pixels não nulos
        if pixel > 0 and start is None:
            start = index
        # Finaliza o segmento atual ao encontrar um pixel zero
        elif pixel == 0 and start is not None:
            locations.append((start, index))
            start = None

    return locations


def findContiguousRegionCenters(oneDimImage: np.ndarray) -> Iterable[int]:
    """Obtém o centro de cada região contígua identificada.

    Retorna a média dos índices de início e fim de cada segmento,
    arredondada para baixo.
    """
    return [int(np.mean(list(locationPair))) for locationPair in findContiguousRegions(oneDimImage)]


def euclideanDistance(x: Numeric, y: Numeric) -> float:
    """Calcula a distância euclidiana para os deslocamentos ``x`` e ``y``."""
    return sqrt((x**2) + (y**2))


def distanceBetweenPoints(firstPoint: Point, secondPoint: Point) -> float:
    """Distância euclidiana entre dois pontos do traçado."""
    return euclideanDistance(firstPoint.x - secondPoint.x, firstPoint.y - secondPoint.y)


def angleFromOffsets(x: Numeric, y: Numeric) -> float:
    """Calcula o ângulo formado pelos deslocamentos ``x`` e ``y`` em graus."""
    return asin(y / euclideanDistance(x, y)) / pi * 180


def angleBetweenPoints(firstPoint: Point, secondPoint: Point) -> float:
    """Retorna o ângulo entre dois pontos em relação ao eixo *x*."""
    deltaX = secondPoint.x - firstPoint.x
    deltaY = secondPoint.y - firstPoint.y
    return angleFromOffsets(deltaX, deltaY)


def angleSimilarity(firstAngle: float, secondAngle: float) -> float:
    """Mede quão próximos são dois ângulos, retornando valor entre 0 e 1."""
    return (180 - abs(secondAngle - firstAngle)) / 180


def searchArea(initialRow: int, radius: int) -> Iterable[Tuple[int, int]]:
    """Gera intervalos de linhas que compõem a janela de busca.

    A partir de uma linha inicial e de um raio, calcula o quanto podemos
    subir ou descer em cada coluna à direita, formando um semicírculo.
    """
    area = []
    for column in range(1, radius + 1):
        verticalOffset = 0
        # Aumenta o deslocamento vertical enquanto o ponto estiver dentro do raio
        while euclideanDistance(column, verticalOffset + 1) <= float(radius):
            verticalOffset += 1
        area.append((initialRow - verticalOffset, initialRow + verticalOffset))

    return area


def getPointLocations(image: np.ndarray) -> List[List[Point]]:
    """Obtém os pontos candidatos do traçado para cada coluna da imagem."""
    columns = np.swapaxes(image, 0, 1)
    pointLocations = []

    # Varre horizontalmente a imagem
    for column, pixels in enumerate(columns):
        # Calcula o centro de cada grupo de pixels ligados
        rows = findContiguousRegionCenters(pixels)
        points = common.mapList(rows, lambda row: Point(column, row))

        pointLocations.append(points)

    return pointLocations


# TODO: Fazer a pontuação multiplicar ou normalizar pelo tamanho do caminho
def score(currentPoint: Point, candidatePoint: Point, candidateAngle: float) -> float:
    """Calcula o custo de ir do ponto atual para um candidato."""
    DISTANCE_WEIGHT = .5

    currentAngle = angleBetweenPoints(candidatePoint, currentPoint)
    angleValue = 1 - angleSimilarity(currentAngle, candidateAngle)
    distanceValue = distanceBetweenPoints(currentPoint, candidatePoint)

    # Combina distância e ângulo em uma única métrica de custo
    return (distanceValue * DISTANCE_WEIGHT) + (angleValue * (1 - DISTANCE_WEIGHT))


def getAdjacent(pointsByColumn, bestPathToPoint, startingColumn: int, minimumLookBack: int):
    """Obtém pontos já processados dentro de uma janela à esquerda."""
    rightColumnIndex = startingColumn
    leftColumnIndex = int(common.lowerClamp(startingColumn - minimumLookBack, 0))

    result = list(common.flatten(pointsByColumn[leftColumnIndex:rightColumnIndex]))

    # Se não houver pontos nesta janela, expandimos para a esquerda
    while len(result) == 0 and leftColumnIndex >= 0:
        leftColumnIndex -= 1
        result = list(common.flatten(pointsByColumn[leftColumnIndex:rightColumnIndex]))  # TODO: Tornar esta busca mais eficiente?

    for point in result:
        assert point in bestPathToPoint, "Ponto encontrado antes de ser registrado"
        pointScore, _, pointAngle = bestPathToPoint[point]
        yield pointScore, point, pointAngle


def interpolate(fromPoint: Point, toPoint: Point) -> Iterator[Point]:
    """Interpola linearmente entre dois pontos."""
    slope = (toPoint.y - fromPoint.y) / (toPoint.x - fromPoint.x)
    f = lambda x: slope * (x - toPoint.x) + toPoint.y

    for x in range(fromPoint.index + 1, toPoint.index):
        yield Point(x, f(x))


def convertPointsToSignal(points: List[Point], width: Optional[int] = None) -> np.ndarray:
    """Converte uma lista de pontos em um vetor que representa o sinal."""
    assert len(points) > 0

    firstPoint = points[0]  # Ponto mais distante do eixo y
    # Último ponto também está disponível como `points[-1]`, mas não é necessário aqui

    arraySize = width or (firstPoint.x + 1)
    signal = np.full(arraySize, np.nan, dtype=float)

    signal[firstPoint.index] = firstPoint.y
    priorPoint = firstPoint

    for point in points[1:]:
        # Preenche lacunas entre pontos consecutivos usando interpolação
        if isnan(signal[point.index + 1]):
            for interpolatedPoint in interpolate(point, priorPoint):
                signal[interpolatedPoint.index] = interpolatedPoint.y

        signal[point.index] = point.y
        priorPoint = point

    return signal


def extractSignal(binary: BinaryImage) -> Optional[np.ndarray]:
    """Extrai o traçado de uma imagem binária usando Viterbi."""
    pointsByColumn = getPointLocations(binary.data)
    points = list(common.flatten(pointsByColumn))

    if len(points) == 0:
        return None

    minimumLookBack = 1

    bestPathToPoint: Dict[Point, Tuple[float, Optional[Point], float]] = {}

    # TODO: Permitir maior tolerância inicial antes de iniciar o algoritmo

    # Inicializa tabela de programação dinâmica com casos base (extremo esquerdo)
    # TODO: Isto é realmente necessário? Sem ele, `getAdjacent` falha.
    for column in pointsByColumn[:1]:
        for point in column:
            bestPathToPoint[point] = (0, None, 0)

    # Constrói a tabela coluna por coluna
    for column in pointsByColumn[1:]:
        for point in column:
            # Reúne pontos à esquerda dentro da área de busca
            adjacent = list(getAdjacent(pointsByColumn, bestPathToPoint, point.index, minimumLookBack))

            if len(adjacent) == 0:
                print(f"Nenhum adjacente a {point}")
                bestPathToPoint[point] = (0, None, 0)
            else:
                bestScore: float
                bestPoint: Point
                bestScore, bestPoint = min(
                    [
                        (score(point, candidatePoint, candidateAngle) + cadidateScore, candidatePoint)
                        for cadidateScore, candidatePoint, candidateAngle in adjacent
                    ],
                    key=lambda triplet: triplet[0],  # Minimiza apenas pelo custo
                )
                bestPathToPoint[point] = (
                    bestScore,
                    bestPoint,
                    angleBetweenPoints(bestPoint, point),
                )

    # Busca retroativa para encontrar o melhor caminho a partir da borda direita
    OPTIMAL_ENDING_WIDTH = 20
    optimalCandidates = list(
        getAdjacent(
            pointsByColumn,
            bestPathToPoint,
            startingColumn=binary.width,
            minimumLookBack=OPTIMAL_ENDING_WIDTH,
        )
    )

    _, current = min(
        [(totalScore, point) for totalScore, point, _ in optimalCandidates],
        key=lambda pair: pair[0],
    )

    bestPath = []

    while current is not None:
        bestPath.append(current)
        _, current, _ = bestPathToPoint[current]

    signal = convertPointsToSignal(bestPath)  # , width=binary.width)

    return signal
