from dataclasses import dataclass


type postuple = tuple[float,float]


@dataclass(slots=True)
class Position:
    x:float = 0
    y:float = 0

    @property
    def val(self) -> postuple:
        return self.x, self.y
    @val.setter
    def val(self, val:postuple):
        self.x, self.y = val


def ttop(t:postuple|Position) -> Position:
    # Casts any iterable or Position object to a Position object
    if isinstance(t, Position):
        return t
    return Position(*t)

