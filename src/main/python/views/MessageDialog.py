"""Caixa de diálogo simples para exibir mensagens ao usuário."""

from PyQt5 import QtCore, QtGui, QtWidgets
from QtWrapper import *


class MessageDialog(QtWidgets.QDialog):
    """Mostra uma mensagem informativa com um único botão de confirmação."""

    def __init__(self, message: str = "", title: str = ""):
        super().__init__()
        self.message = message
        self.title = title
        self.initUI()
        self.connectUI()

    def initUI(self) -> None:
        """Constrói os widgets que compõem a janela."""

        self.setWindowTitle(self.title)
        VerticalBoxLayout(
            owner=self,
            name="mainLayout",
            contents=[
                # Texto central com a mensagem desejada.
                Label(owner=self, name="message", text=self.message),
                # Botão para fechar a janela.
                PushButton(owner=self, name="okButton", text="OK"),
            ],
        )
        self.message.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainLayout)

    def connectUI(self) -> None:
        """Define os sinais da interface."""

        # Fecha a janela quando o botão for pressionado.
        self.okButton.clicked.connect(lambda: self.close())

