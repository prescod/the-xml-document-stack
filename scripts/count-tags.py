import argparse
from collections import Counter
from typing import Dict
from bs4 import BeautifulSoup
from pathlib import Path

def count_elements_in_dita_files(dir_path: str) -> Dict[str, int]:
    # Initialise a Counter to count the tags
    tag_counter = Counter()

    # Convert the string path to a Path object
    dir_path = Path(dir_path)

    # Loop over each DITA file in the directory and subdirectories
    for file_path in dir_path.rglob('*.dita'):
        print(file_path)
        if file_path.is_dir():
            continue
        with open(file_path, 'r', encoding='utf-8') as file:
            # Parse the file with BeautifulSoup
            soup = BeautifulSoup(file, 'xml')

            # Loop over each tag in the file
            for tag in soup.find_all():
                # Increment the counter for this tag
                if tag.name=="html":
                    breakpoint()
                tag_counter[tag.name] += 1

    return tag_counter


def main():
    # Define command line arguments
    parser = argparse.ArgumentParser(description='Count the usage of every element in a directory of DITA files.')
    parser.add_argument('dir_path', type=str, help='The path to the directory containing the DITA files.')

    # Parse command line arguments
    args = parser.parse_args()

    # Count the elements in the DITA files
    tag_counter = count_elements_in_dita_files(args.dir_path)

    tags = [(count, tag) for tag, count in tag_counter.items()]

    # Print out the count of each tag
    for count, tag in sorted(tags):
        print(f'{tag}: {count}')


if __name__ == "__main__":
    main()
