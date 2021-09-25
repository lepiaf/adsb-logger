from transformer.transformer import Transformer


class Velocity(Transformer):
    def support(self, obj) -> bool:
        if obj['velocity'] is None:
            return False

        return True

    def transform(self, obj):
        velocity = {
            'speed': obj['velocity'][0],
            'heading': obj['velocity'][1],
            'vertical_rate': obj['velocity'][2],
            'type': obj['velocity'][3],
        }
        obj['velocity'] = velocity

        return obj
