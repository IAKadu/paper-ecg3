"""Modela um ECG completo, incluindo suas derivações e escalas de grade."""

class Ecg:
    # Escala de tempo padrão em mm/s
    DEFAULT_TIME_SCALE = 25
    # Escala de voltagem padrão em mm/mV
    DEFAULT_VOLTAGE_SCALE = 10

    def __init__(self):
        # Dicionário contendo os dados de cada derivação
        self.leads = {}
        # Escala vertical da grade (mm/mV)
        self.gridVoltageScale = Ecg.DEFAULT_VOLTAGE_SCALE
        # Escala horizontal da grade (mm/s)
        self.gridTimeScale = Ecg.DEFAULT_TIME_SCALE

    def printLeadInfo(self):
        """Imprime no console as informações armazenadas das derivações."""
        for lead in self.leads.items():
            print(lead)

