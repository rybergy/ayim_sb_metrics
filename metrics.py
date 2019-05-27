from glob import iglob
import progressbar
from osb_file_parser import Storyboard, get_storyboard_files

# LIST OF METRICS:
#  - Most common sprite name

sprite_counts_total = {} # Total sprite count among all sbs
sprite_counts_per_sb = {} # Total sprite count, counting 1 per sb
handled_cur_mapset = set()
cur_mapset = ''

def print_metrics_to_file(results, filename):
    with open(f'metrics/{filename}.txt', 'w+') as f:
        for i in range(len(results)):
            # Print them in reverse, since we want reverse sorted
            res = results[-i - 1]
            f.write(res[0] + ': ' + str(res[1]) + ' times\n')

def increment_dict(dict, key):
    if key in dict:
        dict[key] += 1
    else:
        dict[key] = 1

def calculate_all_metrics(file_paths):
    error_log = open('errormetrics.log', 'w+')
    for file_path in file_paths:
        try:
            calculate_metrics_for_mapset(file_path)
        except Exception as error:
            error_log.write(f"ERROR: \n{file_path}\n{error}\n\n")

    total = sorted(sprite_counts_total.items(), key =
                    lambda kv: (kv[1], kv[0]))
    per_sb = sorted(sprite_counts_per_sb.items(), key =
                    lambda kv: (kv[1], kv[0]))
    print_metrics_to_file(total, 'total-sprite-count')
    print_metrics_to_file(per_sb, 'per-sb-sprite-count')

def calculate_metrics_for_mapset(file_path):
    maps = get_storyboard_files(file_path)
    handled_cur_mapset.clear()
    global cur_mapset
    cur_mapset = file_path
    for beatmap in maps:
        calculate_metrics_for_beatmap(beatmap)

def calculate_metrics_for_beatmap(sb):
    calculate_common_sprite_name(sb)

def calculate_common_sprite_name(sb: Storyboard):
    for line in sb.repl_ev_lines:
        if not line.startswith(' '):
            parts = line.split(',')
            # Take the sprite path between quotes
            sprite_path = parts[3][1:-1]
            # Find the last slash (can mix either forward or back slash)
            forwardslash_pos = sprite_path.rfind('/')
            last_slash_pos = forwardslash_pos if forwardslash_pos != -1 else sprite_path.rfind('\\')
            # Find the name after the last slash
            sprite_name = sprite_path[last_slash_pos + 1:] if last_slash_pos != -1 else sprite_path
            # Check if we've found this sprite in the current mapset
            if sprite_name not in handled_cur_mapset:
                increment_dict(sprite_counts_per_sb, sprite_name)
                handled_cur_mapset.add(sprite_name)
            # Add to total sprite count regardless
            increment_dict(sprite_counts_total, sprite_name)

if __name__ == '__main__':
    all_osz = list(iglob('output/**/*.osz', recursive=True))
    files = []
    error_log = open("error.log", "w")
    for file_path in progressbar.progressbar(all_osz):
        try:
            files.append(file_path)
        except Exception as error:
            error_log.write(f"ERROR: \n{file_path}\n{error}\n\n")

    calculate_all_metrics(files)

    