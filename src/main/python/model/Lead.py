"""
lead.py

Tipo que representa uma derivação de ECG.
"""

from enum import Enum
import dataclasses


class LeadId(Enum):
    """Enumeração com os diferentes nomes das derivações.

    O `Enum` oferece funcionalidades úteis:

      - Verificar se uma string é um membro válido:
        ```
        nome in LeadId.__members__
        ```

      - Converter uma string em enumeração:
        ```
        minha_lead = LeadId[nome]
        ```
    """

    I   = 0
    II  = 1
    III = 2
    aVR = 3
    aVL = 4
    aVF = 5
    V1  = 6
    V2  = 7
    V3  = 8
    V4  = 9
    V5  = 10
    V6  = 11

    def __repr__(self) -> str:
        names = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
        return names[self.value]


@dataclasses.dataclass(frozen=True)
class Lead:
    """Representa a região de interesse selecionada para uma derivação."""
    x: int      # posição X inicial da ROI
    y: int      # posição Y inicial da ROI
    width: int  # largura da região selecionada
    height: int # altura da região selecionada
    startTime: int  # instante inicial (ms) do sinal nesse trecho

