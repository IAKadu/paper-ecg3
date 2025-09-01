"""ecgdigitize.visualization
=================================

Ferramentas simples para visualização de imagens utilizadas no
processo de digitalização do eletrocardiograma.

O módulo contém funções auxiliares que usam ``matplotlib`` e ``opencv``
para exibir imagens coloridas ou em tons de cinza, além de rotinas para
sobrepor linhas e sinais digitalizados na imagem original.
"""
import math
from typing import List, Optional, Sequence, Tuple, Union

import cv2
import numpy as np
from numpy.lib.arraysetops import isin

from . import common
from .image import Image, ColorImage, GrayscaleImage, BinaryImage


class Color:
    """Enumeração simples para indicar o tipo de cor esperado."""

    # Indica que a imagem está em tons de cinza (apenas um canal)
    greyscale = 0
    # Indica que a imagem está no espaço de cor BGR utilizado pelo OpenCV
    BGR = 1

def displayImage(image: Image, title: str = "") -> None:
    """Exibe uma imagem utilizando ``matplotlib``.

    A função detecta automaticamente se o objeto é uma imagem colorida
    ou em tons de cinza e ajusta a coloração de acordo.
    """

    import matplotlib.pyplot as plt

    if isinstance(image, ColorImage):
        # Para imagens coloridas basta repassar os dados diretamente
        displayImage = image
        plt.imshow(displayImage.data)
    elif isinstance(image, (GrayscaleImage, BinaryImage)):
        # Converte para RGB e define o ``cmap`` para escala de cinza
        displayImage = image.toColor()
        plt.imshow(displayImage.data, cmap="gray")

    # Remove marcações dos eixos para facilitar a visualização
    plt.xticks([])
    plt.yticks([])
    plt.title(title)
    plt.show()


def overlayLines(lines: Union[List, np.ndarray], colorImage: ColorImage) -> ColorImage:
    """Sobrepõe linhas detectadas sobre uma imagem colorida.

    ``lines`` deve ser uma coleção de pares ``(rho, theta)`` no formato
    retornado pela Transformada de Hough do OpenCV. Cada linha é desenhada
    sobre uma cópia da imagem original.
    """

    newImage = colorImage.data.copy()

    for rho, theta in lines:
        # Converte a representação polar (rho, theta) para dois pontos
        # distantes na imagem, garantindo que a linha cruzará todo o quadro
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 10000 * (-b))
        y1 = int(y0 + 10000 * (a))
        x2 = int(x0 - 10000 * (-b))
        y2 = int(y0 - 10000 * (a))

        # Desenha a linha na cor roxa padrão utilizada pelo projeto
        cv2.line(newImage, (x1, y1), (x2, y2), (85, 19, 248))

    return ColorImage(newImage)


def displayImages(listOfImages: Sequence[Image]) -> None:
    """Exibe uma lista de imagens lado a lado.

    A implementação foi deixada como *stub* para uso futuro; o código
    comentado serve como referência de como organizar múltiplas imagens em
    um grid utilizando ``matplotlib``.
    """

    pass


def overlaySignalOnImage(
    signal: np.ndarray,
    image: ColorImage,
    color: Tuple[np.uint8, np.uint8, np.uint8] = (85, 19, 248),
    lineWidth: int = 3
) -> ColorImage:
    """Desenha um sinal unidimensional sobre a imagem do traçado.

    Parameters
    ----------
    signal:
        Vetor contendo as amplitudes do sinal já nas coordenadas da imagem.
        Valores ``NaN`` representam trechos ausentes e não são desenhados.
    image:
        Imagem colorida que receberá o sinal.
    color:
        Tupla BGR com a cor da linha a ser desenhada.
    lineWidth:
        Espessura do traço que representa o sinal.
    """

    assert len(signal.shape) == 1
    assert isinstance(image, ColorImage)

    def quantize(element: np.float) -> Optional[int]:
        """Converte valores do sinal para inteiros, ignorando ``NaN``."""

        if not np.isnan(element):
            return int(element)
        else:
            return None

    output = image.data.copy()
    quantizedSignal = common.mapList(signal, quantize)

    # Desenha segmentos apenas quando dois pontos consecutivos são válidos
    for first, second in zip(
        enumerate(quantizedSignal[:-1]),
        enumerate(quantizedSignal[1:], start=1),
    ):
        if first[1] is not None and second[1] is not None:
            cv2.line(output, first, second, color, thickness=lineWidth)

    return ColorImage(output)

