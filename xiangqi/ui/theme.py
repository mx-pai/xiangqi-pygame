from dataclasses import dataclass

@dataclass(frozen=True)
class Theme:
    name: str
    piece_style: str
    inset: dict[str, float]

    @staticmethod
    def style_1():
        return Theme(name="风格一",
                    piece_style="stype_1",
                    inset={"l":0.07, "r":0.06, "t":0.09, "b":0.10})

    @staticmethod
    def style_2():
        return Theme(name="风格二",
                     piece_style="stype_2",
                     inset={"l":0.06, "r":0.067, "t":0.057, "b":0.059})

    @staticmethod
    def style_3():
        return Theme(name="风格三",
                    piece_style="stype_3",
                    inset={"l":0.045, "r":0.05, "t":0.045, "b":0.046})