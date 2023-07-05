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


def get_exclusions() -> List[str]:
    with open("exclude_files.txt", "r") as f:
        exclusions = [line.strip().lower() for line in f.readlines()]
    return tuple(filter(None, exclusions))


def get_doctype(soup: bs4.BeautifulSoup) -> str:
    items = [item for item in soup.contents if isinstance(item, bs4.Doctype)]
    return items[0] if items else None


def sniff_document_type(soup: bs4.BeautifulSoup):
    doctype = get_doctype(soup)
    if not doctype:
        return (None, None)

    doctype = doctype.lower()
    root = doctype.split()[0]
    assert root, breakpoint()
    if "dita" in doctype:
        return ("dita", root)
    elif "docbook" in doctype:
        return ("docbook", root)
    elif "jats" in doctype:
        return ("jats", root)
    elif "www.tei-c.org" in doctype:
        return ("tei", root)
    elif "html" in doctype:
        return ("html", root)
    
    return (None, None)
    


def handle_content(
    idx: Hashable, row: pd.Series, PREFIX: str, exclusions: List[str]
) -> None:
    content = row["content"]
    # Check the first 500 bytes for <!DOCTYPE
    docstart = content[:500]
    if (
        ("<!DOCTYPE" in docstart and "OASIS" in docstart)
        or "<TEI" in docstart
        or "//NLM//DTD" in docstart
    ):
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
            # Parse content with BeautifulSoup
                soup = bs4.BeautifulSoup(content, "lxml")
            family, root = sniff_document_type(soup)
            if family:
                # Find doctype to make doctype directories
                if root in exclusions:
                    return

                path = Path(row["max_stars_repo_path"])
                repo = row["max_stars_repo_name"]
                # Create directories and save the content
                parent_dir = f"xml/{family}/{root}/{repo}/{path.parent}"
                Path(parent_dir).mkdir(parents=True, exist_ok=True)
                # Save content
                xml_file_name = f"{parent_dir}/{path.name}"
                with open(xml_file_name, "w") as file:
                    file.write(content)
                # print(f"Saved content to: {xml_file_name}")
                # Save the row data to a JSON file
                json_file_name = f"{xml_file_name}.json"
                row["content"] = None
                row.to_json(json_file_name)
                # print(f"Saved metadata to: {json_file_name}")
        except Exception as e:
            error_message = f"Error at index {idx} - {str(e)}"
            print(error_message)
            dir_path = "xml/__BAD"
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            # Save content
            with open(f"{dir_path}/content_{idx}.txt", "w") as file:
                file.write(content)
            # Save the row data to a JSON file
            json_file_name = f"{dir_path}/metadata_{idx}.json"
            row["ERROR"] = e
            row.to_json(json_file_name)
            print(f"Saved error and metadata to: {json_file_name}")


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



PREFIX = "<!DOCTYPE "


def handle_parquet(filename: str, exclusions: List[str]):
    print("Parsing", filename)
    df = pd.read_parquet(filename)

    for idx, row in df.iterrows():
        handle_content(idx, row, PREFIX, exclusions)


if __name__ == "__main__":
    main()
