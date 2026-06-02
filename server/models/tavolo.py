from dataclasses import dataclass

@dataclass
class Tavolo:
    numero: int
    capienza: int
    coord_x: int
    coord_y: int
    stato: str
