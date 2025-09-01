"""Funções utilitárias genéricas usadas por todo o projeto.

Este módulo centraliza pequenos auxiliares matemáticos e de manipulação de
listas/iteráveis. Os comentários explicam cada passo para facilitar a leitura
de quem não está acostumado com algumas construções de Python.
"""
from collections import Counter
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Sequence, Tuple, TypeVar, Union

from dataclasses import dataclass
import numpy as np
from numpy import mean, median

# Types
List = list
Int = int
Float = float
Numeric = Union[Float, Int]

A = TypeVar("A")
B = TypeVar("B")


@dataclass(frozen=True)
class Failure:
    """Representa uma falha genérica retornada por funções do módulo."""

    # Texto descritivo do motivo da falha
    reason: str


def reversedRange(stop: int) -> Sequence[int]:
    """Gera uma sequência decrescente de ``stop - 1`` até ``0``."""

    return range(stop - 1, -1, -1)


def inclusiveRange(start: int, stop: int) -> Sequence[int]:
    """Versão do ``range`` que inclui o valor final ``stop``."""

    return range(start, stop + 1)


def neg(inputValue: Int) -> Int:
    """Retorna o valor negativo de ``inputValue``."""

    return -1 * inputValue


def upperClamp(value: Numeric, limit: Numeric) -> Numeric:
    """Restringe ``value`` para não ultrapassar ``limit`` superior."""

    return value if (value < limit) else limit


def lowerClamp(value: Numeric, limit: Numeric) -> Numeric:
    """Garante que ``value`` não seja menor que ``limit`` inferior."""

    return value if (value > limit) else limit


def mapList(elements: Iterable[A], func: Callable[[A], B]) -> List[B]:
    """Aplica ``func`` a cada item e retorna o resultado como ``list``."""

    return list(map(func, elements))


def flatten(listOfLists: Iterable[Iterable[A]]) -> Iterable[A]:
    """Achata uma lista de listas em um único gerador de elementos."""

    return (e for _list in listOfLists for e in _list)


def flatMap(elements: Iterable[A], func: Callable[[A], Iterable[Iterable[B]]]) -> Iterable[B]:
    """Combina ``map`` e ``flatten`` para funções que retornam iteráveis."""

    # TODO: melhorar tipagem quando possível
    return flatten(mapList(elements, func))


def filterList(elements: Iterable[A], func: Callable[[A], A]) -> List[A]:
    """Filtra elementos que satisfazem ``func`` retornando nova lista."""

    return list(filter(func, elements))


def calculateDistancesBetweenValues(sortedList: Union[List, np.ndarray]) -> List[float]:
    """Calcula distâncias entre valores adjacentes em uma lista ordenada."""

    spacings = [y - x for (x, _), (y, _) in zip(sortedList[0:-1], sortedList[1:])]
    return spacings


def mode(data: Union[List, np.ndarray]) -> Numeric:
    """Obtém o valor mais frequente da coleção ``data``."""

    # TODO: revisar tipagem para suportar outros iteráveis
    value, _ = Counter(data).most_common(1)[0]  # retorna [(valor, ocorrências), ...]
    return value


def shiftedPairs(
    signal: Union[List, np.ndarray], limit: Optional[int] = None
) -> Iterator[Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]]:
    """Gera pares do sinal original deslocado incrementalmente.

    Útil para operações como autocorrelação. ``limit`` define quantos
    deslocamentos serão produzidos; por padrão é metade do tamanho do sinal.
    """

    limit = len(signal) // 2 if limit is None else limit

    if limit > len(signal) // 2:
        raise ValueError("'limit' é maior que metade do tamanho de 'signal'")

    for offset in range(limit):
        if offset == 0:
            # Sem deslocamento: par original
            yield signal, signal
        else:
            # Remove ``offset`` elementos do início/fim para alinhar
            yield signal[:-offset], signal[offset:]


def autocorrelation(signal: np.ndarray, limit: int = None) -> np.ndarray:
    """Calcula a autocorrelação de ``signal`` para diferentes deslocamentos."""

    return np.array([np.corrcoef(x, y)[0][1] for x, y in shiftedPairs(signal, limit)])


def zipDict(dictionary: Dict) -> Iterable[Tuple[Any, Any]]:
    """Converte um dicionário em lista de pares ``(chave, valor)``."""

    return [(key, value) for key, value in dictionary.items()]


def padLeft(
    elements: Union[List, np.ndarray], count: int, fillValue: float = 0
) -> Union[List, np.ndarray]:
    """Preenche ``count`` posições à esquerda usando ``fillValue``."""

    if type(elements) is np.ndarray:
        return np.pad(elements, (count, 0), constant_values=fillValue)
    else:
        return ([fillValue] * count) + elements


def padRight(
    elements: Union[List, np.ndarray], count: int, fillValue: float = 0
) -> Union[List, np.ndarray]:
    """Preenche ``count`` posições à direita usando ``fillValue``."""

    if type(elements) is np.ndarray:
        return np.pad(elements, (0, count), constant_values=fillValue)
    else:
        return elements + ([fillValue] * count)


def emptyOrNone(elements: Sequence[Any]) -> bool:
    """Verifica se a sequência está vazia ou é ``None``."""

    return len(elements) == 0 or elements is None
