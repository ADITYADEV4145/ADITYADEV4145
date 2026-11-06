import unittest
from pathlib import Path
from rotate_gif import GIFS, START, END, rotate


class RotationTests(unittest.TestCase):
    def setUp(self):
        self.original = (Path(__file__).resolve().parents[1] / 'README.md').read_text()

    def test_full_cycle_preserves_surrounding_readme(self):
        content = self.original
        before = content.split(START)[0]
        after = content.split(END)[1]
        visited = []
        for _ in GIFS:
            content, url = rotate(content)
            visited.append(url)
            self.assertEqual(content.split(START)[0], before)
            self.assertEqual(content.split(END)[1], after)
        self.assertEqual(len(set(visited)), len(GIFS))
        self.assertEqual(content, self.original)

    def test_missing_duplicate_or_reversed_markers_are_rejected(self):
        for content in ['missing', self.original + START, END + START]:
            with self.subTest(content=content[:30]), self.assertRaises(ValueError):
                rotate(content)

    def test_unknown_image_is_rejected(self):
        content = self.original
        for url, _ in GIFS:
            content = content.replace(url, 'https://example.com/unknown.gif')
        with self.assertRaises(ValueError):
            rotate(content)


if __name__ == '__main__':
    unittest.main()
