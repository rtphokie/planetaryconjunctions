import unittest
from src import main
from pprint import pprint


class MyTestCase(unittest.TestCase):
    def test_something(self):
        main()

    def test_comb(self):
        from itertools import combinations
        arr=['mercury', 'venus', 'moon', 'mars', 'jupiter', 'saturn']
        foo = (list(combinations(arr, 2)))
        for x in foo:
            # print(f"{x[0]} - {x[1]}")
            print(f"separation_{x[0].lower()}_{x[1].lower()}(t)")
            # print(f'''def separation_{x[0].lower()}_{x[1].lower()}(t):
    # return separation(t, '{x[0].upper()}', '{x[1].upper()}')
    #         ''')


if __name__ == '__main__':
    unittest.main()
