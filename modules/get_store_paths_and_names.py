import os

def get_store_paths_and_names(directory_path):
    """
    Traverses a directory one-level deep and returns two lists:
    1. Relative paths of the directories found.
    2. Names of the directories found.

    Args:
        directory_path (str): Path to the directory to traverse.

    Returns:
        tuple: Two lists - one with relative paths, and another with directory names.
    """
    relative_paths = []  # List to hold relative paths of the directories found
    dir_names = []  # List to hold names of the directories found

    if os.path.isdir(directory_path):
        for entry in os.scandir(directory_path):
            if entry.is_dir():
                relative_paths.append(entry.path)
                dir_names.append(entry.name)

    return relative_paths, dir_names