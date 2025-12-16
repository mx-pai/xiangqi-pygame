from dataclasses import dataclass

@dataclass(frozen=True)
class Theme:
    name: str
    piece_style: str

    @staticmethod
    def style_1():
        return Theme(name="风格一", piece_style="stype_1")

    @staticmethod
    def style_2():
        return Theme(name="风格二", piece_style="stype_2")

    @staticmethod
    def style_3():
        return Theme(name="风格三", piece_style="stype_3")