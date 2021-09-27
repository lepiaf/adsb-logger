from transformer.transformer import Transformer


class Position(Transformer):
    def support(self, obj) -> bool:
        if 'position' not in obj or obj['position'] is None:
            return False

        return True

    def transform(self, obj):
        if 'alt' not in obj or obj['alt'] is None:
            obj['alt'] = 0.0

        position = {
            'type': 'Point',
            'coordinates': [obj['position'][1], obj['position'][0], obj['alt'] * 0.3048]
        }
        obj['position'] = position

        return obj
