import os
import re
import bs4
import json
import argparse
import pandas as pd
from typing import List
from bs4 import BeautifulSoup
from pathlib import Path

def get_exclusions() -> List[str]:
    with open('exclude_files.txt', 'r') as f:
        exclusions = [line.strip() for line in f.readlines()]
    return exclusions

def get_doctype(soup: bs4.BeautifulSoup) -> str:
    items = [item for item in soup.contents if isinstance(item, bs4.Doctype)]
    return items[0] if items else None

def handle_content(idx: int, row: pd.Series, PREFIX: str, errors: List[str], exclusions: List[str]) -> None:
    content = row['content']
    # Check the first 500 bytes for <!DOCTYPE
    if '\n<!DOCTYPE' in content[:500] and "PUBLIC" in content[:500]:
        try:
            # Parse content with BeautifulSoup
            soup = BeautifulSoup(content, 'lxml')
            doctype = get_doctype(soup)
            if doctype:
                # Remove prefix from DOCTYPE
                root = doctype.removeprefix(PREFIX).strip()
                if root:
                    # Remove the second string enclosed in double quotes
                    root = root.split('"')[0]
                    # Replace every sub-string of non-alpha-numeric characters with a dash
                    root = re.sub('\W+', '-', root)
                    # Check against exclusion list
                    if any(root.startswith(exclusion) for exclusion in exclusions):
                        return
                    # Split the root to create directory structure
                    dir_name, file_name = root.split(" ", 1)
                    # Remove PUBLIC or SYSTEM from the file_name
                    file_name = file_name.replace("PUBLIC", "").replace("SYSTEM", "").strip()
                    # Create directories and save the content
                    dir_path = f'xml/{dir_name}/{file_name}/{row["max_stars_repo_name"]}/{row["max_stars_repo_path"]}'
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    # Save content
                    xml_file_name = f'{dir_path}/{os.path.basename(row["max_stars_repo_path"])}'
                    with open(xml_file_name, 'w') as file:
                        file.write(content)
                    print(f"Saved content to: {xml_file_name}")
                    # Save the row data to a JSON file
                    json_file_name = xml_file_name.replace('.xml', '.json')
                    row.to_json(json_file_name)
                    print(f"Saved metadata to: {json_file_name}")
        except Exception as e:
            error_message = f"Error at index {idx} - {str(e)}"
            errors.append(error_message)
            dir_path = 'xml/__BAD'
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            # Save content
            with open(f'{dir_path}/content_{idx}.txt', 'w') as file:
                file.write(content)
            # Save the row data to a JSON file
            json_file_name = f'{dir_path}/metadata_{idx}.json'
            row.to_json(json_file_name)
            print(f"Saved error and metadata to: {json_file_name}")

def main():
    parser = argparse.ArgumentParser(description='Process parquet files.')
    parser.add_argument('filenames', metavar='N', type=str, nargs='+',
                        help='an input parquet filename')
    args = parser.parse_args()

    exclusions = get_exclusions()

    errors = []
    for filename in args.filenames:
        df = pd.read_parquet(filename)
        PREFIX = "<!DOCTYPE "
        for idx, row in df.iterrows():
            handle_content(idx, row, PREFIX, errors, exclusions)

    print("\nErrors:")
    for error in errors:
        print(error)

if __name__ == "__main__":
    main()
