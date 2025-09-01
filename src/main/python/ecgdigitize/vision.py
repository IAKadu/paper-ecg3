"""Funções genéricas de processamento de imagem utilizadas pelo projeto.

O objetivo é concentrar aqui chamadas ao OpenCV e outras rotinas de visão
computacional para manter os módulos principais mais limpos.
"""
from ecgdigitize.image import BinaryImage, GrayscaleImage
import math
from typing import List, Tuple

import cv2
import numpy as np


def houghLines(binary: BinaryImage, threshold: int = 150) -> np.ndarray:
    """Executa a transformada de Hough retornando linhas detectadas."""

    output = cv2.HoughLines(binary.data, 1, np.pi / 180, threshold)

    if output is None:
        return np.array([])
    else:
        return np.squeeze(output, axis=1)


def getLinesInDirection(lines: np.ndarray, directionInDegrees: float) -> List[Tuple[float, float]]:
    """Filtra somente as linhas próximas a um ângulo específico."""

    return [
        (rho, theta)
        for rho, theta in lines
        if math.isclose(theta * 180 / math.pi, directionInDegrees, abs_tol=2)
    ]


def houghLineToAngle(line: Tuple[float, float]):
    """Converte uma linha no espaço de Hough para ângulo em graus."""

    rho, theta = line
    return theta * 180 / math.pi


def openImage(binaryImage: BinaryImage):
    """Aplica operação morfológica *opening* para remover ruídos pequenos."""

    element = cv2.getStructuringElement(cv2.MORPH_OPEN, (3, 3))
    eroded = cv2.erode(binaryImage.data, element)
    opened = cv2.dilate(eroded, element)

    return opened


def blur(image: GrayscaleImage, kernelSize: int = 2):
    """Aplica uma suavização gaussiana simples."""

    def guassianKernel(size):
        return np.ones((size, size), np.float32) / (size**2)

    blurred = cv2.filter2D(image.data, -1, guassianKernel(kernelSize))
    return GrayscaleImage(blurred)



