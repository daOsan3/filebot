import pathspec

def read_ignore_file(ignore_file_path):
    with open(ignore_file_path, 'r') as f:
        lines = f.read().splitlines()
    return lines

def filter_ignored_files(files, ignore_file_path):
    ignore_lines = read_ignore_file(ignore_file_path)
    spec = pathspec.PathSpec.from_lines('gitwildmatch', ignore_lines)
    return [f for f in files if not spec.match_file(f)]


if __name__ == '__main__':
    # Usage
    ignore_file_path = '.docubotignore'
    all_files = ['test.py', 'test.pyc', 'dir/to/ignore/file.txt', 'dir/to/include/file.txt']

    filtered_files = filter_ignored_files(all_files, ignore_file_path)

    print("Filtered files:", filtered_files)
