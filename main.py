import os
import progressbar
from shutil import copyfile
from glob import iglob
from osb_file_parser import osz_contains_storyboard


def copy_to_output_folder(files):
    for f in progressbar.progressbar(files):
        os.makedirs(f"output/{os.path.dirname(f)}", exist_ok=True)
        copyfile(f, f"output/{f}")


if __name__ == '__main__':
    all_osz = list(iglob('maps/**/**/*.osz', recursive=True))
    files = []
    error_log = open("error.log", "w")
    for file_path in progressbar.progressbar(all_osz):
        try:
            if osz_contains_storyboard(file_path):
                files.append(file_path)
        except Exception as error:
            error_log.write(f"ERROR: \n{file_path}\n{error}\n\n")

    copy_to_output_folder(files)
