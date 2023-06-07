# the-xml-document-stack

1. Set up a `venv` with `requirements.txt`

2. Download HuggingFace documents onto cache and symlink in
   the `dataset_bin` directory like this:

   `python download-xml-from-stack.py`

   Or you can download a smaller subset like this:

   `python download-xml-from-stack.py 100`

3. Extract relevant XML files into a subdirectory like this:

    `python find_xml_in_the_stack.py dataset_bin/data/xml/train-00*`


NOTE: Even if you delete the symlinks in `dataset_bin` the
      files will still exist in ~/.cache/huggingface/ !!!!
      They will take up 78 GB until you get rid of them!

     