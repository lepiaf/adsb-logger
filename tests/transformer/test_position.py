import unittest

from transformer.position import Position


class PositionTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.transformer = Position()

    def test_support(self):
        data_provider = [
            {'obj': {'position': [0.0, 0.0]}, 'expected': True},
            {'obj': {'position': None}, 'expected': False},
            {'obj': {}, 'expected': False}
        ]

        for data in data_provider:
            self.assertEqual(self.transformer.support(data['obj']), data['expected'])

    def test_transform(self):
        data_provider = [
            {
                'obj': {'position': [0.0, 0.0]},
                'expected': {'alt': 0.0, 'position': {'coordinates': [0.0, 0.0, 0.0], 'type': 'Point'}}
            },
            {
                'obj': {'position': [0.0, 0.0], 'alt': 30000},
                'expected': {'alt': 30000, 'position': {'coordinates': [0.0, 0.0, 9144.0], 'type': 'Point'}}
            },
        ]

        for data in data_provider:
            self.assertEqual(self.transformer.transform(data['obj']), data['expected'])
