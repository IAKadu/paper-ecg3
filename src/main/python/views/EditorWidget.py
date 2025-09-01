"""Widget principal do editor de ECG.

Agrupa a área de visualização da imagem e os painéis de edição,
permitindo ao usuário selecionar derivação, ajustar rotação e
configurações de escala antes da digitalização do sinal.
"""
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from model.Lead import LeadId
from views.ImageView import *
from views.ROIView import *
from views.EditPanelLeadView import *
from views.EditPanelGlobalView import *
from QtWrapper import *
from views.MessageDialog import *

class Editor(QtWidgets.QWidget):
    """Componente central que coordena visualização e edição do ECG."""

    processEcgData = QtCore.pyqtSignal()
    saveAnnotationsButtonClicked = QtCore.pyqtSignal()

    image = None  # Imagem em formato OpenCV

    def __init__(self, parent):
        super().__init__()
        # Referência à janela principal da aplicação
        self.mainWindow = parent

        self.initUI()
        self.connectUI()

    def initUI(self):
        """Monta a interface do editor com visualizador e painel de controles."""
        self.setLayout(
            HorizontalBoxLayout(self, "main", margins=(0,0,0,0), contents=[
                HorizontalSplitter(owner=self, name="viewSplitter", contents=[
                    Custom(
                        owner=self,
                        name="imageViewer",
                        widget=ImageView()
                    ),
                    ScrollArea(
                        owner=self,
                        name="controlPanel",
                        horizontalScrollBarPolicy=QtCore.Qt.ScrollBarAlwaysOff,
                        verticalScrollBarPolicy=QtCore.Qt.ScrollBarAsNeeded,
                        widgetIsResizable=True,
                        innerWidget=
                        StackedWidget(owner=self, name="editPanel", widgets=[
                            Custom(
                                owner=self,
                                name="EditPanelGlobalView",
                                widget=EditPanelGlobalView(self)
                            ),
                            Custom(
                                owner=self,
                                name="EditPanelLeadView",
                                widget=EditPanelLeadView(self)
                            )
                        ])
                    )
                ])
            ])
        )
        self.viewSplitter.setCollapsible(0,False)
        self.viewSplitter.setCollapsible(1,False)
        self.viewSplitter.setSizes([2,1])
        self.editPanel.setCurrentIndex(0)

        # Constraint the width of the adjustable side panel on the right of the editor
        self.controlPanel.setMinimumWidth(250)
        self.controlPanel.setMaximumWidth(450)

    def connectUI(self):
        """Conecta sinais de menu e widgets internos às ações do editor."""
        self.mainWindow.addLead1.triggered.connect(lambda: self.addLead(LeadId['I']))
        self.mainWindow.addLead2.triggered.connect(lambda: self.addLead(LeadId['II']))
        self.mainWindow.addLead3.triggered.connect(lambda: self.addLead(LeadId['III']))
        self.mainWindow.addLeadaVR.triggered.connect(lambda: self.addLead(LeadId['aVR']))
        self.mainWindow.addLeadaVL.triggered.connect(lambda: self.addLead(LeadId['aVL']))
        self.mainWindow.addLeadaVF.triggered.connect(lambda: self.addLead(LeadId['aVF']))
        self.mainWindow.addLeadV1.triggered.connect(lambda: self.addLead(LeadId['V1']))
        self.mainWindow.addLeadV2.triggered.connect(lambda: self.addLead(LeadId['V2']))
        self.mainWindow.addLeadV3.triggered.connect(lambda: self.addLead(LeadId['V3']))
        self.mainWindow.addLeadV4.triggered.connect(lambda: self.addLead(LeadId['V4']))
        self.mainWindow.addLeadV5.triggered.connect(lambda: self.addLead(LeadId['V5']))
        self.mainWindow.addLeadV6.triggered.connect(lambda: self.addLead(LeadId['V6']))

        # Quando usuário seleciona uma ROI, alterna painel correspondente
        self.imageViewer.roiItemSelected.connect(self.setControlPanel)

        self.EditPanelLeadView.leadStartTimeChanged.connect(self.updateLeadStartTime)
        self.EditPanelLeadView.deleteLeadRoi.connect(self.deleteLeadRoi)

    def loadSavedState(self, data):
        """Restaura estado previamente salvo, incluindo rotação e ROIs."""
        self.EditPanelGlobalView.setRotation(data['rotation'])
        self.EditPanelGlobalView.setValues(voltScale=data['voltageScale'], timeScale=data['timeScale'])
        self.EditPanelGlobalView.setLastSavedTimeStamp(data['timeStamp'])

        leads = data['leads']
        for name in leads:
            lead = leads[name]
            cropping = lead['cropping']
            self.addLead(
                leadIdEnum=LeadId[name],
                x=cropping['x'],
                y=cropping['y'],
                width=cropping['width'],
                height=cropping['height'],
                startTime=lead['start'],
            )


    ###########################
    # Control Panel Functions #
    ###########################

    def setControlPanel(self, leadId=None, leadSelected=False):
        """Alterna entre painel global e painel de detalhes da derivação."""
        if leadSelected == True and leadId is not None:
            self.showLeadDetailView(leadId)
        else:
            self.showGlobalView()

    def showGlobalView(self):
        """Exibe controles gerais de rotação e escala."""
        self.editPanel.setCurrentIndex(0)

    def showLeadDetailView(self, leadId):
        """Exibe painel de edição específico para o `leadId` informado."""
        leadStartTime = self.imageViewer.getLeadRoiStartTime(leadId)
        self.EditPanelLeadView.setValues(leadId, leadStartTime)
        self.editPanel.setCurrentIndex(1)


    ###################
    # Image Functions #
    ###################

    def resetImageEditControls(self):
        """Restaura valores padrão e limpa indicadores de salvamento."""
        self.EditPanelGlobalView.rotationSlider.setValue(0)
        self.EditPanelGlobalView.clearTimeSpinBox()
        self.EditPanelGlobalView.clearVoltSpinBox()
        self.EditPanelGlobalView.setLastSavedTimeStamp(timeStamp=None)
        self.showGlobalView()

    def loadImageFromPath(self, path: Path):
        """Carrega imagem do disco e exibe no visualizador."""
        self.image = ImageUtilities.readImage(path)
        self.displayImage()

    def displayImage(self):
        """Mostra a imagem no `ImageView` e ajusta o zoom inicial."""
        self.imageViewer.setImage(self.image)
        self.editPanel.show()

        # Ajusta o zoom para enquadrar a imagem
        self.imageViewer.fitImageInView()

    def removeImage(self):
        """Remove a imagem atual do editor."""
        self.image = None
        self.imageViewer.removeImage()


    ######################
    # Lead ROI functions #
    ######################

    def addLead(self, leadIdEnum, x=0, y=0, width=400, height=200, startTime=0.0):
        """Adiciona uma ROI para a derivação especificada."""
        if self.imageViewer.hasImage():
            leadId = leadIdEnum.name

            # Desabilita ação de menu para evitar múltiplas caixas para mesmo lead
            self.mainWindow.leadButtons[leadIdEnum].setEnabled(False)

            # Cria instância da ROI e adiciona ao `ImageView`
            roiBox = ROIItem(self.imageViewer._scene, leadId)
            roiBox.setRect(x, y, width, height)
            roiBox.startTime = startTime

            self.imageViewer._scene.addItem(roiBox)
            roiBox.show()

    def updateLeadStartTime(self, leadId, value=None):
        """Atualiza o tempo inicial de uma ROI após alteração no painel."""
        if value is None:
            value = self.EditPanelLeadView.leadStartTimeSpinBox.value()

        self.imageViewer.setLeadRoiStartTime(leadId, value)

    def deleteLeadRoi(self, leadId):
        """Remove ROI do `ImageView` e reabilita botão de menu."""
        self.imageViewer.removeRoiBox(leadId)
        self.mainWindow.leadButtons[LeadId[leadId]].setEnabled(True)
        self.setControlPanel()  # Retorna para painel global

    def deleteAllLeadRois(self):
        """Remove todas as ROIs e reativa os botões de adição."""
        self.imageViewer.removeAllRoiBoxes()

        # Reabilita todos os botões de menu
        for _, button in self.mainWindow.leadButtons.items():
            button.setEnabled(True)

        self.setControlPanel()    # Retorna para painel global
