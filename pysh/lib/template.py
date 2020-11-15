
class Template:
    def __init__(self, reg):
        self._reg = reg

    @staticmethod
    def create():
        return


class Clz(Template):
    def __init__(self):
        super().__init__("1")