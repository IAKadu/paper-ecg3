"""Rotinas para converter imagens de derivações em sinais digitais.

Este módulo centraliza operações de detecção e extração, além de
funções de escalonamento e amostragem do sinal obtido.
"""

from typing import Callable
from ecgdigitize.image import BinaryImage, ColorImage
from .. import common

import numpy as np


def extractSignalFromImage(
    image: ColorImage,
    detectionMethod: Callable[[ColorImage], BinaryImage],
    extractionMethod: Callable[[BinaryImage], np.ndarray],
) -> np.ndarray:
    """Extrai o traçado de uma imagem colorida.

    Args:
        image: Imagem original da derivação.
        detectionMethod: Função que segmenta o traçado e retorna imagem binária.
        extractionMethod: Função que converte a imagem binária em vetor numérico.

    Returns:
        Vetor contendo o sinal digitalizado.
    """
    # O sistema de coordenadas das imagens possui origem no topo,
    # portanto o sinal resultante está espelhado verticalmente.
    signalBinary = detectionMethod(image)
    signal = extractionMethod(signalBinary)

    return signal


def verticallyScaleECGSignal(
    signal: np.ndarray,
    gridSizeInPixels: float,
    millimetersPerMilliVolt: float = 10.0,
    gridSizeInMillimeters: float = 1.0,
) -> np.ndarray:
    """Escala o sinal verticalmente para microvolts.

    Args:
        signal: Vetor do sinal extraído.
        gridSizeInPixels: Distância vertical entre linhas da grade em pixels.
        millimetersPerMilliVolt: Fator mm/mV (padrão 10 mm/mV).
        gridSizeInMillimeters: Tamanho da grade em milímetros (1 mm ou 5 mm).

    Returns:
        Sinal escalonado em microvolts.
    """
    gridsPerPixel = 1 / gridSizeInPixels
    millimetersPerGrid = gridSizeInMillimeters
    milliVoltsPerMillimeter = 1 / millimetersPerMilliVolt
    microVoltsPerMilliVolt = 1000
    microVoltsPerPixel = (
        gridsPerPixel * millimetersPerGrid * milliVoltsPerMillimeter * microVoltsPerMilliVolt
    )
    return signal * microVoltsPerPixel * -1  # Pixels têm origem no topo da imagem


def ecgSignalSamplingPeriod(
    gridSizeInPixels: float,
    millimetersPerSecond: float = 25.0,
    gridSizeInMillimeters: float = 1.0,
) -> float:
    """Calcula o período de amostragem do sinal em segundos por pixel."""
    gridsPerPixel = 1 / gridSizeInPixels
    millimetersPerGrid = gridSizeInMillimeters
    secondsPerMillimeter = 1 / millimetersPerSecond
    secondsPerPixel = gridsPerPixel * millimetersPerGrid * secondsPerMillimeter

    return secondsPerPixel


def zeroECGSignal(
    signal: np.ndarray,
    zeroingMethod: Callable[[np.ndarray], float] = common.mode,
) -> np.ndarray:
    """Centraliza o sinal subtraindo um valor de referência."""
    zeroPoint = zeroingMethod(signal)
    return signal - zeroPoint

