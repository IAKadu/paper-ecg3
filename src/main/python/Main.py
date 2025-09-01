"""
Main.py
Criado em 1 de novembro de 2020

Ponto de entrada da aplicação.
"""

import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext

from controllers.MainController import MainController


if __name__ == '__main__':
    context = ApplicationContext()

    # Converte os caminhos de recursos para um formato utilizável pelo PyInstaller
    def resource(relativePath):
        return context.get_resource(relativePath)

    # Inicializa o controlador principal e a janela associada
    controller = MainController()

    # Inicia o loop de eventos do Qt e mantém a aplicação em execução
    exit_code = context.app.exec_()

    # Mostra o código de saída e encerra o programa
    print(f"Exiting with status {exit_code}")
    sys.exit(exit_code)

