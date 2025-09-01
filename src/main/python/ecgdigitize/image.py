"""Estruturas leves para representar imagens e operações auxiliares.

Reúne classes simples baseadas em ``dataclasses`` que encapsulam dados de
imagens em cores, tons de cinza ou binárias, além de funções de E/S e
transformações comuns como recorte e rotação.
"""

from pathlib import Path
from typing import Optional, Tuple, Union
import dataclasses

import cv2
import numpy as np
from numpy.lib.arraysetops import isin
import scipy.stats as stats


@dataclasses.dataclass(frozen=True)
class Image:
    """Classe base contendo apenas a matriz de pixels."""

    data: np.ndarray

    @property
    def height(self):
        """Altura da imagem em pixels."""

        return self.data.shape[0]

    @property
    def width(self):
        """Largura da imagem em pixels."""

        return self.data.shape[1]


class ColorImage(Image):
    """Representa uma imagem em cores no espaço BGR do OpenCV."""

    def __post_init__(self) -> None:
        assert isinstance(self.data, np.ndarray)
        assert len(self.data.shape) == 3 and self.data.shape[2] == 3

    def toGrayscale(self):  # -> GrayscaleImage
        """Converte para escala de cinza usando a combinação ponderada padrão."""

        return GrayscaleImage(cv2.cvtColor(self.data, cv2.COLOR_BGR2GRAY))


class GrayscaleImage(Image):
    """Armazena imagem com um único canal de intensidade."""

    def __post_init__(self) -> None:
        assert isinstance(self.data, np.ndarray)
        assert len(self.data.shape) == 2

    def toColor(self) -> ColorImage:
        """Expande o canal único para BGR, útil para visualização."""

        return ColorImage(cv2.cvtColor(self.data, cv2.COLOR_GRAY2BGR))

    def toBinary(self, threshold: Optional[int] = None, inverse: bool = True):  # -> BinaryImage
        """Gera imagem binária a partir de um limiar automático ou definido."""

        if threshold is None:
            if inverse:
                binaryData: np.ndarray
                _, binaryData = cv2.threshold(self.data, 0, 1, cv2.THRESH_OTSU)
                # Converte de uint8 -> bool, inverte valores e retorna a uint8
                binaryData = np.invert(binaryData.astype("bool")).astype("uint8")
            else:
                _, binaryData = cv2.threshold(self.data, 0, 1, cv2.THRESH_OTSU)
        else:
            if inverse:
                _, binaryData = cv2.threshold(self.data, threshold, 1, cv2.THRESH_BINARY_INV)
            else:
                _, binaryData = cv2.threshold(self.data, threshold, 1, cv2.THRESH_BINARY)

        return BinaryImage(binaryData)

    def normalized(self):  # -> GrayscaleImage:
        """Normaliza os valores para o intervalo ``[0, 1]``."""

        assert self.data.dtype is np.dtype("uint8")
        return GrayscaleImage(self.data / 255)

    def whitePointAdjusted(self, strength: float = 1.0):  # -> GrayscaleImage:
        """Ajusta o ponto branco para aumentar contraste."""

        hist = self.histogram()
        whitePoint = np.argmax(hist)
        whiteScaleFactor = 255 / whitePoint * strength
        return GrayscaleImage(cv2.addWeighted(self.data, whiteScaleFactor, self.data, 0, 0))

    def histogram(self) -> np.ndarray:
        """Retorna o histograma de intensidades da imagem."""

        counts, _ = np.histogram(self.data, 255, range=(0, 255))
        return counts


class BinaryImage(Image):
    """Imagem contendo apenas valores 0 ou 1 por pixel."""

    def __post_init__(self) -> None:
        assert isinstance(self.data, np.ndarray)
        assert len(self.data.shape) == 2

    def toColor(self) -> ColorImage:
        """Expande a imagem binária para BGR (0 ou 255)."""

        return ColorImage(cv2.cvtColor(self.data * 255, cv2.COLOR_GRAY2BGR))

    def toGrayscale(self) -> GrayscaleImage:
        """Converte para tons de cinza (0 ou 255)."""

        return GrayscaleImage(self.data * 255)


#########################
# Input / Output
#########################


def openImage(path: Path) -> ColorImage:
    """Abre uma imagem do disco retornando um ``ColorImage``."""

    assert isinstance(path, Path)
    assert path.exists()

    data = cv2.imread(str(path))
    assert data is not None

    return ColorImage(data)


def saveImage(image: Image, path: Path) -> None:
    """Salva ``image`` no caminho indicado convertendo para BGR se necessário."""

    assert isinstance(image, (ColorImage, GrayscaleImage, BinaryImage))

    if isinstance(image, ColorImage):
        outputImage = image
    elif isinstance(image, GrayscaleImage):
        outputImage = image.toColor()
    elif isinstance(image, BinaryImage):
        outputImage = image.toColor()
    else:
        raise AssertionError

    return cv2.imwrite(str(path), outputImage.data)


# TODO: This takes waaayyy to long for practical use
def getMode(inputImage: np.ndarray) -> Tuple[int, int, int]:
    """Obtém a cor mais frequente, útil para preencher bordas em rotações."""

    firstModes = stats.mode(inputImage, axis=0)
    modeResults = stats.mode(firstModes.mode, axis=1).mode[0][0]
    modeValues = tuple(map(int, modeResults))

    return modeValues


@dataclasses.dataclass(frozen=True)
class Rectangle:
    """Define um retângulo pela posição ``(x, y)`` e dimensões."""

    x: int
    y: int
    width: int
    height: int


@dataclasses.dataclass(frozen=True)
class Boundaries:
    """Delimita uma área com limites inicial/final em X e Y."""

    fromX: int
    toX: int
    fromY: int
    toY: int


def cropped(inputImage: Image, crop: Union[Rectangle, Boundaries]) -> Image:
    """Recorta uma subárea da imagem original."""

    if isinstance(crop, Rectangle):
        x, y, w, h = crop.x, crop.y, crop.width, crop.height
        crop = Boundaries(x, x + w, y, y + h)

    outputData = inputImage.data.copy()
    croppedData = outputData[crop.fromY:crop.toY, crop.fromX:crop.toX]

    if isinstance(inputImage, ColorImage):
        return ColorImage(croppedData)
    elif isinstance(inputImage, GrayscaleImage):
        return GrayscaleImage(croppedData)
    elif isinstance(inputImage, BinaryImage):
        return BinaryImage(croppedData)
    else:
        raise ValueError


def rotated(inputImage: Image, angle: float, border: Tuple[int, int, int] = (255, 255, 255)) -> Image:
    """Gira a imagem em ``angle`` graus preenchendo bordas com ``border``."""

    center = (inputImage.width // 2, inputImage.height // 2)
    rotationMatrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotatedData = cv2.warpAffine(
        inputImage.data,
        rotationMatrix,
        (inputImage.width, inputImage.height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border,
    )

    if isinstance(inputImage, ColorImage):
        return ColorImage(rotatedData)
    elif isinstance(inputImage, GrayscaleImage):
        return GrayscaleImage(rotatedData)
    elif isinstance(inputImage, BinaryImage):
        return BinaryImage(rotatedData)
    else:
        raise ValueError
