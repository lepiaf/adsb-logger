import unittest

from transformer.velocity import Velocity


class VelocityTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.transformer = Velocity()

    def test_support(self):
        data_provider = [
            {'obj': {'velocity': [0.0, 0.0, 0.0, '']}, 'expected': True},
            {'obj': {'velocity': None}, 'expected': False},
            {'obj': {}, 'expected': False}
        ]

        for data in data_provider:
            self.assertEqual(self.transformer.support(data['obj']), data['expected'])

    def test_transform(self):
        data_provider = [
            {
                'obj': {
                    'velocity': [0.0, 0, 0, 'GS']
                },
                'expected': {
                    'velocity': {
                        'speed': 0.0,
                        'heading': 0.0,
                        'vertical_rate': 0,
                        'type': 'GS',
                    }
                }
            },
        ]

        for data in data_provider:
            self.assertEqual(self.transformer.transform(data['obj']), data['expected'])
