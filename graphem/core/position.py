from dataclasses import dataclass


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
