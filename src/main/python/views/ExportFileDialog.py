"""Janela para exportar os sinais digitalizados para arquivo."""

from PyQt5 import QtWidgets, QtCore
from QtWrapper import *
from views.ImagePreviewDialog import ImagePreviewDialog

# Mapeia a descrição apresentada ao usuário para a extensão do arquivo
fileTypesDictionary = {
    "Text File (*.txt)": "txt",
    "CSV (*.csv)": "csv",
}


class ExportFileDialog(QtWidgets.QDialog):
    """Permite escolher o caminho de exportação e visualizar as derivações."""

    def __init__(self, previewImages):
        super().__init__()
        self.leadPreviewImages = previewImages
        self.fileExportPath = None
        self.fileType = None
        self.setWindowTitle("Export ECG Data")
        # Tamanho inicial arbitrário para facilitar o desenvolvimento.
        self.resize(700, 400)
        self.buildUI()

    def buildUI(self) -> None:
        """Monta todos os widgets e layouts da janela."""

        self.leadPreviewLayout = QtWidgets.QFormLayout()

        # Cria um par "rótulo/botão de prévia" para cada derivação processada.
        for leadId, image in sorted(self.leadPreviewImages.items(), key=lambda img: img[0].value):
            self.leadPreviewLayout.addRow(
                Label(owner=self, text="Lead " + str(leadId.name)),
                PushButton(owner=self, name="button", text="Preview"),
            )
            self.button.clicked.connect(
                lambda checked, img=image.data, title=leadId.name: self.displayPreview(img, title)
            )

        VerticalBoxLayout(
            owner=self,
            name="mainLayout",
            contents=[
                # Linha para escolher o caminho do arquivo de saída.
                HorizontalBoxLayout(
                    owner=self,
                    name="chooseFileLayout",
                    contents=[
                        Label(owner=self, name="chooseFileLabel", text="Export to:"),
                        LineEdit(
                            owner=self,
                            name="chooseFileTextBox",
                            contents="Choose file path",
                            readOnly=True,
                        ),
                        PushButton(owner=self, name="chooseFileButton", text="..."),
                    ],
                ),
                # Seleção de delimitador do arquivo exportado.
                HorizontalBoxLayout(
                    owner=self,
                    name="delimiterChoiceLayout",
                    contents=[
                        Label(owner=self, name="delimiterLabel", text="Data Delimiter: "),
                        ComboBox(
                            owner=self,
                            name="delimiterDropdown",
                            items=["Comma", "Tab", "Space"],
                        ),
                    ],
                ),
                # Área de pré-visualização das derivações exportadas.
                VerticalBoxLayout(
                    owner=self,
                    name="leadPreviewLayout",
                    contents=[
                        Label(owner=self, name="leadPreviewLabel", text="Preview Selected Leads:"),
                        ScrollArea(
                            owner=self,
                            name="leadPreivewScrollArea",
                            innerWidget=Widget(
                                owner=self,
                                name="leadPreviewWidget",
                                layout=self.leadPreviewLayout,
                            ),
                        ),
                    ],
                ),
                # Botões de confirmação/cancelamento e área para mensagem de erro.
                HorizontalBoxLayout(
                    owner=self,
                    name="confirmCancelButtonLayout",
                    contents=[
                        Label(owner=self, name="errorMessageLabel", text=""),
                        PushButton(owner=self, name="confirmButton", text="Export"),
                        PushButton(owner=self, name="cancelButton", text="Cancel"),
                    ],
                ),
            ],
        )

        self.delimiterChoiceLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.confirmCancelButtonLayout.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)

        self.setLayout(self.mainLayout)

        self.connectUI()

    def connectUI(self) -> None:
        """Conecta sinais e slots dos botões."""

        self.chooseFileButton.clicked.connect(lambda: self.openSaveFileDialog())
        self.confirmButton.clicked.connect(lambda: self.confirmExportPath())
        self.cancelButton.clicked.connect(lambda: self.close())

    def openSaveFileDialog(self) -> None:
        """Abre diálogo nativo para selecionar o caminho de exportação."""

        path, selectedFilter = QtWidgets.QFileDialog.getSaveFileName(
            parent=self,
            caption="Export to File",
            filter="Text File (*.txt);;CSV (*.csv)",
        )
        if path != "" and selectedFilter in fileTypesDictionary:
            self.errorMessageLabel.setText("")
            self.chooseFileTextBox.setText(path)
            self.fileExportPath = path
            self.fileType = fileTypesDictionary[selectedFilter]

    def confirmExportPath(self) -> None:
        """Valida a seleção de caminho antes de fechar a janela."""

        if self.fileExportPath is not None and self.fileType is not None:
            self.accept()
        else:
            print("no export path selected")
            self.errorMessageLabel.setText("Please select a valid export path")

    def displayPreview(self, image, title) -> None:
        """Exibe uma pré-visualização da derivação escolhida."""

        previewDialog = ImagePreviewDialog(image, title)
        previewDialog.exec_()

