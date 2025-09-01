"""Funções auxiliares para manipulação de imagens com OpenCV e Qt."""
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
from PyQt5 import QtGui
import scipy.stats as stats


def readImage(path: Path) -> np.ndarray:
    """Lê uma imagem do disco utilizando OpenCV."""

    return cv2.imread(str(path.absolute()))


def opencvImageToPixmap(image: np.ndarray) -> QtGui.QPixmap:
    """Converte uma matriz do OpenCV para ``QPixmap``.

    A rotina foi adaptada de um exemplo disponível na internet (ver link
    abaixo) e é útil para exibir imagens carregadas pelo OpenCV em widgets do
    Qt.
    """
    # Fonte: https://stackoverflow.com/a/50800745/7737644 (Creative Commons)

    height, width, channel = image.shape
    bytesPerLine = 3 * width

    pixmap = QtGui.QPixmap(
        QtGui.QImage(
            image.data,
            width,
            height,
            bytesPerLine,
            QtGui.QImage.Format_RGB888
        ).rgbSwapped()
    )

    return pixmap

