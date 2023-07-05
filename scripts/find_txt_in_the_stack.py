from functools import partial
import os
import re
import warnings
import bs4
import json
import argparse
import pandas as pd
from typing import Hashable, List
from pathlib import Path
import concurrent.futures
from find_xml_in_the_stack import get_exclusions




def handle_content(
    idx: Hashable, row: pd.Series,
) -> None:
    content = row["content"]
    path = Path(row["max_stars_repo_path"])
    repo = row["max_stars_repo_name"]
    # Create directories and save the content
    if len(content)<200:
        return
    
    if "readme" not in path.name.lower():
        return

    parent_dir = f"text/{repo}/{path.parent}"
    Path(parent_dir).mkdir(parents=True, exist_ok=True)
    # Save content
    file_name = f"{parent_dir}/{path.name}"
    with open(file_name, "w") as file:
        file.write(content)
        # print(f"Saved content to: {file_name}")
        # Save the row data to a JSON file
    json_file_name = f"{file_name}.json"
    row["content"] = None
    row.to_json(json_file_name)


def main():
    parser = argparse.ArgumentParser(description="Process parquet files.")
    parser.add_argument(
        "filenames", metavar="N", type=str, nargs="+", help="an input parquet filename"
    )
    parser.add_argument(
        "--parallel", action="store_true", default=False, help="Enable parallel processing. May be slower!"
    )

    args = parser.parse_args()

    exclusions = get_exclusions()

    if  args.parallel:
        func = partial(handle_parquet, exclusions=exclusions)

        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            tuple(executor.map(func , args.filenames))
        print("DONE")
    else:
        for filename in args.filenames:
            handle_parquet(filename, exclusions)

def handle_parquet(filename: str, exclusions: List[str]):
    print("Parsing", filename)
    df = pd.read_parquet(filename)

    for idx, row in df.iterrows():
        handle_content(idx, row)


if __name__ == "__main__":
    main()
