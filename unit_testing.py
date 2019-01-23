import unittest
from osb_file_parser import contains_storyboard, osz_contains_storyboard


class StoryboardChecks(unittest.TestCase):
    def test_blank_osb_file(self):
        self.assertFalse(contains_storyboard("test/blank_osb.osb"))

    def test_has_osb_file(self):
        self.assertTrue(contains_storyboard("test/good_osb.osb"))

    def test_no_sb_osu(self):
        self.assertFalse(contains_storyboard("test/no_sb.osu"))

    def test_optimized_osb(self):
        self.assertTrue(contains_storyboard("test/optimized_osb.osb"))

    def test_sb_osu(self):
        self.assertTrue(contains_storyboard("test/sb.osu"))


class OszBeatmapChecks(unittest.TestCase):
    def test_no_storyboards(self):
        self.assertFalse(osz_contains_storyboard("test/osz/530071 Kevin Manthei - Invader Zim Theme Song.osz"))

    def test_has_storyboard(self):
        self.assertTrue(osz_contains_storyboard("test/osz/582089 Camellia vs Akira Complex - Reality Distortion.osz"))


if __name__ == '__main__':
    unittest.main()
