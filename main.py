import argparse
import pathlib
import os
import hashlib

"""
Author : robertmikolajczyk <ronert1674@gmail.com>
Date   : 2025-05-29
Purpose: Folders Synchronization
"""


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")


def get_argpars():

    parser = argparse.ArgumentParser(
        description="Folders Synchronization",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "source", metavar="source", type=dir_path, help="Path to the source folder"
    )

    parser.add_argument(
        "destination",
        metavar="destination",
        type=dir_path,
        help="Path to the destination folder",
    )

    parser.add_argument(
        "interval",
        metavar="interval",
        type=int,
        help="Interval between synchronizations",
    )

    parser.add_argument(
        "amount", metavar="amount", type=int, help="Amount of synchronizations"
    )

    parser.add_argument("logfile", metavar="logfile", type=str, help="Path to log file")

    return parser.parse_args()


def get_hash(file_path, algorithm="sha256"):
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as fh:
        data = fh.read()
        hash_func.update(data)
        return hash_func.hexdigest()


def main():

    files = {}

    args = get_argpars()
    source_folder = args.source
    dest_folder = args.destination
    interval = args.interval
    amount = args.amount
    log_file = args.logfile
    # print(f"Source folder: {source_folder}")
    # print(f"Destination folder: {dest_folder}")
    # print(f"Interval: {interval}")
    # print(f"Amount of synchronization: {amount}")
    # print(f"Log file: {log_file}")

    for item in pathlib.Path(source_folder).rglob("*"):
        if os.path.isfile(item):
            files[item] = get_hash(item)


    print(files)
# Create output to the file and to the standard console with infomration related to

if __name__ == "__main__":
    main()
