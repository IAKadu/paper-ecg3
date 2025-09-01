"""Detecção da grade milimetrada.

Este módulo contém utilitários que isolam a malha presente no papel
milimetrado a partir de uma imagem colorida. A grade é convertida em uma
máscara binária para que outros algoritmos possam ignorá-la ou medi-la.
"""

import cv2
import numpy as np

from ..image import BinaryImage, ColorImage
from .. import vision
from ..signal.detection import adaptive


def kernelApproach(colorImage: ColorImage) -> BinaryImage:
    """Identifica a grade aplicando operações morfológicas.

    A imagem é binarizada, suavizada com duas "openings" (erosão seguida
    de dilatação) para remover pequenos elementos e, em seguida, subtraída
    da versão original. A diferença evidencia as linhas da grade, que são
    erodidas levemente para afiná-las.

    Parameters
    ----------
    colorImage: ColorImage
        Imagem de entrada contendo o ECG colorido.

    Returns
    -------
    BinaryImage
        Máscara binária contendo apenas a grade identificada.
    """

    # Converte para escala de cinza e aplica um limiar alto para capturar
    # somente os pixels mais escuros.
    binaryImage = colorImage.toGrayscale().toBinary(threshold=240)

    opened: np.ndarray
    # Executa duas aberturas consecutivas para eliminar artefatos finos.
    opened = vision.openImage(binaryImage.data)
    opened = vision.openImage(opened)

    # Subtrai a imagem aberta da binária para ressaltar a grade.
    subtracted: np.ndarray = cv2.subtract(binaryImage.data, opened)

    # Faz uma erosão cruzada para afinar as linhas resultantes.
    final: np.ndarray = cv2.erode(
        subtracted,
        cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2)),
    )

    return BinaryImage(final)


def thresholdApproach(colorImage: ColorImage, erode: bool = False) -> BinaryImage:
    """Alternativa baseada em limiar adaptativo.

    Primeiro detecta todos os pixels escuros e depois remove o traçado do
    sinal do ECG, dilatando-o para garantir a subtração completa. Opcionalmente
    aplica uma erosão final para limpar ruídos residuais.
    """

    # Obtém todos os pixels escuros presentes na imagem.
    binaryImage = allDarkPixels(colorImage)

    # Extrai somente o sinal para podermos removê-lo da imagem binária.
    signalImage = adaptive(colorImage)

    dilatedSignal = cv2.dilate(
        signalImage.data,
        cv2.getStructuringElement(cv2.MORPH_DILATE, (5, 5)),
    )

    # Subtrai o sinal dilatado da imagem binária, restando apenas a grade.
    subtracted: np.ndarray = cv2.subtract(binaryImage.data, dilatedSignal)

    if erode:
        # Erosão opcional para remover pequenos resíduos.
        final = cv2.erode(
            subtracted,
            cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2)),
        )
        return BinaryImage(final)
    else:
        return BinaryImage(subtracted)


def allDarkPixels(colorImage: ColorImage, belowThreshold: int = 230) -> BinaryImage:
    """Cria máscara com todos os pixels mais escuros que um limiar.

    A imagem é convertida para tons de cinza e sua exposição é ajustada para
    que o valor mais frequente seja branco. Após essa normalização um
    limiar é aplicado, resultando em uma imagem binária com tudo que é
    potencialmente grade ou traçado do ECG.
    """

    grayscale = colorImage.toGrayscale()

    # Ajusta a exposição para normalizar diferentes tons do papel.
    adjusted = grayscale.whitePointAdjusted()

    # Converte para binário considerando apenas os tons abaixo do limiar.
    binary = adjusted.toBinary(belowThreshold)

    return binary

