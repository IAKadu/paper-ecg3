"""Funções auxiliares para estimar a frequência da grade do ECG."""

from typing import List, Optional, Union

import numpy as np
import scipy.signal
import scipy.interpolate


def _findFirstPeak(signal: np.ndarray, minHeight: float = 0.3, prominence: float = 0.05) -> Optional[int]:
    """Localiza o primeiro pico acima de um limiar mínimo."""
    peaks, _ = scipy.signal.find_peaks(signal, prominence=prominence, height=minHeight)
    if len(peaks) == 0:
        return None
    else:
        return peaks[0]


def _estimateFirstPeakLocation(
    signal: np.ndarray,
    interpolate: bool = True,
    interpolationRadius: int = 2,
    interpolationGranularity: float = 0.01,
) -> Optional[float]:
    """Estima a posição do primeiro pico com maior precisão."""
    assert interpolationRadius >= 1

    index = _findFirstPeak(signal)
    if index is None:
        return None

    if interpolate:
        # Ajusta uma parábola aos pontos ao redor do pico para refinar a posição
        start, end = index - interpolationRadius, index + interpolationRadius
        func = scipy.interpolate.interp1d(range(start, end + 1), signal[start:end + 1], kind="quadratic")
        newX = np.arange(start, end, interpolationGranularity)
        newY = func(newX)

        newPeak = newX[np.argmax(newY)]

        # -- Depuração --
        # import matplotlib.pyplot as plt
        # plt.plot(range(start, end + 1), signal[start:end + 1])
        # plt.plot(newX, newY)
        # plt.show()

        return newPeak

    else:
        return index

