import argparse
import multiprocessing
import pathlib
import subprocess
import tempfile
from lxml import etree

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert DITA files to Markdown')
    parser.add_argument('-i', '--input_dir', required=True, help='Path to directory containing DITA files')
    parser.add_argument('-o', '--output_dir', required=True, help='Path to output directory for Markdown files')
    return parser.parse_args()

def adjust_image_paths_and_create_placeholders(input_file, temp_dir):
    nsmap = {'d': 'http://dita.oasis-open.org/architecture/2005/'}

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(input_file), parser)
    root = tree.getroot()

    # Find all image elements
    for image in root.findall(".//d:image", nsmap):
        href = image.get('href')

        # Replace the image path with a relative path to temp_dir
        image_file = pathlib.Path(href)
        new_href = image_file.name
        image.set('href', new_href)

        # Create a placeholder image file in temp_dir
        placeholder_image_path = temp_dir / new_href
        placeholder_image_path.touch()

    # Write the modified XML back to the file
    tree.write(str(input_file), pretty_print=True, xml_declaration=True, encoding="utf-8", doctype=tree.docinfo.doctype)

def process_file(input_file, input_dir, output_dir):
    # Ignore files smaller than 2K
    if input_file.stat().st_size < 2048:
        return
    # Prepare the output file name
    relative_path = input_file.relative_to(input_dir)
    md_output_dir = output_dir / relative_path.with_suffix('')
    md_output_dir.mkdir(parents=True, exist_ok=True)

    outfile = (md_output_dir / input_file.name)

    if outfile.exists():
        return

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = pathlib.Path(temp_dir_name)

        # Copy the input file to the temporary directory
        temp_file = temp_dir / input_file.name
        temp_file.write_text(input_file.read_text())

        # Adjust image paths and create placeholder image files
        adjust_image_paths_and_create_placeholders(temp_file, temp_dir)


        # Prepare the error output file name
        error_file = md_output_dir / ("error_" + input_file.stem + '.error')

        # Execute the conversion command
        command = f"dita --input={temp_file} --format=markdown --output={md_output_dir}"
        result = subprocess.run(command, shell=True, stderr=subprocess.PIPE)

        # If there was an error, write the error message to the error file
        if result.returncode != 0:
            with open(error_file, 'w') as ef:
                ef.write(result.stderr.decode())
        outfile.write_text(input_file.read_text())
        print(outfile)

        command = f"dita --input={temp_file} --format=html5 --output={md_output_dir}"
        result = subprocess.run(command, shell=True, stderr=subprocess.PIPE)

        # If there was an error, write the error message to the error file
        if result.returncode != 0:
            with open(error_file, 'w') as ef:
                ef.write(result.stderr.decode())

def process_file_wrapper(args):
    try:
        process_file(*args)
    except Exception as e:
        print(f"Error processing {args[0]}: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--num-processes", type=int, default=8)
    return parser.parse_args()

def main():
    args = parse_arguments()

    input_dir = pathlib.Path(args.input_dir)
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use glob to find all .dita or .xml files in input directory (recursive)
    files_to_process = list(input_dir.rglob('*.dita')) + list(input_dir.rglob('*.xml'))
    arguments_to_process = [(input_file, input_dir, output_dir) for input_file in files_to_process]

    with multiprocessing.Pool(args.num_processes) as p:
        p.map(process_file_wrapper, arguments_to_process)

    print("Conversion complete.")

if __name__ == "__main__":
    main()
