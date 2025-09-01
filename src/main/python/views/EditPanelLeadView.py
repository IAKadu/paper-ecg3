"""Painel de edição específico para cada derivação."""

from PyQt5 import QtCore, QtWidgets

from QtWrapper import *


class EditPanelLeadView(QtWidgets.QWidget):
    """Widget que permite editar parâmetros individuais de um *lead*."""

    leadStartTimeChanged = QtCore.pyqtSignal(str, float)
    deleteLeadRoi = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()

        # Referência ao widget do editor que contém este painel
        self.parent = parent

        self.leadId = None

        # Define políticas de tamanho para ocupar largura total e altura fixa
        self.sizePolicy().setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.sizePolicy().setVerticalPolicy(QtWidgets.QSizePolicy.Fixed)

        self.initUI()

    def initUI(self):
        """Cria os controles de configuração do lead."""

        VerticalBoxLayout(owner=self, name="mainlayout", margins=(5, 5, 5, 5), contents=[
            Label(
                owner=self,
                name="title",
                text=""
            ),
            FormLayout(owner=self, name="controlsLayout", contents=[
                [
                    Label(
                        owner=self,
                        name="leadStartTimeLabel",
                        text="Start time: "
                    ),
                    DoubleSpinBox(
                        owner=self,
                        name="leadStartTimeSpinBox",
                        suffix=" sec",
                        minVal=0,
                        maxVal=1000
                    )
                ]
            ]),
            PushButton(
                owner=self,
                name="deleteLeadButton",
                text="Delete Lead"
            )
        ])

        self.mainlayout.setAlignment(QtCore.Qt.AlignTop)
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        self.setLayout(self.mainlayout)
        # Propaga alteração de tempo inicial e requisição de exclusão
        self.leadStartTimeSpinBox.valueChanged.connect(
            lambda: self.leadStartTimeChanged.emit(self.leadId, self.leadStartTimeSpinBox.value())
        )
        self.deleteLeadButton.clicked.connect(lambda: self.deleteLeadRoi.emit(self.leadId))


    def setValues(self, leadId, startTime=0.0):
        """Define identificador e início do traçado para o *lead* atual."""
        self.leadId = leadId
        self.setTitle(leadId)
        self.leadStartTimeSpinBox.setValue(startTime)

    def setTitle(self, leadId):
        """Exibe o nome do *lead* no título do painel."""
        self.title.setText("Lead " + leadId)

    def startTimeChanged(self):
        """Callback simples utilizado em testes ou *debug*."""
        print("start time changed: " + str(self.leadStartTimeSpinBox.value()))
        self.parent.leadStartTimeChanged.emit(self.leadId, self.leadStartTimeSpinBox.value())
