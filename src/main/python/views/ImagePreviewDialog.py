
"""Diálogo de visualização de imagem individual.

Este módulo contém um `QDialog` simples que apresenta ao usuário
uma prévia ampliada de uma derivação do ECG.  A imagem exibida é
recebida em formato *OpenCV* e convertida para `QPixmap`.
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from QtWrapper import *
from ImageUtilities import opencvImageToPixmap


class ImagePreviewDialog(QtWidgets.QDialog):
    """Janela modal responsável por exibir uma derivação isolada.

    Parameters
    ----------
    image : numpy.ndarray
        Matriz da imagem em formato *OpenCV* que será exibida.
    leadId : str
        Identificador textual da derivação apresentada no título.
    """

    def __init__(self, image, leadId):
        super().__init__()
        # Converte a imagem do OpenCV para o formato aceito pelo Qt
        self.pixmap = opencvImageToPixmap(image)
        self.leadId = leadId
        self.initUI()

    def initUI(self):
        """Monta a interface básica do diálogo."""
        self.setWindowTitle("Lead " + str(self.leadId))

        # Layout vertical simples que ocupa toda a janela
        self.layout = QVBoxLayout()
        # Margens utilizadas para manter um pequeno espaçamento ao redor
        self.margins = QtCore.QMargins(4, 4, 4, 4)

        # `QLabel` central onde a imagem será desenhada
        self.pixmapLabel = QLabel()
        self.pixmapLabel.setContentsMargins(self.margins)
        self.pixmapLabel.setPixmap(self.pixmap)
        self.pixmapLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.pixmapLabel.setMinimumSize(1, 1)

        # Insere o rótulo no layout e remove margens externas
        self.layout.addWidget(self.pixmapLabel)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

    def resizeEvent(self, event):
        """Redimensiona a imagem ao alterar o tamanho da janela."""
        self.pixmapLabel.resize(
            self.width() - (self.margins.right() - self.margins.left()),
            self.height() - (self.margins.top() - self.margins.bottom()),
        )
        self.pixmapLabel.setPixmap(
            self.pixmap.scaled(
                self.pixmapLabel.width(),
                self.pixmapLabel.height(),
                QtCore.Qt.KeepAspectRatio,
            )
        )
