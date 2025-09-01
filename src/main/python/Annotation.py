"""metadata.py
=================

Módulo responsável por guardar e manipular *metadados* associados às
derivações ECG utilizadas no processo de extração.  Metadados referem-se a
informações fornecidas manualmente pelo usuário – como localização do
recorte ou parâmetros de escala – em oposição aos dados contidos na imagem
em si.  As estruturas abaixo seguem o paradigma de ``dataclasses`` do
Python, que simplifica a criação de classes voltadas ao armazenamento de
informações.
"""
from os import path
import dataclasses
import json
import pathlib
import datetime
from typing import Any, Dict, List, Optional, Union

from model import Lead


# Versão atual do esquema de anotação salvo; permite futura evolução da
# estrutura de dados sem quebrar compatibilidade com arquivos antigos.
VERSION = 0


def noneValuesRemoved(dictionary: Dict[Any, Any]) -> Dict[Any, Any]:
    """Remove entradas cujos valores são ``None``.

    Muitos campos são opcionais, e ao exportarmos para JSON é útil evitar
    chaveamentos com valor ``null``.  Esta função retorna um novo dicionário
    contendo apenas os pares realmente preenchidos.
    """
    return {key: value for key, value in dictionary.items() if value is not None}


@dataclasses.dataclass(frozen=True)
class CropLocation():
    """Representa a região recortada de um traçado.

    Os atributos ``x`` e ``y`` correspondem às coordenadas do canto superior
    esquerdo do recorte dentro da imagem original.  ``width`` e ``height``
    definem, em pixels, o tamanho da área que contém o sinal.
    """

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self):
        """Garante que todos os campos foram informados como inteiros."""
        assert isinstance(self.x, int)
        assert isinstance(self.y, int)
        assert isinstance(self.width, int)
        assert isinstance(self.height, int)


@dataclasses.dataclass(frozen=True)
class ImageMetadata():
    """Informações básicas sobre a imagem utilizada no processo.

    Attributes:
        name: Nome do arquivo de imagem.
        directory: Caminho do diretório onde o arquivo se encontra.
        hashValue: Hash opcional para verificar integridade.
    """

    name: str
    directory: Optional[str] = None
    hashValue: Optional[Any] = None


@dataclasses.dataclass(frozen=True)
class LeadAnnotation:
    """Anotação de uma derivação individual.

    Cada derivação possui a região de recorte correspondente ao seu traçado e
    o instante de início do sinal, em segundos ou amostras, dentro da faixa
    temporal global.
    """

    cropping: CropLocation
    start: Union[float, int]


@dataclasses.dataclass(frozen=True)
class Schema:
    """Identifica de forma única o formato do arquivo de anotação."""

    name: str
    version: int

    def __post_init__(self):
        """Valida que o esquema possui nome simples e versão inteira."""
        assert isinstance(self.name, str)
        assert '.' not in self.name
        assert isinstance(self.version, int)

    def __repr__(self) -> str:
        return f"{self.name}.{self.version}"


@dataclasses.dataclass(frozen=True)
class Annotation:
    """Agrupa todas as informações anotadas pelo usuário.

    Um objeto ``Annotation`` funciona como um *snapshot* do trabalho em
    andamento, possibilitando que o usuário continue a digitalização em um
    momento futuro.  Abaixo está um exemplo de construção:

    ```
    Annotation(
        ImageMetadata("fullscan.png"),  # Diretório e hash são opcionais
        0.0,   # Rotação aplicada à imagem
        25.0,  # Escala de tempo (mm/s)
        10.0,  # Escala de voltagem (mm/mV)
        {
            Lead.LeadName.I: LeadAnnotation(
                CropLocation(0, 0, 20, 40),
                0.0
            ),
            Lead.LeadName.III: LeadAnnotation(
                CropLocation(0, 0, 20, 40),
                0.0
            )
        }
    )
    ```
    """

    schema: Schema = dataclasses.field(
        default=Schema("paper-ecg-user-annotation", VERSION), init=False
    )

    # Momento em que a anotação foi criada; usado para referência do usuário
    timeStamp: str
    # Informações da imagem de entrada
    image: ImageMetadata
    # Rotação aplicada à imagem para alinhamento correto
    rotation: Union[int, float]
    # Escala temporal definida na interface (mm/s)
    timeScale: Union[int, float]
    # Escala de voltagem (mm/mV)
    voltageScale: Union[int, float]
    # Dicionário que mapeia cada derivação à sua anotação específica
    leads: Dict[Lead.LeadId, LeadAnnotation]

    def toDict(self):
        """Converte a anotação para um ``dict`` serializável.

        É necessário tratar alguns campos manualmente: os IDs das derivações
        (enums) são convertidos para ``str`` e dados opcionais com ``None`` são
        removidos para evitar ruído na representação JSON.
        """
        dictionary = dataclasses.asdict(self)

        # Converter enum de cada lead para string
        dictionary["leads"] = {
            lead.name: dataclasses.asdict(annotation) for lead, annotation in self.leads.items()
        }
        # Remover campos opcionais vazios da imagem
        dictionary["image"] = noneValuesRemoved(dataclasses.asdict(self.image))

        return dictionary

    def save(self, filePath: pathlib.Path):
        """Grava a anotação em disco no formato JSON."""
        dictionary = self.toDict()
        jsonSerial = json.dumps(dictionary)

        # ``pathlib`` simplifica a escrita de arquivos de forma portátil
        with filePath.open('w') as file:
            file.write(jsonSerial)

