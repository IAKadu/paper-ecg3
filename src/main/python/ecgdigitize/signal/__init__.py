"""Rotinas de alto nível para manipulação de sinais de ECG.

Este pacote reexporta funções convenientes do submódulo ``signal``
para facilitar o acesso a operações comuns relacionadas ao
processamento do traçado, como extração e normalização.
"""

from .signal import (
    ecgSignalSamplingPeriod,
    extractSignalFromImage,
    verticallyScaleECGSignal,
    zeroECGSignal,
)
