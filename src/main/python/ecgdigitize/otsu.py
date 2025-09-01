"""Rotinas de otimização utilizadas pelo algoritmo de Otsu.

O foco deste módulo é fornecer funções auxiliares para encontrar limiares que
separam regiões claras e escuras em uma imagem em escala de cinza.
"""

from typing import Callable, List, Optional, Tuple, Union

from ecgdigitize.image import GrayscaleImage


def otsuThreshold(image: GrayscaleImage) -> float:
    """Calcula o limiar ótimo segundo o método de Otsu.

    Referência: *A Threshold Selection Method from Gray-Level Histograms*
    - Nobuyuki Otsu (1979).
    """

    assert isinstance(image, GrayscaleImage)

    L = 256  # Número de tons possíveis em uma imagem de 8 bits
    height, width = image.data.shape
    N = height * width  # Quantidade total de pixels
    n = image.histogram()  # Contagem de pixels para cada valor de cinza
    p = n / N  # Probabilidade de ocorrência de cada nível

    def ω(k: int) -> float:
        """Probabilidade acumulada até o nível ``k``."""

        return sum(p[0:k])

    def μ(k: int) -> float:
        """Média ponderada dos níveis de cinza até ``k``."""

        return sum([(i + 1) * p_i for i, p_i in enumerate(p[0:k])])

    μ_T = μ(L)  # Média global da imagem

    def σ_B(k: int) -> float:  # σ²_B - variância entre classes
        numerator = (μ_T * ω(k) - μ(k)) ** 2
        denominator = ω(k) * (1 - ω(k))
        return numerator / denominator

    # Procura o valor de k que maximiza a separação entre classes
    k = climb1dHill(list(range(L)), σ_B)

    return k


def climb1dHill(xs: List[int], evaluate: Callable[[int], Union[float, int]]) -> int:
    """Busca o valor que maximiza ``evaluate`` em uma lista ordenada.

    Percorre a lista em forma de "subida de morro": a cada passo avalia os
    vizinhos à esquerda e à direita e avança na direção que apresentar maior
    pontuação. A função ``evaluate`` deve retornar um escore numérico para
    cada posição ``x``.
    """

    evaluations = {}

    def cachedEvaluate(index: int) -> float:
        """Memoriza avaliações já realizadas para evitar recálculos."""

        if index not in evaluations:
            evaluations[index] = evaluate(index)
        return evaluations[index]

    def neighbors(index: int) -> Tuple[Optional[int], Optional[int]]:
        """Retorna os índices vizinhos imediato de ``index``."""

        left, right = None, None
        if index > 0:
            left = index - 1
        if index < len(xs) - 1:
            right = index + 1
        return (left, right)

    startIndex = len(xs) // 2
    currentIndex, currentScore = startIndex, cachedEvaluate(xs[startIndex])

    while True:
        left, right = neighbors(currentIndex)
        if left is None or right is None:
            # TODO: tratar bordas com mais cuidado
            raise NotImplementedError

        leftScore, rightScore = cachedEvaluate(xs[left]), cachedEvaluate(xs[right])

        # Se mover para a esquerda melhora, siga nessa direção
        if left is not None and leftScore > currentScore:
            currentIndex, currentScore = left, leftScore
            continue

        # Se mover para a direita melhora, siga para lá
        if right is not None and rightScore > currentScore:
            currentIndex, currentScore = right, rightScore
            continue

        # Se nenhuma direção melhora, encontramos o pico local
        return xs[currentIndex]
