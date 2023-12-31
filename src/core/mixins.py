class JSONRepresentationMixin:
    def to_json(self) -> dict:
        return {
            column: value
            for column, value in self.__dict__.items()
            if not column.startswith("_")
        }
