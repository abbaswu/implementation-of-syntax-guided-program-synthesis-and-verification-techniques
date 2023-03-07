'''
Credits: https://stackoverflow.com/questions/19189274/nested-defaultdict-of-defaultdict

Usage:

my_dict = RecursiveDefaultDict()
my_dict['a']['b'] = 1
my_dict['a']['c']['d'] = 2
my_dict['b']

print(my_dict)  # {'a': {'b': 1, 'c': {'d': 2}}, 'b': {}}
'''

from collections import defaultdict


class RecursiveDefaultDict(defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(RecursiveDefaultDict, *args, **kwargs)

    def __repr__(self):
        return repr(dict(self))

