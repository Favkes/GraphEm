from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(slots=True)
class Position:
    x:float = 0
    y:float = 0

    @property
    def val(self) -> tuple[float,float]:
        return self.x, self.y
    @val.setter
    def val(self, val:tuple[float,float]):
        self.x, self.y = val


def ttop(t:Iterable[float]|Position) -> Position:
    # Casts any iterable or Position object to a Position object
    if isinstance(t, Position):
        return t
    return Position(*t)

