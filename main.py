#!/usr/bin/python
import os, sys, zipfile
from threading import Thread
from pathlib import Path


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


def extract_all_zip_files(dir_path):
    zip_files = []
    os.chdir('\\'.join([os.getcwd(), dir_path]))
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
    for root, dirs, files in os.walk(root_path, topdown=False): # deleting all the files (and directories) that werent moved because they caused exceptions
        if root == root_path:
            continue
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    # for name in dirs:  # delete the remaining empty folders in the root directory
    #     os.rmdir(os.path.join(root, name))


def main():
    dir_path = '.'
    if len(sys.argv) > 1:
        dir_path = sys.argv[1]
    user_input = 'n'
    while user_input != 'y':
        user_input = input(f'\nare you sure you wish to perform this action on the files at {os.path.join(os.getcwd(), dir_path)}'
                           f'\n enter y/n: ').lower()
        if user_input == 'n':
            exit(0)
    t1 = Thread(target=extract_all_zip_files, args=(dir_path,))
    t1.start()
    t1.join()
    unite_all_files_recursive()
    print("finished")


if __name__ == '__main__':
    main()
