class Language(str):
    """Natural language of text, speach, or song."""

    def __init__(self, code: str):
        self.code: str = code

    def __eq__(self, other: "Language") -> bool:
        if not other:
            return False
        return self.code == other.code

    def __str__(self) -> str:
        """Get English name of the language or return code."""

        if self.code == "fr":
            return "French"

        return self.code

    def __hash__(self) -> int:
        return hash(self.code)

    @classmethod
    def __get_validators__(cls):
        yield cls
