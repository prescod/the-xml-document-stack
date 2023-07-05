import argparse
from find_xml_in_the_stack import handle_content, get_exclusions
from huggingface_hub import hf_hub_download
from datasets import load_dataset
from time import time
from pathlib import Path

local = Path("dataset_bin")
local.mkdir(exist_ok=True)

def download_parquets(top: int):
    for i in range(0, top):
        filename=f"data/xml/train-00{i:03}-of-00297.parquet"
        print(filename)
        hf_hub_download(
            repo_id="bigcode/the-stack",
            repo_type="dataset",
            filename=filename,
            local_dir=local,
            local_dir_use_symlinks=True,
        )

# ds = load_dataset("bigcode/the-stack", streaming=True, split="train")
# ds2 = ds.filter(lambda row: row["lang"].lower() == "xml")
# a = next(iter(ds2))

# create the parser
parser = argparse.ArgumentParser(description="Set the top of the index.")

# add a command-line argument
parser.add_argument("--index_top", type=int, default=296, help="The top of the index")

# parse the arguments
args = parser.parse_args()

# use args.index_top where you previously used i
download_parquets(args.index_top)
