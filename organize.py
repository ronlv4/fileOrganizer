#!/usr/bin/python

import argparse
import errno
import os
import zipfile
from pathlib import Path
from threading import Thread
from typing import List

verbose_print = lambda *a: None
dir_path: Path
num_of_threads: int


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
        zip_ref.extractall(str(file_name)[:-4])
    print(f'finished extracting {file_name}')


def get_zip_files_list(zip_path_list: List[Path]):
    verbose_print(f'getting zip files list from {dir_path}')
    zip_path_list[:] = [dir_path / Path(file_name) for file_name in os.listdir(dir_path) if file_name.endswith('.zip')]
    verbose_print(f'found {len(zip_path_list)} zip files')


def get_threads_list(zip_path_list: List[Path]):
    min_zip_files_per_thread = len(zip_path_list) // num_of_threads
    zip_files_groups = [zip_path_list[i * min_zip_files_per_thread:(i + 1) * min_zip_files_per_thread] for i in
                        range(0, num_of_threads)]
    for i in range(len(zip_path_list) % num_of_threads):
        zip_files_groups[i].append(zip_path_list[-(i + 1)])
    verbose_print(f'min zip files per thread: {min_zip_files_per_thread}')
    verbose_print(f'created {len(zip_files_groups)} zip files groups')
    verbose_print(f'number of files per group: {[len(group) for group in zip_files_groups]}')
    return [Thread(target=extract_group_of_zip_files, args=(zip_files_group,)) for zip_files_group in zip_files_groups]


def extract_group_of_zip_files(zip_path_list: List[Path]):
    for zip_path in zip_path_list:
        extract_zip(zip_path)


def extract_all_zip_files(zip_path_list: List[Path]):
    verbose_print(f'extracting {len(zip_path_list)} zip files')
    verbose_print(f'using {num_of_threads} threads')
    threads = get_threads_list(zip_path_list)
    verbose_print(f'created {len(threads)} threads')
    verbose_print('starting threads')
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    verbose_print('all threads finished executing')


def unite_all_files_recursive():
    for root, dirs, files in os.walk(dir_path, topdown=False):
        root = Path(root)
        for file in files:
            try:
                os.rename(root.joinpath(file), dir_path.joinpath(file))
            except OSError as e:
                if e.errno == errno.EEXIST:
                    os.remove(e.filename)
        for dir in dirs:
            dir = Path(root).joinpath(dir)
            if not os.listdir(dir):
                os.rmdir(dir)


def print_usage_and_exit():
    print(f'{Format.RED}usage: python organize.py <path to directory containing zip files>{Format.NOCOLOR}')
    exit(1)


def get_user_confirmation(message):
    user_input = 'n'
    while user_input != 'y':
        print(message)
        user_input = input(f'{Format.YELLOW}enter y/n: {Format.NOCOLOR}').lower()
        if user_input == 'n':
            exit(0)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=f'{Format.GREEN}Originally made to organize "Google takeout" photos and videos into a single directory{Format.NOCOLOR}')
    parser.usage = f'{Format.RED}organize.py <path to directory containing zip files>{Format.NOCOLOR}'
    parser.add_argument('dir_path', type=str, help='path to directory containing zip files')
    parser.add_argument('-t', '--threads', type=int, default=3, help='number of threads to use')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    arguments = parser.parse_args()
    global verbose_print, dir_path, num_of_threads
    dir_path = Path(arguments.dir_path)
    num_of_threads = arguments.threads
    if arguments.verbose:
        verbose_print = lambda *args: print(', '.join(args))
    if not 1 <= arguments.threads <= 10:
        print(f'{Format.RED}number of threads must be between 1 and 10{Format.NOCOLOR}')
        exit(1)


def delete_original_zip_files(zip_files_list: List[Path]):
    get_user_confirmation(message=f'{Format.BOLD}Would you like to delete the zip files?{Format.NOCOLOR}')
    for zip_path in zip_files_list:
        os.remove(zip_path)
    print(f'{Format.GREEN}deleted {len(zip_files_list)} zip files{Format.NOCOLOR}')


def main():
    parse_arguments()
    zip_files_list = []
    get_user_confirmation(message=f'Are you sure you wish to perform this action on the files at {dir_path}?')
    get_zip_files_list(zip_files_list)
    extract_all_zip_files(zip_files_list)
    unite_all_files_recursive()
    print("finished")
    print(f'{Format.GREEN}all files were extracted to {dir_path}{Format.NOCOLOR}')
    delete_original_zip_files(zip_files_list)


if __name__ == '__main__':
    main()
