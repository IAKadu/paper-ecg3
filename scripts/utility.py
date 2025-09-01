# Funções utilitárias para validação de números em texto.

from typing import List, TypeVar

T = TypeVar("T")


def _acceptableNumber(
    text: str,
    negationAllowed: bool = True,
    periodAllowed: bool = True,
    containsDigits: bool = False,
) -> bool:
    """Verifica se um texto pode representar um número válido.

    A análise é feita recursivamente, caracter por caracter, respeitando as
    restrições de sinal e ponto decimal.
    """

    if text == "":
        return containsDigits

    x = text[0]

    if x == "-":
        return negationAllowed and _acceptableNumber(
            text[1:], False, periodAllowed, containsDigits
        )
    if x == ".":
        return periodAllowed and _acceptableNumber(text[1:], False, False, containsDigits)
    if x.isdigit():
        return _acceptableNumber(text[1:], False, periodAllowed, True)

    return False


def isFloat(x: str) -> bool:
    """Indica se a string representa um número de ponto flutuante."""

    return _acceptableNumber(x)


def isInt(x: str) -> bool:
    """Indica se a string representa um número inteiro."""

    return _acceptableNumber(x, negationAllowed=True, periodAllowed=False)


def isPositive(x: str) -> bool:
    """Indica se a string representa um inteiro não negativo."""

    return _acceptableNumber(x, negationAllowed=False, periodAllowed=False)


def allTrue(elements: List[bool]) -> bool:
    """Retorna ``True`` se todos os elementos da lista forem verdadeiros."""

    return elements.count(False) == 0

