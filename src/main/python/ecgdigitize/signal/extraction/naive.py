"""
Implementa um método ingênuo de extração do traçado de um ECG.

A rotina percorre cada coluna da imagem binarizada do traçado e calcula
o ponto médio entre o primeiro e o último pixels não nulos encontrados,
simulando um "centro de massa" do sinal.
"""
from typing import Iterator, Optional, Tuple
import numpy as np

from ... import common


def findFirstLastNonZeroPixels(oneDimImage: np.ndarray) -> Tuple[Optional[int], Optional[int]]:
    """Retorna a primeira e a última posição de pixel diferente de zero.

    A função recebe um vetor unidimensional, normalmente representando uma
    coluna da imagem binária, e identifica onde o traçado do sinal começa
    e termina na vertical.
    """

    def reverseEnumerate(array: np.ndarray) -> Iterator[Tuple[int, int]]:
        """Percorre o array de trás para frente sem criar uma cópia.

        Utilizamos ``reversedRange`` para economizar memória e ganhar
        desempenho ao evitar a inversão explícita do vetor.
        """
        for index in common.reversedRange(len(array)):
            yield index, array[index]

    def findFirstNonZero(oneDimImage: np.ndarray, reversed: bool = False) -> Optional[int]:
        """Localiza o primeiro índice com valor diferente de zero.

        Args:
            oneDimImage: Coluna da imagem a ser percorrida.
            reversed: Quando ``True``, a busca é feita de baixo para cima.

        Returns:
            O índice do primeiro pixel válido ou ``None`` se não houver.
        """
        iterator = reverseEnumerate(oneDimImage) if reversed else enumerate(oneDimImage)
        for index, pixel in iterator:
            if pixel > 0:
                return index

        return None

    # Busca o primeiro pixel acima e abaixo para delimitar o traçado
    top = findFirstNonZero(oneDimImage)
    bottom = findFirstNonZero(oneDimImage, reversed=True)
    return top, bottom


def extract(image: np.ndarray) -> np.ndarray:
    """Extrai um vetor com a posição vertical do traçado em cada coluna.

    Percorre a imagem coluna a coluna, identifica a parte superior e
    inferior do traçado e calcula o ponto médio entre eles, assumindo que
    o sinal é fino e contínuo.
    """
    # Transpõe a matriz para iterar facilmente sobre as colunas
    columns = np.swapaxes(image, 0, 1)
    output = np.zeros(len(columns))

    for index, column in enumerate(columns):
        # Determina os limites do traçado na coluna atual
        top, bottom = findFirstLastNonZeroPixels(column)

        if top is not None and bottom is not None:
            # Calcula o ponto médio entre o topo e a base encontrados
            output[index] = (top + bottom) / 2

    return output
