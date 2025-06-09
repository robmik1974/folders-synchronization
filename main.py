import argparse
import pathlib
import os
import hashlib
import shutil
import time
import logging

"""
Author : robertmikolajczyk <ronert1674@gmail.com>
Date   : 2025-05-29
Purpose: Folders Synchronization
"""

def setup_logging(log_file: str) -> logging.Logger:
    """Set up logging configuration"""

    logger = logging.getLogger('folder_sync')
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def dir_path(path: str) -> str:
    """Validate if the given path is a directory."""

    if os.path.isdir(path):
        return path
    raise argparse.ArgumentTypeError(f"{path} is not a valid path")


def get_argpars():
    """Parse command line arguments."""
    
    parser = argparse.ArgumentParser(
        description="Folders Synchronization",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("source", 
                        metavar="source", 
                        type=dir_path, 
                        help="Path to the source folder"
    )

    parser.add_argument("destination",
                        metavar="destination",
                        type=dir_path,
                        help="Path to the destination folder",
    )

    parser.add_argument("interval",
                        metavar="interval",
                        type=float,
                        help="Interval between synchronizations",
    )

    parser.add_argument("amount", 
                        metavar="amount", 
                        type=int, 
                        help="Amount of synchronizations"
    )

    parser.add_argument("logfile", 
                        metavar="logfile", 
                        type=str, 
                        help="Path to log file")

    return parser.parse_args()

 
def get_hash(file_path: str, algorithm: str = "sha256") -> str:
    """Calculate hash of a file using the specified algorithm."""

    hash_func = hashlib.new(algorithm)
    try:
        with open(file_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except (FileNotFoundError, PermissionError) as e:
        raise e


def synchronize_destination_folder(source_folder: str, dest_folder: str, logger: logging.Logger) -> None:
    """Synchronize destination folder with source folder."""

    try:
        for item in pathlib.Path(dest_folder).iterdir():
            source_path = list(pathlib.PurePath(item).parts)
            source_path[0] = source_folder
            if os.path.isfile(item):
                if not os.path.exists(pathlib.Path(*source_path)):
                    logger.info(f"File will be removed: {item}")
                    os.remove(item)
            else:
                if len(os.listdir(item)) == 0:
                    if not os.path.exists(pathlib.Path(*source_path)):
                        logger.info(f"Empty folder will be removed: {item}")
                        os.rmdir(item)
                else:
                    synchronize_destination_folder(source_folder, item, logger)

    except (PermissionError, OSError) as e:
        logger.error(f"Error processing {dest_folder}: {str(e)}")


def process_file(item: pathlib.Path, dest_folder: str, logger: logging.Logger) -> None:
    """Process a single file for synchronization."""
    try:
        hash = item, get_hash(item)
        dest_path = list(pathlib.PurePath(hash[0]).parts[:-1])
        dest_path[0] = dest_folder
        file = pathlib.PurePath(hash[0]).parts[-1]
        dest_path = pathlib.Path(*dest_path)
        full_dest_path = dest_path.joinpath(file)

        if not os.path.exists(dest_path):
            logger.info(f"Path will be created: {dest_path}")
            os.makedirs(dest_path)

        if not os.path.exists(full_dest_path):
            logger.info(f"File will be created: {full_dest_path}")
            shutil.copy(hash[0], dest_path)
        else:
            if hash[1] != get_hash(full_dest_path):
                logger.info(f"File will be updated: {full_dest_path}")
                os.remove(full_dest_path)
                shutil.copy(hash[0], dest_path)
    except (PermissionError, OSError) as e:
        logger.error(f"Error processing file {item}: {str(e)}")


def process_empty_folder(item: pathlib.Path, dest_folder: str, logger: logging.Logger) -> None:
    """Process an empty folder for synchronization."""
    try:
        dest_path = list(pathlib.PurePath(item).parts)
        dest_path[0] = dest_folder
        dest_path = pathlib.Path(*dest_path)

        if not os.path.exists(dest_path):
            logger.info(f"Empty folder will be created: {dest_path}")
            os.makedirs(dest_path)
    except (PermissionError, OSError) as e:
        logger.error(f"Error processing empty folder {item}: {str(e)}")


def process_source_items(source_folder: str, dest_folder: str, logger: logging.Logger) -> None:
    """Process all items in the source folder."""
    for item in pathlib.Path(source_folder).rglob("*"):
        try:
            if os.path.isfile(item):
                process_file(item, dest_folder, logger)
            elif len(os.listdir(item)) == 0:
                process_empty_folder(item, dest_folder, logger)
        except (PermissionError, OSError) as e:
            logger.error(f"Error processing {item}: {str(e)}")
            continue


def perform_synchronization(source_folder: str, dest_folder: str, logger: logging.Logger) -> None:
    """Perform a single synchronization cycle."""
    try:
        synchronize_destination_folder(source_folder, dest_folder, logger)
        process_source_items(source_folder, dest_folder, logger)
    except Exception as e:
        logger.error(f"Unexpected error during synchronization: {str(e)}")
        raise


def main():
    """Main function to run the folder synchronization."""
    args = get_argpars()
    logger = setup_logging(args.logfile)
    
    source_folder = args.source
    dest_folder = args.destination
    interval = args.interval
    amount = args.amount
    
    logger.info(f"Starting synchronization from {source_folder} to {dest_folder}")

    for _ in range(amount):
        try:
            perform_synchronization(source_folder, dest_folder, logger)
            logger.info(f"Sleeping for {interval} seconds")
            time.sleep(interval)
        except Exception as e:
            logger.error("Synchronization failed - stopping")
            break

if __name__ == "__main__":
    main()
