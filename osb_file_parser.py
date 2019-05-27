from zipfile import ZipFile
from constants import blank_lines, ignore_lines, text_events, text_variables
from enum import Enum, auto

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
        line = line.decode().replace('\n', '').replace('\r', '')
    except AttributeError:
        pass
    return line.replace('\n', '').replace('\r', '')


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


class Storyboard:

    def __init__(self, name, var_lines, ev_lines):
        self.name = name
        self.var_size = 0
        self.var_lines = var_lines
        self.ev_lines = ev_lines
        self.vars = {}
        self._register_vars()
        self.repl_ev_lines = []
        self.ev_size = 0
        self.repl_ev_size = 0
        self._replace_evs()

    def _register_vars(self):
        for line in self.var_lines:
            midpoint = line.index('=')
            var_name = line[1:midpoint]
            var_value = line[midpoint + 1:] 
            self.vars[var_name] = var_value
            self.var_size += len(line)

    def _replace_evs(self):
        for line in self.ev_lines:
            newline = line
            while '$' in newline:
                newline = self._replace_ev(newline)
            self.repl_ev_lines.append(newline)
            self.ev_size += len(line)
            self.repl_ev_size += len(newline)


    def _replace_ev(self, line):
        start = line.index('$') + 1
        cur_idx = start + 1
        while line[start:cur_idx] not in self.vars:
            cur_idx += 1
        var_name = line[start:cur_idx]
        var_value = self.vars[var_name]
        return line[:start - 1] + var_value + line[cur_idx:]



def get_storyboard(file):

    class State(Enum):
        Normal = auto()
        Variables = auto()
        Events = auto()

    var_lines = []
    ev_lines = []
    # Ignore the first couple events until we get to the first layer
    ignore_events = False
    state = State.Normal
    for bline in file:
        line = clean_line(bline).replace('\n', '').replace('\r', '')
        # Check for section headers
        if line.startswith('[') and line.endswith(']'):
            # Check if we need to change state of current section
            stripped = line[1:-1]
            # Entering variables / events section
            if stripped == text_variables:
                state = State.Variables
            elif stripped == text_events:
                state = State.Events
            # Any other section
            else:
                # If we're in the events or variables section, we're done
                if state != State.Normal:
                    break
        elif line.startswith('//'):
            if line in ignore_lines:
                ignore_events = True
            elif line in blank_lines:
                ignore_events = False
        elif line != '':
            # Check if we're hitting the background layer
            if line == blank_lines[0]:
                ignore_events = False
            if state == State.Variables:
                var_lines.append(line)
            elif state == State.Events and not ignore_events:
                ev_lines.append(line)

    sb = Storyboard(file.name, var_lines, ev_lines)
    return sb if sb.ev_lines != [] or sb.var_lines != [] else None


def get_storyboard_files(file_path):
    with ZipFile(file_path) as beatmap:
        files = [beatmap.open(f, 'r') for f in beatmap.namelist() 
            if f.endswith('osu') or f.endswith('osb')]
        sbs = []
        for f in files:
            sb = get_storyboard(f)
            if sb is not None:
                sbs.append(sb)
        return sbs