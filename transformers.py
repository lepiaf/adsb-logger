class Transformers:
    def __init__(self) -> None:
        self.transformers = []

    def transform(self, obj):
        for transformer in self.transformers:
            if not transformer.support(obj):
                continue

            obj = transformer.transform(obj)

        return obj
