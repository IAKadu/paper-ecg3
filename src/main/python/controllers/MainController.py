"""
MainController.py
Criado em 9 de novembro de 2020

Controla a janela principal, incluindo a barra de menus e o editor.
"""
from pathlib import Path

import cv2
import json
import dataclasses
import webbrowser
from PyQt5 import QtWidgets

from ecgdigitize.image import ColorImage, openImage

from Conversion import convertECGLeads, exportSignals
from views.MainWindow import MainWindow
from views.ImageView import *
from views.EditorWidget import *
from views.ROIView import *
from views.ExportFileDialog import *
from QtWrapper import *
import Annotation
from model.Lead import Lead, LeadId
import datetime
from model.InputParameters import InputParameters


class MainController:

    def __init__(self):
        # Cria a janela principal da aplicação
        self.window = MainWindow()
        # Conecta os elementos da interface aos métodos do controlador
        self.connectUI()
        # Caminho do arquivo de imagem atualmente aberto
        self.openFile = None
        # Imagem colorida carregada para edição
        self.openImage: Optional[ColorImage] = None

    def connectUI(self):
        """Liga os elementos da interface gráfica aos respectivos manipuladores."""
        self.window.fileMenuOpen.triggered.connect(self.openImageFile)
        self.window.fileMenuClose.triggered.connect(self.closeImageFile)
        self.window.editor.processEcgData.connect(self.confirmDigitization)
        self.window.editor.saveAnnotationsButtonClicked.connect(self.saveAnnotations)

        # Abre páginas auxiliares no navegador padrão
        self.window.reportIssueButton.triggered.connect(
            lambda: webbrowser.open('https://github.com/Tereshchenkolab/paper-ecg/issues')
        )
        self.window.userGuideButton.triggered.connect(
            lambda: webbrowser.open('https://github.com/Tereshchenkolab/paper-ecg/blob/master/USER-GUIDE.md')
        )

    def openImageFile(self):
        """Solicita ao usuário uma imagem e a carrega no editor."""

        # Conforme a documentação do pathlib, se nenhuma seleção é feita Path('.') é retornado
        #  https://docs.python.org/3/library/pathlib.html
        path = Path(self.openFileBrowser("Open File", "Images (*.png *.jpg *.jpeg *.tif *.tiff)"))

        if path != Path('.'):
            # Carrega a imagem e reinicia os controles de edição
            self.window.editor.loadImageFromPath(path)
            self.window.editor.resetImageEditControls()
            self.openFile = path
            self.openImage = openImage(path)
            # Tenta carregar anotações previamente salvas
            self.attempToLoadAnnotations()
        else:
            print("[Warning] No image selected")

    def openFileBrowser(self, caption: str, fileType: str, initialPath: str = "") -> str:
        """Abre um diálogo para que o usuário selecione um arquivo.

        Args:
            caption (str): Texto exibido na janela.
            fileType (str): Tipos de arquivos aceitos, ex: `Images (*.png *.jpg)`.
            initialPath (str, optional): Caminho inicial do navegador. Padrão "".

        Returns:
            str: Caminho absoluto do arquivo selecionado.
        """
        absolutePath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.window,  # Janela pai
            caption,
            initialPath,  # Se vazio, usa o caminho acessado recentemente
            fileType,
        )

        return absolutePath

    def closeImageFile(self):
        """Fecha a imagem atual e restaura os controles do editor."""
        self.window.editor.removeImage()
        self.window.editor.deleteAllLeadRois()
        self.window.editor.resetImageEditControls()
        self.openFile = None
        self.openImage = None

    def confirmDigitization(self):
        """Valida os dados informados e inicia a digitalização, se possível."""
        inputParameters = self.getCurrentInputParameters()

        # Trecho utilitário para salvar a derivação I em arquivo (mantido como referência)
        # rotatedImage = digitize.image.rotated(self.window.editor.image, inputParameters.rotation)
        # leadData = inputParameters.leads[LeadId.I]
        # cropped = digitize.image.cropped(
        #     rotatedImage,
        #     digitize.image.Rectangle(
        #         leadData.x, leadData.y, leadData.width, leadData.height
        #     )
        # )
        # import random
        # cv2.imwrite(f"lead-pictures/{self.openFile.stem}-{random.randint(0,10**8)}.png", cropped)

        if len(inputParameters.leads) > 0:
            # Há pelo menos uma derivação selecionada; prossegue para processamento
            self.processEcgData(inputParameters)
        else:
            # Nenhuma derivação selecionada: exibe aviso
            warningDialog = MessageDialog(
                message="Warning: No data to process\n\nPlease select at least one lead to digitize",
                title="Warning",
            )
            warningDialog.exec_()

    # temos todos os dados do ECG e local de exportação – prontos para processar
    def processEcgData(self, inputParameters):
        """Recebe os parâmetros e gera os sinais digitalizados."""
        if self.window.editor.image is None:
            raise Exception("IMAGE NOT AVAILABLE WHEN `processEcgData` CALLED")

        # Extrai os sinais e imagens de pré-visualização
        extractedSignals, previewImages = convertECGLeads(self.openImage, inputParameters)

        if extractedSignals is None:
            # Exibe erro caso o processamento falhe
            errorDialog = MessageDialog(
                message="Error: Signal Processing Failed\n\nPlease check your lead selection boxes",
                title="Error",
            )
            errorDialog.exec_()
        else:
            # Mostra diálogo para exportação dos sinais
            exportFileDialog = ExportFileDialog(previewImages)
            if exportFileDialog.exec_():
                self.exportECGData(
                    exportFileDialog.fileExportPath,
                    exportFileDialog.delimiterDropdown.currentText(),
                    extractedSignals,
                )

    def exportECGData(self, exportPath, delimiter, extractedSignals):
        """Salva os sinais digitalizados no arquivo escolhido."""
        seperatorMap = {"Comma": ',', "Tab": '\t', "Space": ' '}
        assert delimiter in seperatorMap, f"Unrecognized delimiter {delimiter}"

        exportSignals(extractedSignals, exportPath, separator=seperatorMap[delimiter])

    def saveAnnotations(self):
        """Persiste as anotações da imagem atual em um arquivo JSON."""
        inputParameters = self.getCurrentInputParameters()

        if self.window.editor.image is None:
            return

        assert self.openFile is not None

        def extractLeadAnnotation(lead: Lead) -> Annotation.LeadAnnotation:
            return Annotation.LeadAnnotation(
                Annotation.CropLocation(
                    lead.x,
                    lead.y,
                    lead.width,
                    lead.height,
                ),
                lead.startTime,
            )

        metadataDirectory = self.openFile.parent / '.paperecg'
        if not metadataDirectory.exists():
            metadataDirectory.mkdir()

        filePath = metadataDirectory / (self.openFile.stem + '-' + self.openFile.suffix[1:] + '.json')

        print("leads\n", inputParameters.leads.items())

        leads = {
            name: extractLeadAnnotation(lead) for name, lead in inputParameters.leads.items()
        }

        currentDateTime = (datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")

        Annotation.Annotation(
            timeStamp=currentDateTime,
            image=Annotation.ImageMetadata(self.openFile.name, directory=str(self.openFile.parent.absolute())),
            rotation=inputParameters.rotation,
            timeScale=inputParameters.timeScale,
            voltageScale=inputParameters.voltScale,
            leads=leads,
        ).save(filePath)

        print("Metadata successfully saved to:", str(filePath))
        self.window.editor.EditPanelGlobalView.setLastSavedTimeStamp(currentDateTime)

    def attempToLoadAnnotations(self):
        """Tenta carregar anotações previamente salvas para a imagem aberta."""
        if self.window.editor.image is None:
            return

        assert self.openFile is not None

        metadataDirectory = self.openFile.parent / '.paperecg'
        if not metadataDirectory.exists():
            return

        filePath = metadataDirectory / (self.openFile.stem + '-' + self.openFile.suffix[1:] + '.json')
        if not filePath.exists():
            return

        print("Loading saved state from:", filePath, '...')

        # Carrega o estado salvo
        with open(filePath) as file:
            data = json.load(file)

        self.window.editor.loadSavedState(data)

    def getCurrentInputParameters(self):
        """Obtém os parâmetros atuais informados na interface."""
        return InputParameters(
            rotation=self.window.editor.EditPanelGlobalView.getRotation(),
            timeScale=self.window.editor.EditPanelGlobalView.timeScaleSpinBox.value(),
            voltScale=self.window.editor.EditPanelGlobalView.voltScaleSpinBox.value(),
            leads=self.window.editor.imageViewer.getAllLeadRoisAsDict(),
        )

