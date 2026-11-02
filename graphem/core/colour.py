from dataclasses import dataclass


@dataclass(slots=True)
class Colour:
    r:int = 255
    g:int = 255
    b:int = 255

    @staticmethod
    def clip(value):
        return max(0, min(255, round(value)))

    def __setattr__(self, key, value):
        if key in ("r", "g", "b"):
            value = self.clip(value)
        object.__setattr__(self, key, value)

    @property
    def val(self):
        return self.r, self.g, self.b
    @val.setter
    def val(self, val:tuple[int,int,int]):
        # clip all values first to catch errors before mutations
        r, g, b = (self.clip(v) for v in val)

        # use setattr directly to omit redundant clip calls
        object.__setattr__(self, "r", r)
        object.__setattr__(self, "r", r)
        object.__setattr__(self, "r", r)