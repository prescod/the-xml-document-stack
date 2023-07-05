import os
import argparse
from typing import List
from prettytable import PrettyTable
import pandas as pd

# Define the function to calculate the number of files and the size of the data
def get_dir_info(dir_path: str, exclude_ext: List[str]) -> (int, float):
    num_files = 0
    data_size = 0

    # Walk through the directory
    for root, dirs, files in os.walk(dir_path):
        files = [f for f in files if not any(f.endswith(ext) for ext in exclude_ext)]
        num_files += len(files)
        data_size += sum(os.path.getsize(os.path.join(root, name)) for name in files)

    # Convert size to megabytes
    data_size_mb = data_size / (1024 * 1024)

    return num_files, data_size_mb

def main(dir_path: str, exclude_ext: List[str], tab_delimited: bool, html_output: str):
    # Define column headers
    table_headers = ["Directory", "Number of Files", "Data Size (MB)"]

    rows = []

    # Get the subdirectories
    subdirectories = [os.path.join(dir_path, d) for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]

    # For each subdirectory, get and print the info
    for subdir in subdirectories:
        num_files, data_size = get_dir_info(subdir, exclude_ext)
        rows.append([subdir, num_files, f"{data_size:.2f}"])

    if html_output:
        df = pd.DataFrame(rows, columns=table_headers)
        df.to_html(html_output, index=False)
    elif tab_delimited:
        print('\t'.join(table_headers))
        for row in rows:
            print('\t'.join(map(str, row)))
    else:
        table = PrettyTable()
        table.field_names = table_headers
        for row in rows:
            table.add_row(row)
        print(table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate the number of files and size of data in subdirectories.")
    parser.add_argument("--dir", default='xml', help="Base directory to calculate file and data sizes.")
    parser.add_argument("--exclude_ext", nargs='*', default=['json'], help="File extensions to exclude.")
    parser.add_argument("--tab", action='store_true', help="Print the output as a tab-delimited table.")
    parser.add_argument("--html", default='', help="Path to the output HTML file.")

    args = parser.parse_args()

    main(args.dir, args.exclude_ext, args.tab, args.html)
