def is_binary_file(file_path, chunk_size=1024):
    """
    Determine if a file is a binary file.

    Parameters:
        file_path (str): The path to the file to check.
        chunk_size (int): The size of the chunk to read from the file for checking.

    Returns:
        bool: True if the file is binary, False otherwise.
    """
    text_characters = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x7f)) - {34, 39, 60, 62, 92})
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            if b'\x00' in chunk:  # Check for null bytes
                return True
            elif not chunk:  # An empty file is considered a text file
                return False

            # Check for non-text characters (>30%)
            nontext = chunk.translate(None, text_characters)
            return len(nontext) / len(chunk) > 0.30
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return False
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return False

if __name__ == '__main__':
    file_path = input("Enter the file path to check: ")
    if is_binary_file(file_path):
        print(f"{file_path} is a binary file.")
    else:
        print(f"{file_path} is not a binary file.")
