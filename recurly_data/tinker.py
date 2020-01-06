"""Module"""
import os
import pickle


class Tinker:
    """Tinker"""
    def __init__(self):
        self.letter_a = "Letter A"
        self.__pickle = "info.pickle"

    @property
    def letter_b(self):
        """letter_b"""
        data = {}
        if os.path.exists(self.__pickle):
            with open(self.__pickle, "rb") as handle:
                data = pickle.load(handle)
        return data

    @letter_b.setter
    def letter_b(self, data):
        with open(self.__pickle, "wb") as handle:
            pickle.dump(
                data, handle, protocol=pickle.HIGHEST_PROTOCOL
            )

    def tinker_func(self):
        """tinker_func"""
        return f"Tinker class: {self.letter_a} and {self.letter_b}"


if __name__ == "__main__":
    TINKER = Tinker()
    print(TINKER)
    print(dir(TINKER))
    print(TINKER.letter_a)
    TINKER.letter_b = ({"Letter": "B"}, {"Letter": "C"})
    print(TINKER.letter_b[0]["Letter"])
    print(TINKER.letter_b[1]["Letter"])
