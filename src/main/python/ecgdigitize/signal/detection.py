"""ecgdigitize.signal.detection
================================

Rotinas responsáveis por converter uma imagem colorida do traçado em
uma máscara binária que represente apenas a curva do sinal.

Neste módulo estão implementados métodos de limiarização inspirados em
Mallawaarachchi et. al., 2014, além de utilitários para remover ruído e
detectar a presença da grade milimetrada.
"""
import cv2
import numpy as np

from .. import common, otsu, vision
from ..image import BinaryImage, ColorImage
from ..grid import frequency as grid_frequency


def otsuDetection(
    image: ColorImage, useBlur: bool = False, invert: bool = True
) -> BinaryImage:
    """Binariza a imagem utilizando o método de Otsu.

    Parameters
    ----------
    image:
        Imagem colorida contendo o traçado do ECG.
    useBlur:
        Quando ``True``, aplica um desfoque simples antes da binarização
        para reduzir ruídos.
    invert:
        Inverte o resultado final, útil quando o traçado está escuro
        sobre fundo claro.

    Returns
    -------
    BinaryImage
        Máscara binária com o traçado destacado.
    """

    # Citação do artigo: o método em escala de cinza preserva mais
    # informações em traçados antigos. Abordagens em CIE-LAB podem dar
    # melhor resultado em imagens mais novas (ainda não implementado).
    greyscaleImage = image.toGrayscale()

    # Opcionalmente aplica um blur para reduzir ruído (não descrito no artigo)
    if useBlur:
        blurredImage = vision.blur(greyscaleImage, kernelSize=3)
    else:
        blurredImage = greyscaleImage

    # Aplica limiarização automática de Otsu
    binaryImage = blurredImage.toBinary(inverse=invert)

    return binaryImage


def _denoise(
    image: BinaryImage,
    kernelSize: int = 3,
    erosions: int = 1,
    dilations: int = 1,
) -> BinaryImage:
    """Aplica operações morfológicas para remover ruído da máscara."""

    eroded = image.data

    # Erosão reduz regiões brancas isoladas
    for _ in range(erosions):
        eroded = cv2.erode(
            eroded,
            cv2.getStructuringElement(cv2.MORPH_CROSS, (kernelSize, kernelSize)),
        )

    dilated = eroded

    # Dilatação reconstrói o traçado após a erosão
    for _ in range(dilations):
        dilated = cv2.dilate(
            dilated,
            cv2.getStructuringElement(cv2.MORPH_DILATE, (kernelSize, kernelSize)),
        )

    return BinaryImage(dilated)


def _gridIsDetectable(image: BinaryImage) -> bool:
    """Verifica se a grade do papel milimetrado ainda é perceptível."""

    columnDensity = np.sum(image.data, axis=0)
    columnFrequencyStrengths = common.autocorrelation(columnDensity)
    columnFrequency = grid_frequency._estimateFirstPeakLocation(
        columnFrequencyStrengths,
        interpolate=False,
    )

    return columnFrequency is not None


def adaptive(image: ColorImage, applyDenoising: bool = False) -> BinaryImage:
    """Ajusta o limiar de Otsu até que a grade deixe de ser detectada."""

    # Fator de proteção que limita a variação do limiar
    maxHedge = 1.0
    minHedge = 0.6

    grayscaleImage = image.toGrayscale()
    otsuThreshold = otsu.otsuThreshold(grayscaleImage)

    hedging = float(maxHedge)
    binary = grayscaleImage.toBinary(otsuThreshold * hedging)

    # Reduz gradualmente o limiar até que a grade desapareça
    while _gridIsDetectable(binary):
        hedging -= 0.05  # TODO: escolher passo de forma mais inteligente
        if hedging < minHedge:
            break

        binary = grayscaleImage.toBinary(otsuThreshold * hedging)

    if applyDenoising:
        return _denoise(binary)
    else:
        return binary


