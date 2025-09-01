"""Painel de controles gerais do editor.

Permite ajustar rotação da imagem e parâmetros de escala da grade
(tempo e voltagem) antes do processamento do sinal.
"""

from datetime import datetime
from PyQt5 import QtCore, QtWidgets

from QtWrapper import *
import model.EcgModel as EcgModel
import ecgdigitize
from ecgdigitize.image import ColorImage
from views.MessageDialog import *

DEFAULT_TIME_SCALE = 25
DEFAULT_VOLTAGE_SCALE = 10


class EditPanelGlobalView(QtWidgets.QWidget):
    """Widget com ajustes aplicáveis a toda a imagem."""

    def __init__(self, parent):
        super().__init__()

        # Referência ao widget principal do editor
        self.editorWidget = parent

        # Configura políticas de tamanho para ocupar horizontalmente e ter altura fixa
        self.sizePolicy().setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.sizePolicy().setVerticalPolicy(QtWidgets.QSizePolicy.Fixed)

        self.initUI()
        self.connectUI()

    def initUI(self):
        """Monta os widgets de rotação e escala da grade."""

        VerticalBoxLayout(owner=self, name="mainLayout", margins=(5, 5, 5, 5), contents=[
            GroupBox(owner=self, name="adjustmentsGroup", title="Image Adjustments", layout=
                VerticalBoxLayout(owner=self, name="adjustmentsGroupLayout", contents=[
                    Label("Rotation"),
                    HorizontalSlider(self, "rotationSlider"),
                    HorizontalBoxLayout(owner=self, name="buttonLayout", margins=(0, 0, 0, 0), contents=[
                        PushButton(self, "autoRotateButton", text="Auto Rotate"),
                        PushButton(self, "resetRotationButton", text="Reset")
                    ])
                ])
            ),
            GroupBox(owner=self, name="gridScaleGroup", title="Grid Scale", layout=
                FormLayout(owner=self, name="controlsLayout", contents=[
                    (
                        Label(
                            owner=self,
                            name="timeScaleLabel",
                            text="Time Scale: "
                        ),
                        HorizontalBoxLayout(
                            owner=self,
                            name="timeScaleBoxLayout",
                            contents=[
                                SpinBox(
                                    owner=self,
                                    name="timeScaleSpinBox",
                                    minVal=1,
                                    maxVal=1000,
                                    suffix=" mm/s",
                                    defaultValue=DEFAULT_TIME_SCALE
                                )
                            ]
                        )
                    ),
                    (
                        Label(
                            owner=self,
                            name="voltScaleLabel",
                            text="Voltage Scale: "
                        ),
                        HorizontalBoxLayout(
                            owner=self,
                            name="voltageScaleBoxLayout",
                            contents=[
                                SpinBox(
                                    owner=self,
                                    name="voltScaleSpinBox",
                                    minVal=1,
                                    maxVal=1000,
                                    suffix=" mm/mV",
                                    defaultValue=DEFAULT_VOLTAGE_SCALE
                                )
                            ]
                        )

                    )
                ])
            ),
            PushButton(
                owner=self,
                name="processDataButton",
                text="Process Lead Data"
            ),
            PushButton(
                owner=self,
                name="saveAnnotationsButton",
                text="Save Metadata"
            ),
            Label(
                owner=self,
                name="lastSavedTimeStamp",
                text=""
            )
        ])

        self.mainLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.setLayout(self.mainLayout)

        # Alinha os rótulos do formulário à esquerda
        self.controlsLayout.setFormAlignment(QtCore.Qt.AlignLeft)
        self.controlsLayout.setLabelAlignment(QtCore.Qt.AlignLeft)
        # Faz com que os campos cresçam horizontalmente
        self.controlsLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        # Alinha os controles numéricos à direita
        self.timeScaleBoxLayout.setAlignment(QtCore.Qt.AlignRight)
        self.voltageScaleBoxLayout.setAlignment(QtCore.Qt.AlignRight)

        self.lastSavedTimeStamp.setAlignment(QtCore.Qt.AlignCenter)

        # Define valores iniciais nos *spin boxes*
        self.clearTimeSpinBox()
        self.clearVoltSpinBox()


    def connectUI(self):
        """Conecta sinais dos widgets às ações correspondentes."""
        self.rotationSlider.sliderPressed.connect(self.rotationSliderChanged)
        self.rotationSlider.sliderMoved.connect(self.rotationSliderChanged)
        # Slider permite variação de -15º a +15º (escala *10 para precisão)
        self.rotationSlider.setRange(-15 * 10, 15 * 10)

        self.autoRotateButton.clicked.connect(self.autoRotate)
        self.resetRotationButton.clicked.connect(self.resetRotation)

        self.processDataButton.clicked.connect(lambda: self.editorWidget.processEcgData.emit())
        self.saveAnnotationsButton.clicked.connect(lambda: self.editorWidget.saveAnnotationsButtonClicked.emit())

    def clearVoltSpinBox(self):
        """Restaura o valor padrão do controle de escala de voltagem."""
        self.voltScaleSpinBox.setValue(DEFAULT_VOLTAGE_SCALE)

    def clearTimeSpinBox(self):
        """Restaura o valor padrão do controle de escala de tempo."""
        self.timeScaleSpinBox.setValue(DEFAULT_TIME_SCALE)

    def rotationSliderChanged(self, _ = None):
        """Atualiza a rotação da imagem conforme o movimento do *slider*."""
        value = self.getRotation()
        self.editorWidget.imageViewer.rotateImage(value)

    def getRotation(self) -> float:
        """Valor atual de rotação em graus."""
        return self.rotationSlider.value() / -10

    def setRotation(self, angle: float):
        """Altera o valor do *slider* e aplica a rotação indicada."""
        self.rotationSlider.setValue(angle * -10)
        self.rotationSliderChanged()

    def autoRotate(self):
        """Tenta estimar automaticamente a inclinação do papel milimetrado."""
        if self.editorWidget.image is None:
            return

        colorImage = ColorImage(self.editorWidget.image)
        angle = ecgdigitize.estimateRotationAngle(colorImage)

        if angle is None:
            errorModal = QtWidgets.QMessageBox()
            errorModal.setWindowTitle("Error")
            errorModal.setText("Unable to detect the angle automatically!")
            errorModal.setInformativeText("Use the slider to adjust the rotation manually")
            errorModal.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            errorModal.exec_()
        else:
            self.setRotation(angle)

    def resetRotation(self):
        """Retorna a imagem à orientação original."""
        self.setRotation(0)

    def setValues(self, voltScale, timeScale):
        """Define os valores exibidos nos controles de escala."""
        self.voltScaleSpinBox.setValue(voltScale)
        self.timeScaleSpinBox.setValue(timeScale)

    def setLastSavedTimeStamp(self, timeStamp=None):
        """Exibe a data/hora da última gravação de metadados."""
        if timeStamp is not None:
            self.lastSavedTimeStamp.setText("Last saved: " + timeStamp)
        else:
            self.lastSavedTimeStamp.setText(None)

