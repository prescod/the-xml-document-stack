import os
import hashlib
from collections import defaultdict

def find_duplicates(directory):
    # Dict where keys are file sizes and values are filenames
    files_by_size = defaultdict(list)
    
    # Walk through the directory and populate files_by_size
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            try:
                # Get the size of the file
                file_size = os.path.getsize(full_path)
            except OSError as e:
                print(f"Error: {e}")
                continue
            
            # Add to the dict
            files_by_size[file_size].append(full_path)


    # Now check for duplicates within each size
    for size, files in files_by_size.items():
        if len(files) > 1:
            hashes = defaultdict(list)
            for file in files:
                try:
                    with open(file, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    hashes[file_hash].append(file)
                except OSError as e:
                    print(f"Error: {e}")
                    continue

            # Now report duplicates
            for file_hash, files in hashes.items():
                if len(files) > 1:
                    print(f"Duplicate files: {files}")

if __name__ == "__main__":
    find_duplicates("xml")  # Replace with your directory
    print("Done")
