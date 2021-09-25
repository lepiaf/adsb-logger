from transformer.transformer import Transformer


class Position(Transformer):
    def support(self, obj) -> bool:
        if obj['position'] is None:
            return False

        return True

    def transform(self, obj):
        position = {
            'type': 'Point',
            'coordinates': [obj['position'][1], obj['position'][0], (obj['alt']*0,3048)]
        }
        obj['position'] = position

        return obj
