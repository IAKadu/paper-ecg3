"""Janela principal da aplicação."""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from views.EditorWidget import Editor
from model.Lead import LeadId
import QtWrapper as Qt


class MainWindow(QtWidgets.QMainWindow):
    """Agrupa menus, botões e o editor central de derivação."""

    def __init__(self):
        super().__init__()
        self.buildUI()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------
    def buildUI(self) -> None:
        """Cria menus, define o editor e ajusta propriedades da janela."""

        self.buildMenuBar()
        self.buildLeadButtonDictionary()

        # Widget principal onde o usuário edita as derivações.
        self.editor = Editor(self)
        self.setCentralWidget(self.editor)
        self.setContentsMargins(0, 0, 0, 0)

        self.setWindowTitle("Paper ECG")
        # self.setWindowIcon(QtGui.QIcon('pythonlogo.png'))

        # Exibe em tamanho fixo para macOS/Linux e maximizado no Windows.
        if sys.platform == "darwin" or sys.platform.startswith("linux"):
            self.resize(1000, 600)
            self.show()
        else:
            self.showMaximized()

    def buildMenuBar(self) -> None:
        """Cria a barra de menus com as opções principais."""

        Qt.MenuBar(
            owner=self,
            name="bar",
            menus=[
                self.buildFileMenu(),
                self.buildLeadMenu(),
                self.buildHelpMenu(),
            ],
        )

    def buildFileMenu(self) -> Qt.Menu:
        """Menu responsável por abrir ou fechar arquivos de imagem."""

        return Qt.Menu(
            owner=self,
            name="fileMenu",
            displayName="File",
            items=[
                # Opção para abrir um novo arquivo de imagem.
                Qt.MenuAction(
                    owner=self,
                    name="fileMenuOpen",
                    displayName="Open",
                    shortcut=QtGui.QKeySequence.Open,
                    statusTip="Open an image file",
                ),
                # Fecha a imagem atualmente carregada.
                Qt.MenuAction(
                    owner=self,
                    name="fileMenuClose",
                    displayName="Close",
                    shortcut=QtGui.QKeySequence.Close,
                    statusTip="Close image file",
                ),
            ],
        )

    def buildLeadMenu(self) -> Qt.Menu:
        """Menu para adicionar as doze derivações clássicas do ECG."""

        return Qt.Menu(
            owner=self,
            name="leadMenu",
            displayName="Leads",
            items=[
                Qt.MenuAction(owner=self, name="addLead1", displayName="Add Lead I", shortcut=QtGui.QKeySequence("Ctrl+1"), statusTip="Add Lead I"),
                Qt.MenuAction(owner=self, name="addLead2", displayName="Add Lead II", shortcut=QtGui.QKeySequence("Ctrl+2"), statusTip="Add Lead II"),
                Qt.MenuAction(owner=self, name="addLead3", displayName="Add Lead III", shortcut=QtGui.QKeySequence("Ctrl+3"), statusTip="Add Lead III"),
                Qt.MenuAction(owner=self, name="addLeadaVR", displayName="Add Lead aVR", shortcut=QtGui.QKeySequence("Ctrl+4"), statusTip="Add Lead aVR"),
                Qt.MenuAction(owner=self, name="addLeadaVL", displayName="Add Lead aVL", shortcut=QtGui.QKeySequence("Ctrl+5"), statusTip="Add Lead aVL"),
                Qt.MenuAction(owner=self, name="addLeadaVF", displayName="Add Lead aVF", shortcut=QtGui.QKeySequence("Ctrl+6"), statusTip="Add Lead aVF"),
                Qt.MenuAction(owner=self, name="addLeadV1", displayName="Add Lead V1", shortcut=QtGui.QKeySequence("Ctrl+7"), statusTip="Add Lead V1"),
                Qt.MenuAction(owner=self, name="addLeadV2", displayName="Add Lead V2", shortcut=QtGui.QKeySequence("Ctrl+8"), statusTip="Add Lead V2"),
                Qt.MenuAction(owner=self, name="addLeadV3", displayName="Add Lead V3", shortcut=QtGui.QKeySequence("Ctrl+9"), statusTip="Add Lead V3"),
                Qt.MenuAction(owner=self, name="addLeadV4", displayName="Add Lead V4", shortcut=QtGui.QKeySequence("Ctrl+0"), statusTip="Add Lead V4"),
                Qt.MenuAction(owner=self, name="addLeadV5", displayName="Add Lead V5", shortcut=QtGui.QKeySequence("Ctrl+[") , statusTip="Add Lead V5"),
                Qt.MenuAction(owner=self, name="addLeadV6", displayName="Add Lead V6", shortcut=QtGui.QKeySequence("Ctrl+]") , statusTip="Add Lead V6"),
            ],
        )

    def buildHelpMenu(self) -> Qt.Menu:
        """Menu com links úteis como guia do usuário e relatório de bugs."""

        return Qt.Menu(
            owner=self,
            name="helpMenu",
            displayName="Help",
            items=[
                Qt.MenuAction(
                    owner=self,
                    name="userGuideButton",
                    displayName="User Guide",
                    shortcut=None,
                    statusTip="View User Guide on GitHub",
                ),
                Qt.MenuAction(
                    owner=self,
                    name="reportIssueButton",
                    displayName="Report An Issue",
                    shortcut=None,
                    statusTip="Report and Issue on GitHub",
                ),
            ],
        )

    # ------------------------------------------------------------------
    # Eventos e utilitários auxiliares
    # ------------------------------------------------------------------
    def resizeEvent(self, event):
        """Garante que o Qt trate o evento de redimensionamento padrão."""

        QtWidgets.QMainWindow.resizeEvent(self, event)

    def buildLeadButtonDictionary(self) -> None:
        """Relaciona cada derivação ao botão de menu correspondente."""

        # Mapeamento usado por outras partes da aplicação para acionar as
        # ações de adicionar cada derivação por meio de um dicionário.
        self.leadButtons = {
            LeadId.I: self.addLead1,
            LeadId.II: self.addLead2,
            LeadId.III: self.addLead3,
            LeadId.aVR: self.addLeadaVR,
            LeadId.aVL: self.addLeadaVL,
            LeadId.aVF: self.addLeadaVF,
            LeadId.V1: self.addLeadV1,
            LeadId.V2: self.addLeadV2,
            LeadId.V3: self.addLeadV3,
            LeadId.V4: self.addLeadV4,
            LeadId.V5: self.addLeadV5,
            LeadId.V6: self.addLeadV6,
        }

