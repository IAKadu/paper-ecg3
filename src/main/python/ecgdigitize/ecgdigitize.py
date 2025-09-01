"""Rotinas de alto nível para digitalização de sinais e grades de ECG.

Este módulo reúne funções que coordenam diferentes etapas do processamento de
imagens: detecção de linhas de grade, extração do traçado do sinal e cálculo de
parâmetros relevantes. As docstrings descrevem a lógica empregada em cada
passo para auxiliar o entendimento do fluxo.
"""

from typing import Optional, Union
from dataclasses import dataclass
from enum import Enum

import numpy as np

from ecgdigitize.image import ColorImage
from . import common
from .grid import detection as grid_detection
from .grid import extraction as grid_extraction
from .signal import detection as signal_detection
from .signal.extraction import viterbi
from . import vision


def estimateRotationAngle(image: ColorImage, houghThresholdFraction: float = 0.25) -> Optional[float]:
    """Estima o ângulo de rotação da imagem a partir das linhas da grade."""

    # Converte a imagem colorida para binária destacando apenas pixels escuros
    binaryImage = grid_detection.thresholdApproach(image)

    # Define limiar do algoritmo de Hough proporcional à largura da imagem
    houghThreshold = int(image.width * houghThresholdFraction)
    lines = vision.houghLines(binaryImage, houghThreshold)

    # Converte cada linha detectada para um ângulo em graus
    angles = common.mapList(lines, vision.houghLineToAngle)
    # Normaliza ângulos para faixa de 0 a 90 graus
    offsets = common.mapList(angles, lambda angle: angle % 90)
    # Mantém apenas ângulos próximos a 0° ou 90°, prováveis linhas da grade
    candidates = common.filterList(offsets, lambda offset: abs(offset) < 30)

    if len(candidates) > 1:
        # Calcula média para suavizar pequenas variações
        estimatedAngle = common.mean(candidates)
        return estimatedAngle
    else:
        return None


class SignalDetectionMethod(Enum):
    """Opções de algoritmos para detecção do traçado do sinal."""

    default = "default"


class SignalExtractionMethod(Enum):
    """Métodos disponíveis para extração do sinal a partir da imagem binária."""

    default = "default"


def digitizeSignal(
    image: ColorImage,
    detectionMethod: SignalDetectionMethod = SignalDetectionMethod.default,
    extractionMethod: SignalExtractionMethod = SignalExtractionMethod.default
) -> Union[np.ndarray, common.Failure]:
    """Digitaliza o traçado do ECG presente na imagem fornecida."""

    # 1) Converte imagem colorida em binária, isolando os pixels do sinal
    if detectionMethod == SignalDetectionMethod.default:
        binary = signal_detection.adaptive(image)
    else:
        raise ValueError("Unrecognized SignalDetectionMethod in `digitizeSignal`")

    # 2) A partir da imagem binária, extrai-se a sequência de amplitudes
    if extractionMethod == SignalExtractionMethod.default:
        signal = viterbi.extractSignal(binary)
    else:
        raise ValueError("Unrecognized SignalExtractionMethod in `digitizeSignal`")

    return signal


class GridDetectionMethod(Enum):
    """Estratégias para localizar a grade de fundo do ECG."""

    default = "default"


class GridExtractionMethod(Enum):
    """Métodos para estimar o espaçamento da grade em pixels."""

    default = "default"


def digitizeGrid(
    image: ColorImage,
    detectionMethod: GridDetectionMethod = GridDetectionMethod.default,
    extractionMethod: GridExtractionMethod = GridExtractionMethod.default
) -> Union[float, common.Failure]:  # Returns size of grid in pixels
    """Estimativa do tamanho da grade de referência em pixels."""

    # 1) Converte a imagem colorida em binária com foco nos pixels da grade
    if detectionMethod == GridDetectionMethod.default:
        # Abordagem simples: considera todos os pixels não brancos como parte da grade
        binary = grid_detection.allDarkPixels(image)
    else:
        raise ValueError("Unrecognized GridDetectionMethod in `digitizeGrid`")

    # 2) Analisa a imagem binária para medir o período da grade
    if extractionMethod == GridExtractionMethod.default:
        gridPeriod = grid_extraction.estimateFrequencyViaAutocorrelation(binary.data)
    else:
        raise ValueError("Unrecognized GridExtractionMethod in `digitizeSignal`")

    return gridPeriod

