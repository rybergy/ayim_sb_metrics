from zipfile import ZipFile
from constants import blank_lines

'''
class Storyboard:

    file = ''

    def __init__(self, file):
        self.file = file

    def initialize_file(self):
        # Open file to find headers
        # Based on headers, simply read for sprites
        # Also requires to open .osu files
        pass

    def is_empty(self):
        return False
'''


def clean_line(line):
    # Compressed opens have byte-objects. Decode them.
    try:
        line = line.decode().strip()
    except AttributeError:
        pass
    return line.strip()


def contains_storyboard_helper(file):
    for line in file:
        line = clean_line(line)
        # Suggests some form of sprites that exist
        if '[Variables]' in line:
            return True

        if '[Events]' in line:
            # Events check, reached the important point in an .osu or .osb file

            next_line = clean_line(file.readline())

            if next_line is not '//Storyboard Layer 0 (Background)':
                # Keep going until you hit that or [TimingPoints]
                while next_line != '//Storyboard Layer 0 (Background)' and next_line != '[TimingPoints]':
                    next_line = clean_line(file.readline())

            # At this point a "blank OSB" or .osu file should match up for checking, so just check the next
            # len(blank_lines) whether it matches, and if it doesn't, then surely there's sprites inside.

            lines = [next_line]
            for l in range(len(blank_lines) - 1):
                lines.append(clean_line(file.readline()))

            return lines != blank_lines

    # Reaching here means file has no [Events] tab anyway?
    return False


def contains_storyboard(file_path):
    # TODO: This is a function wrapper. a bad one too lol
    with open(file_path, 'r+') as file:
        contains_storyboard_helper(file)


def osz_contains_storyboard(file_path):
    with ZipFile(file_path) as beatmap:
        # Take the beatmap, get all the filenames with .osu or .osb extension
        files = [beatmap.open(f, 'r') for f in beatmap.namelist() if f.endswith('osu')
                 or f.endswith('osb')]
        return any([contains_storyboard_helper(f) for f in files])
