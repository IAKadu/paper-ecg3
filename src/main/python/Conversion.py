"""Rotinas de conversão de imagens de ECG em séries de sinais."""

from pathlib import Path

import numpy as np
from numpy.lib.arraysetops import isin  # importado para compatibilidade

import ecgdigitize
import ecgdigitize.signal
import ecgdigitize.image
from ecgdigitize import common, visualization
from ecgdigitize.image import ColorImage, Rectangle

from model.InputParameters import InputParameters


def convertECGLeads(inputImage: ColorImage, parameters: InputParameters):
    """Extrai e alinha os sinais de todas as derivações da imagem."""

    # 1) Aplica rotação para corrigir inclinação do papel
    rotatedImage = ecgdigitize.image.rotated(inputImage, parameters.rotation)

    # 2) Recorta cada derivação conforme os parâmetros fornecidos
    leadImages = {
        leadId: ecgdigitize.image.cropped(
            rotatedImage, Rectangle(lead.x, lead.y, lead.width, lead.height)
        )
        for leadId, lead in parameters.leads.items()
    }

    extractSignal = ecgdigitize.digitizeSignal
    extractGrid = ecgdigitize.digitizeGrid

    # 3) Transforma cada recorte em dados de sinal
    signals = {leadId: extractSignal(img) for leadId, img in leadImages.items()}

    # Se todas as derivações falharam, encerra
    if all(isinstance(signal, common.Failure) for signal in signals.values()):
        return None, None

    # Imagens de pré-visualização com o traçado sobreposto
    previews = {
        leadId: visualization.overlaySignalOnImage(signal, image)
        for (leadId, image), (_, signal) in zip(leadImages.items(), signals.items())
    }

    # 4) Estima o espaçamento da grade para cada derivação
    gridSpacings = {
        leadId: extractGrid(image)
        for leadId, image in leadImages.items()
    }
    spacings = [
        spacing for spacing in gridSpacings.values() if not isinstance(spacing, common.Failure)
    ]

    if len(spacings) == 0:
        return None, None

    samplingPeriodInPixels = gridHeightInPixels = common.mean(spacings)

    # 5) Redimensiona verticalmente os sinais para volts
    scaledSignals = {
        leadId: ecgdigitize.signal.verticallyScaleECGSignal(
            ecgdigitize.signal.zeroECGSignal(signal),
            gridHeightInPixels,
            parameters.voltScale,
            gridSizeInMillimeters=1.0,
        )
        for leadId, signal in signals.items()
    }

    samplingPeriod = ecgdigitize.signal.ecgSignalSamplingPeriod(
        samplingPeriodInPixels, parameters.timeScale, gridSizeInMillimeters=1.0
    )

    # 6) Alinha os sinais com zero padding à esquerda e à direita
    paddedSignals = {
        leadId: common.padLeft(
            signal, int(parameters.leads[leadId].startTime / samplingPeriod)
        )
        for leadId, signal in scaledSignals.items()
    }

    maxLength = max(len(s) for s in paddedSignals.values())
    fullSignals = {
        leadId: common.padRight(signal, maxLength - len(signal))
        for leadId, signal in paddedSignals.items()
    }

    return fullSignals, previews


def exportSignals(leadSignals, filePath, separator='\t'):
    """Exporta os sinais digitalizados para um arquivo de texto."""

    leads = common.zipDict(leadSignals)
    leads.sort(key=lambda pair: pair[0].value)

    assert len(leads) >= 1
    lengthOfFirst = len(leads[0][1])

    # Verifica se todos os sinais possuem o mesmo tamanho
    assert all(len(signal) == lengthOfFirst for _, signal in leads)

    collated = np.array([signal for _, signal in leads])
    output = np.swapaxes(collated, 0, 1)

    if not issubclass(type(filePath), Path):
        filePath = Path(filePath)

    if filePath.exists():
        print("Warning: Output file will be overwritten!")

    outputLines = [
        separator.join([str(val) for val in row]) + "\n"
        for row in output
    ]

    with open(filePath, 'w') as outputFile:
        outputFile.writelines(outputLines)

