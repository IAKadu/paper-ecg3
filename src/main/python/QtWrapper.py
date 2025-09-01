"""Coleção de utilitários para facilitar o uso do Qt.

O módulo concentra funções geradoras de widgets e *layouts* padrão,
abstraindo a criação repetitiva de componentes da interface gráfica.
Essas funções são frequentemente decoradas por :func:`bindsToClass`,
permitindo que o widget criado seja anexado automaticamente ao objeto
"dono".
"""
from typing import cast, List, Optional, Tuple, Union

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QAction, QComboBox, QGroupBox, QHBoxLayout, QLabel, QLayout, QMenu, QMenuBar, QMainWindow, QPushButton, QRadioButton, QScrollArea, QSizePolicy, QSlider, QSplitter, QTabWidget, QVBoxLayout, QWidget, QStackedWidget, QSpinBox, QDoubleSpinBox, QLineEdit, QFormLayout


class SplitterOrientation:
    """Enumeração simples para orientar ``QSplitter``."""

    Horizontal = QtCore.Qt.Horizontal
    Vertical = QtCore.Qt.Vertical


class Separator():
    """Tipo fictício usado para representar um separador de menu."""

    pass


class Tab:
    """Estrutura auxiliar para criação de abas em ``QTabWidget``."""

    def __init__(self, label: str, widget: QWidget):
        self.label = label
        self.widget = widget


def bindsToClass(createWidgetFunction):
    """Decorator que vincula o widget criado a um atributo do objeto.

    As funções decoradas devem receber como primeiros argumentos o
    ``owner`` (objeto que receberá o widget) e ``name`` (nome do atributo).

    Exemplo::

        @bindsToClass
        def createWidget(owner, name, other, parameters):
            ...

        class Window:
            def __init__(self):
                createWidget(self, "example", foo, bar)
                print(self.example)  # -> widget criado
    """

    def createAndBind(*args, **kwargs):
        owner, name = None, None

        # Extrai ``owner`` e ``name`` dos argumentos posicionais ou nomeados
        if "owner" in kwargs and "name" in kwargs:
            owner, name = kwargs["owner"], kwargs["name"]
        elif len(args) == 1 and "name" in kwargs:
            owner, name = args[0], kwargs["name"]
        elif len(args) >= 2:
            owner, name = args[:2]

        # Cria o widget chamando a função original
        widget = createWidgetFunction(*args, **kwargs)

        # Facilita a depuração caso a função retorne ``None`` (segfault em Qt)
        assert widget is not None, (
            f"Widget creation function '{createWidgetFunction.__name__}' returned None"
        )

        if owner is not None and name is not None and name != "":
            # Atribui ``owner.name = widget`` para facilitar o acesso futuro
            setattr(owner, name, widget)

        return widget

    return createAndBind


@bindsToClass
def ComboBox(
    items: List[str],
    owner: Optional[QWidget] = None,
    name: Optional[str] = None
) -> QComboBox:
    """Cria um ``QComboBox`` pré-preenchido com a lista de itens."""

    comboBox = QComboBox()
    comboBox.addItems(items)

    return comboBox


@bindsToClass
def SpinBox(
    owner: QWidget,
    name: str,
    minVal: int,
    maxVal: int,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    defaultValue: Optional[int] = None,
) -> QSpinBox:
    """Gera um ``QSpinBox`` numérico para valores inteiros."""

    spinbox = QSpinBox()
    spinbox.setMinimum(minVal)
    spinbox.setMaximum(maxVal)
    if prefix:
        spinbox.setPrefix(prefix)
    if suffix:
        spinbox.setSuffix(suffix)
    if defaultValue:
        spinbox.setValue(defaultValue)
    return spinbox


@bindsToClass
def DoubleSpinBox(
    owner: QWidget,
    name: str,
    minVal: float,
    maxVal: float,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    defaultValue: Optional[float] = None
) -> QDoubleSpinBox:
    """Versão com casas decimais de :func:`SpinBox`."""

    spinbox = QDoubleSpinBox()
    spinbox.setMinimum(minVal)
    spinbox.setMaximum(maxVal)
    if prefix:
        spinbox.setPrefix(prefix)
    if suffix:
        spinbox.setSuffix(suffix)
    if defaultValue:
        spinbox.setValue(defaultValue)
    return spinbox


@bindsToClass
def Custom(
    owner: QWidget,
    name: str,
    widget: QWidget
):
    """Envolve qualquer widget customizado para caber no paradigma do wrapper."""

    return widget


@bindsToClass
def GroupBox(
    title: str,  # Shown to user
    layout: QLayout,
    owner: QWidget = None,
    name: str = None
) -> QGroupBox:
    """Cria um ``QGroupBox`` contendo o *layout* informado."""

    groupBox = QGroupBox(title)
    groupBox.setLayout(layout)

    return groupBox


@bindsToClass
def HorizontalBoxLayout(
    owner: QWidget = None,
    name: str = None,
    margins: Optional[Tuple[int, int, int, int]] = None,
    contents: List[Union[QWidget, QLayout]] = []
) -> QHBoxLayout:
    """Cria um ``QHBoxLayout`` e adiciona conteúdos na horizontal.

    Args:
        owner: Classe que receberá o layout como atributo.
        name: Nome do atributo utilizado para armazenar o layout.
        margins: Margens (esquerda, topo, direita, base) em pixels.
        contents: Widgets ou layouts a serem adicionados.

    Returns:
        QHBoxLayout configurado.
    """
    horizontalBoxLayout = QHBoxLayout()

    if margins is not None:
        left, top, right, bottom = margins
        horizontalBoxLayout.setContentsMargins(left, top, right, bottom)

    for item in contents:
        if issubclass(type(item), QWidget):
            horizontalBoxLayout.addWidget(cast(QWidget, item))
        elif issubclass(type(item), QLayout):
            horizontalBoxLayout.addLayout(cast(QLayout, item))

    return horizontalBoxLayout


@bindsToClass
def HorizontalSlider(
    owner: QWidget = None,
    name: str = None,
) -> QSlider:
    """Retorna um ``QSlider`` orientado horizontalmente."""
    return QSlider(QtCore.Qt.Horizontal)


@bindsToClass
def HorizontalSplitter(
    contents=List[QWidget],
    owner: QWidget = None,
    name: str = None,
) -> QSplitter:
    """Agrupa widgets lado a lado utilizando ``QSplitter`` horizontal."""

    splitter = QSplitter(QtCore.Qt.Horizontal)

    # ``QSplitter`` só aceita widgets diretos como filhos
    for widget in contents:
        splitter.addWidget(widget)

    return splitter


@bindsToClass
def Label(
    text: str,
    owner: QWidget = None,
    name: str = None
) -> QLabel:
    """Cria um rótulo de texto simples."""

    return QLabel(text)


@bindsToClass
def Menu(
    items: List[Union[QAction, Separator]],
    owner: QWidget = None,
    name: str = None,
    displayName: str = None
) -> QMenu:
    """Cria um ``QMenu`` com itens e separadores."""

    menu = QMenu(displayName)  # aqui o owner é a janela principal
    for item in items:
        if type(item) is Separator:
            menu.addSeparator()
        elif type(item) is QAction:
            menu.addAction(cast(QAction, item))

    return menu


@bindsToClass
def MenuAction(
    shortcut: Optional[Union[str, QtGui.QKeySequence]],
    statusTip: Optional[str],
    owner: QWidget = None,
    name: str = None,
    displayName: str = None
) -> QAction:
    """Cria uma ação de menu configurável."""

    action = QAction(
        '&' + displayName, owner
    ) if displayName else QAction(owner)
    if shortcut:
        action.setShortcut(shortcut)
    if statusTip:
        action.setStatusTip(statusTip)

    return action


@bindsToClass
def MenuBar(
    owner: QMainWindow, menus: List[QMenu], name: str = None
) -> QMenuBar:
    """Monta a barra de menus principal da aplicação."""

    menuBar = owner.menuBar()  # type: QMenuBar
    for menu in menus:
        menuBar.addMenu(menu)

    return menuBar


@bindsToClass
def PushButton(
    owner: QWidget = None,
    name: str = None,
    icon: Optional[QtGui::QIcon] = None,
    text: str = "",
) -> QPushButton:
    """Cria um botão simples, com suporte opcional a ícone."""

    if icon is not None:
        button = QPushButton(icon, text)
    else:
        button = QPushButton(text)

    return button


@bindsToClass
def RadioButton(
    text: str, owner: QWidget = None, name: str = None
) -> QRadioButton:
    """Retorna um ``QRadioButton`` configurado."""

    return QRadioButton(text)


@bindsToClass
def ScrollArea(
    innerWidget: QWidget,
    owner: Optional[QWidget] = None,
    name: Optional[str] = None,
    horizontalScrollBarPolicy: Optional[QtCore.Qt.ScrollBarPolicy] = None,
    verticalScrollBarPolicy: Optional[QtCore.Qt.ScrollBarPolicy] = None,
    widgetIsResizable: Optional[bool] = None
) -> QScrollArea:
    """Adiciona um widget interno a uma área com barras de rolagem."""

    scrollArea = QScrollArea()

    if horizontalScrollBarPolicy is not None:
        scrollArea.setHorizontalScrollBarPolicy(horizontalScrollBarPolicy)

    if verticalScrollBarPolicy is not None:
        scrollArea.setVerticalScrollBarPolicy(verticalScrollBarPolicy)

    if widgetIsResizable is not None:
        scrollArea.setWidgetResizable(widgetIsResizable)

    scrollArea.setWidget(innerWidget)

    return scrollArea


@bindsToClass
def TabWidget(
    tabs: List[Tab],
    owner: Optional[QWidget] = None,
    name: Optional[str] = None,
) -> QTabWidget:
    """Cria um ``QTabWidget`` e adiciona as abas fornecidas."""

    tabWidget = QTabWidget()

    for tab in tabs:
        tabWidget.addTab(tab.widget, tab.label)

    return tabWidget


@bindsToClass
def StackedWidget(
    widgets: List[QWidget],
    owner: Optional[QWidget] = None,
    name: Optional[str] = None,
) -> QStackedWidget:
    """Empilha vários widgets, exibindo apenas um por vez."""

    stackedWidget = QStackedWidget()

    for widget in widgets:
        stackedWidget.addWidget(widget)

    return stackedWidget


@bindsToClass
def VerticalBoxLayout(
    owner: QWidget = None,
    name: str = None,
    margins: Optional[Tuple[int, int, int, int]] = None,
    contents: List[Union[QWidget, QLayout]] = []
) -> QVBoxLayout:
    """Versão vertical de :func:`HorizontalBoxLayout`."""
    verticalBoxLayout = QVBoxLayout()

    if margins is not None:
        left, top, right, bottom = margins
        verticalBoxLayout.setContentsMargins(left, top, right, bottom)

    for item in contents:
        if issubclass(type(item), QWidget):
            verticalBoxLayout.addWidget(cast(QWidget, item))
        elif issubclass(type(item), QLayout):
            verticalBoxLayout.addLayout(cast(QLayout, item))

    return verticalBoxLayout


@bindsToClass
def VerticalSplitter(
    contents=List[QWidget],
    owner: QWidget = None,
    name: str = None
) -> QSplitter:
    """Agrupa widgets verticalmente usando ``QSplitter``."""

    splitter = QSplitter(QtCore.Qt.Vertical)

    # ``QSplitter`` aceita somente widgets diretos, não layouts
    for widget in contents:
        splitter.addWidget(widget)

    return splitter


@bindsToClass
def Widget(
    owner: QWidget = None,
    name: str = None,
    horizontalPolicy: Optional[QSizePolicy.Policy] = None,
    verticalPolicy: Optional[QSizePolicy.Policy] = None,
    layout: Optional[QLayout] = None
) -> QWidget:
    """Cria um ``QWidget`` genérico com opções de ``sizePolicy`` e layout."""
    widget = QWidget()

    sizePolicy = widget.sizePolicy()

    if horizontalPolicy is not None:
        sizePolicy.setHorizontalPolicy(horizontalPolicy)

    if verticalPolicy is not None:
        sizePolicy.setVerticalPolicy(verticalPolicy)

    widget.setSizePolicy(sizePolicy)

    if layout is not None:
        widget.setLayout(layout)

    return widget


@bindsToClass
def LineEdit(
    owner: QWidget = None,
    name: str = None,
    contents: str = "",
    readOnly: bool = False
) -> QLineEdit:
    """Cria um campo de texto de linha única."""

    lineEdit = QLineEdit()
    lineEdit.setText(contents)
    lineEdit.setReadOnly(readOnly)
    return lineEdit

@bindsToClass
def FormLayout(
    contents: List[Tuple[QWidget, QWidget]],
    name: Optional[str] = None,
    owner: Optional[QWidget] = None
) -> QFormLayout:
    """Organiza pares de widgets em forma de formulário."""

    layout = QFormLayout()

    for item in contents:
        item1, item2 = item
        layout.addRow(item1, item2)

    return layout

