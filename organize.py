#!/usr/bin/python
import argparse
import os, sys, zipfile
from threading import Thread
from pathlib import Path

verbose_print = lambda *a: None


class Format:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[98m'
    NOCOLOR = '\033[0m'
    BOLD = '\033[1m'
    GRAY = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    FLASHING = '\033[5m'


def create_folder_per_zip(zip_files):
    for file in os.scandir('.'):
        if file.is_dir():
            continue
        name, type = file.name.split('.')
        if not type == 'zip':
            continue
        zip_files.append(file.name)
        os.makedirs(name, exist_ok=True)


def extract_zip(file_name):
    print(f'extracting {file_name}')
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(file_name[:-4])
    print(f'finished extracting {file_name}')

def get_zip_files_list(dir_path, zip_files_names_list):
    zip_files_names_list[:] = [file[:-4] for file in os.listdir(dir_path) if file.endswith('.zip')]
    verbose_print(f'found {len(zip_files_names_list)} zip files', 'another string')
def extract_all_zip_files(dir_path):
    create_folder_per_zip(zip_files)
    threads = [Thread(target=extract_zip, args=(file,)) for file in zip_files]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def unite_all_files_recursive():
    root_path = os.getcwd()
    for root, dirs, files in os.walk(root_path, topdown=False):
        for file in files:
            try:
                os.rename(os.path.join(root, file), '\\'.join([root_path, file]))
            except OSError:
                pass
    for root, dirs, files in os.walk(root_path,
                                     topdown=False):  # deleting all the files (and directories) that werent moved because they caused exceptions
        if root == root_path:
            continue
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    # for name in dirs:  # delete the remaining empty folders in the root directory
    #     os.rmdir(os.path.join(root, name))


def print_usage_and_exit():
    print(f'{Format.RED}usage: python organize.py <path to directory containing zip files>{Format.NOCOLOR}')
    exit(1)

def get_user_confirmation(dir_path):
    user_input = 'n'
    while user_input != 'y':
        user_input = input(f'Are you sure you wish to perform this action on the files at {os.path.join(os.getcwd(), dir_path)}\n{Format.YELLOW}enter y/n: {Format.NOCOLOR}').lower()
        if user_input == 'n':
            exit(0)
def parse_arguments():
    parser = argparse.ArgumentParser(description=f'{Format.GREEN}Originally made to organize "Google takeout" photos and videos into a single directory{Format.NOCOLOR}')
    parser.usage = f'{Format.RED}organize.py <path to directory containing zip files>{Format.NOCOLOR}'
    parser.add_argument('dir_path', type=str, help='path to directory containing zip files')
    parser.add_argument('-t', '--threads', type=int, default=3, help='number of threads to use')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    arguments = parser.parse_args()
    global verbose_print
    if arguments.verbose:
        verbose_print = lambda *args: print(', '.join(args))
    if not 1 <= arguments.threads < 10:
        print(f'{Format.RED}number of threads must be between 1 and 10{Format.NOCOLOR}')
        exit(1)
    return arguments
def main():
    args = parse_arguments()
    dir_path = Path(args.dir_path)
    zip_files_names_list = []
    get_user_confirmation(dir_path)
    get_zip_files_list(dir_path, zip_files_names_list)
    exit(0)
    t1 = Thread(target=extract_all_zip_files, args=(dir_path,))
    t1.start()
    t1.join()
    unite_all_files_recursive()
    print("finished")


if __name__ == '__main__':
    main()
