from typing import Dict
import dataclasses

from model.Lead import LeadId, Lead


@dataclasses.dataclass(frozen=True)
class InputParameters:
    """Parâmetros de entrada necessários para a digitalização do ECG."""
    rotation: int  # ângulo de rotação aplicado à imagem
    timeScale: int  # escala de tempo (mm/s)
    voltScale: int  # escala de voltagem (mm/mV)
    leads: Dict[LeadId, Lead]  # mapeamento das derivações selecionadas

