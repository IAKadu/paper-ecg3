"""Widget de visualização da imagem do ECG com suporte a zoom e rotação."""
import sys
from typing import Any

from PyQt5 import QtGui, QtCore, QtWidgets

import ImageUtilities
from views.ROIView import ROI_ITEM_TYPE
from model.Lead import Lead, LeadId


MACOS_SCROLL_KEYS = {QtCore.Qt.Key_Meta}  # Tecla Option
# TODO: encontrar forma de capturar a tecla Command; a janela de seleção de arquivos
# rouba o foco e impede o recebimento do evento de soltar a tecla.
SCROLL_STEP_FACTOR = 1.5


onMacOS = sys.platform == "darwin"


# Adaptado de: https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
class ImageView(QtWidgets.QGraphicsView):
    """`QGraphicsView` especializado para exibir e manipular a imagem do ECG."""

    roiItemSelected = QtCore.pyqtSignal(str, bool)
    updateRoiItem = QtCore.pyqtSignal(object)
    updateScale = QtCore.pyqtSignal(float)

    def __init__(self):
        super().__init__()

        self._zoom = 0
        self._scale = 1
        self._empty = True
        self._imageRect = None
        self._macosScrollKey = False

        self._scene = QtWidgets.QGraphicsScene(self)
        self._container = ImageView.createContainer()  # Permite mecânica de rotação
        self._pixmapItem = QtWidgets.QGraphicsPixmapItem(parent=self._container)  # Pixmap com a imagem do ECG
        self._scene.addItem(self._container)

        self.setMinimumSize(600, 400)  # Tamanho mínimo da área de visualização
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.addShortcuts()


    def addShortcuts(self):
        """Habilita atalhos de teclado para ampliar ou reduzir a imagem."""
        QtWidgets.QShortcut(
            QtGui.QKeySequence(QtGui.QKeySequence.ZoomIn),
            self,
            context=QtCore.Qt.WidgetShortcut,
            activated=self.zoomIn,
        )

        QtWidgets.QShortcut(
            QtGui.QKeySequence(QtGui.QKeySequence.ZoomOut),
            self,
            context=QtCore.Qt.WidgetShortcut,
            activated=self.zoomOut,
        )

    @staticmethod
    def createContainer():
        """Cria retângulo base onde o `QPixmap` será inserido."""
        container = QtWidgets.QGraphicsRectItem()
        container.setPen(QtGui.QPen(QtCore.Qt.NoPen))  # Oculta a borda
        container.setFlag(container.ItemClipsChildrenToShape)  # Recorta cantos ao rotacionar
        container.setBrush(QtCore.Qt.white)  # Cor de fundo padrão
        return container

    def setContainerBackground(self, color: Any):
        """Altera a cor de fundo do contêiner de imagem."""
        # TODO: Ajustar para respeitar o parâmetro `color`
        self._container.setBrush(QtCore.Qt.white)

    @property
    def imageRect(self):
        """Retângulo atual ocupado pela imagem."""
        return QtCore.QRectF(self._pixmapItem.pixmap().rect())

    def imageChanged(self):
        """Atualiza dimensões da cena após modificar o `QPixmap`."""
        print("Image changed")
        newRect = self.imageRect
        self._scene.setSceneRect(newRect)
        self._container.setRect(newRect)

    def resizeEvent(self, event):
        """Garante que a imagem se ajuste ao redimensionar a janela."""
        if self.hasImage() and not self.verticalScrollBar().isVisible() and not self.horizontalScrollBar().isVisible():
           self.fitInView(self.imageRect, QtCore.Qt.KeepAspectRatio)

        super().resizeEvent(event)

    def hasImage(self):
        """Indica se há uma imagem carregada."""
        return not self._empty

    def setImage(self, image=None):
        """Recebe uma imagem OpenCV e a exibe no `QGraphicsView`."""
        print("Image set")
        self._pixmapItem.setPixmap(ImageUtilities.opencvImageToPixmap(image))
        self._empty = False
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

        # Mostra o contêiner de fundo da imagem
        self._container.setVisible(True)

        self.rotateImage(0)

        # Define a origem de rotação no centro do pixmap
        pixmapSize = self._pixmapItem.pixmap().size()
        self._pixmapItem.setTransformOriginPoint(pixmapSize.width() // 2, pixmapSize.height() // 2)

        self.imageChanged()

    def fitImageInView(self):
        """Ajusta o *zoom* para enquadrar toda a imagem."""
        self.fitInView(self.imageRect, QtCore.Qt.KeepAspectRatio)

    def removeImage(self):
        """Remove o `QPixmap` e oculta o contêiner da imagem."""
        self._image = None
        self._pixmapItem.setPixmap(QtGui.QPixmap())
        self._empty = True

        # Esconde o contêiner de fundo da imagem
        self._container.setVisible(False)

        self.rotateImage(0)

    def removeAllRoiBoxes(self):
        """Remove todas as caixas de ROI da cena."""
        for item in self._scene.items():
            if item.type == ROI_ITEM_TYPE:
                self._scene.removeItem(item)

    def removeRoiBox(self, leadId):
        """Remove uma ROI específica identificada pelo `leadId`."""
        for item in self._scene.items():
            if item.type == ROI_ITEM_TYPE and item.leadId == leadId:
                self._scene.removeItem(item)

    def getAllLeadRoisAsDict(self):
        """Retorna todas as ROIs como dicionário `LeadId` -> `Lead`."""
        leads = {}
        for item in self._scene.items():
            if item.type == ROI_ITEM_TYPE:
                leads[LeadId[item.leadId]] = Lead(
                    x=item.x, y=item.y, width=item.width, height=item.height, startTime=item.startTime
                )
        return leads

    def getLeadRoiStartTime(self, leadId):
        """Obtém o tempo inicial associado a uma ROI."""
        for item in self._scene.items():
            if item.type == ROI_ITEM_TYPE and item.leadId == leadId:
                return item.startTime

    def setLeadRoiStartTime(self, leadId, startTime):
        """Define o tempo inicial para uma ROI específica."""
        for item in self._scene.items():
            if item.type == ROI_ITEM_TYPE and item.leadId == leadId:
                item.startTime = startTime

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """Detecta teclas especiais para zoom no macOS."""
        if onMacOS and event.key() in MACOS_SCROLL_KEYS:
            self._macosScrollKey = True
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        """Atualiza estado quando teclas especiais são liberadas."""
        if onMacOS and event.key() in MACOS_SCROLL_KEYS:
            self._macosScrollKey = False
        return super().keyPressEvent(event)

    def event(self, event):
        """Trata gestos e perda de foco para suporte a *trackpads* no macOS."""
        # Detecta gesto de pinça no macOS
        # Exemplo: https://doc.qt.io/qt-5/qtwidgets-gestures-imagegestures-example.html
        if isinstance(event, QtGui.QFocusEvent):
            if event.lostFocus():
                self._macosScrollKey = False

        if isinstance(event, QtGui.QNativeGestureEvent) and event.gestureType() == QtCore.Qt.ZoomNativeGesture:
            pinchAmount = event.value()
            self.smoothZoom(pinchAmount)

        return super().event(event)

    def wheelEvent(self, event):
        """Implementa zoom com scroll do mouse ou *trackpad*."""
        if onMacOS:
            if self._macosScrollKey:
                self.smoothZoom(event.angleDelta().y() / 750)
            else:
                super().wheelEvent(event)
        else:  # Zoom in and out using mouse wheel
            if event.angleDelta().y() > 0:
                self.zoomIn()
            else:
                self.zoomOut()

    # def updatePixelSizeOnScreen(self):
    #     print()
    #     graphicsViewRect = self.rect()
    #     viewWidth, viewHeight = graphicsViewRect.width(), graphicsViewRect.height()
    #     imageWidth, imageHeight = self.imageRect.width(), self.imageRect.height()
    #     print(viewWidth, viewHeight, imageWidth, imageHeight)

    def smoothZoom(self, amount: float):
        """Realiza zoom suave proporcional ao gesto no macOS."""
        scaleChange = (1 + amount)
        new_scale = self._scale * scaleChange
        if (self._scale > 1 or amount > 0) and new_scale >= 1:
            self._scale = new_scale
            self.scale(scaleChange, scaleChange)
        else:  # Snap image to the window so it's never smaller than the canvas
            self.fitInView(QtCore.QRectF(self._pixmapItem.pixmap().rect()), QtCore.Qt.KeepAspectRatio)
            self._scale = 1

    #zoomIn and zoomOut based on: https://stackoverflow.com/questions/57713795/zoom-in-and-out-in-widget
    def zoomIn(self):
        """Amplia a imagem em um passo fixo."""
        if self.hasImage():
            transformScale = QtGui.QTransform()
            transformScale.scale(SCROLL_STEP_FACTOR, SCROLL_STEP_FACTOR)

            transform = self.transform() * transformScale
            self.setTransform(transform)
            self._zoom += 1

            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def zoomOut(self):
        """Reduz a imagem ou reajusta para caber na janela."""
        if self.hasImage():
            transformScale = QtGui.QTransform()
            transformScale.scale(SCROLL_STEP_FACTOR, SCROLL_STEP_FACTOR)
            invertedScale, invertible = transformScale.inverted()

            if invertible:
                if self._zoom > 1:
                    transform = self.transform() * invertedScale
                    self.setTransform(transform)
                    self._zoom -= 1
                elif self._zoom == 1:
                    self.fitInView(self.imageRect, QtCore.Qt.KeepAspectRatio)
                    self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                    self._zoom = 0
            else:
                print("scale not invertible")

    def rotateImage(self, rotation: float):
        """Aplica rotação à imagem em torno do seu centro."""
        # No QGraphics a rotação tem sinal invertido em relação ao convencional
        self._pixmapItem.setRotation(rotation * -1)
