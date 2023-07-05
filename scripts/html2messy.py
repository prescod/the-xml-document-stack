import argparse
from pathlib import Path
import os
import shutil
from markdownify import MarkdownConverter, ATX, ATX_CLOSED, SETEXT, UNDERLINED
import random

MARKDOWN_BQ_STYLE = "MARKDOWN_BQ_STYLE"

class MessyMarkdownConverter(MarkdownConverter):
    """
    Create a custom MarkdownConverter that adds two newlines after an image
    """
    counter = 0
    def __init__(self, **options):
        self.__class__.counter += 1
        self.seed  = options.get("seed", self.__class__.counter)
        self.random = random.Random(self.seed)
        
        options.setdefault("autolinks", self.random.choice([True, False]))
        options.setdefault("bullets", self.random.choice(['*', '+', '-', '--', '**', '++', '-*', '+*', '*-', '**-', '++-']))
        options.setdefault("default_title", self.random.choice([True, False]))
        options.setdefault("escape_asterisks", self.random.choice([True, False]))
        options.setdefault("escape_underscores", self.random.choice([True, False]))
        options.setdefault("heading_style", self.random.choice([ATX, ATX_CLOSED, 'SETEXT', 'UNDERLINED']))
        options.setdefault("strong_em_symbol", self.random.choice(['*', '_', "~"]))
        options.setdefault("wrap_width", self.random.randint(40, 120))
        options.setdefault("sub_symbol", self.random.choice(['~', '_']))
        options.setdefault("sup_symbol", "^")
        self.capitalize_bold = self.random.choice([True, False])
        self.blockquote_style = self.random.choice(['>', '>>', '    ', '  '] + [MARKDOWN_BQ_STYLE] * 5)

        super().__init__(**options)
    
    def process_tag(self, node, *args, **kwargs):
        if node.name == "title":
            return ""
        return super().process_tag(node, *args, **kwargs)

    def convert_b(self, el, text, *args):
        if self.capitalize_bold:
            text = text.upper()
        return super().convert_b(el, text, *args)
    
    def convert_blockquote(self, el, text, *args):
        if self.blockquote_style != MARKDOWN_BQ_STYLE:
            bq_prefix = self.blockquote_style
            lines = text.split("\n")
            lines = [f"{bq_prefix} {line}" for line in lines]
            text = "\n".join(lines)
        return super().convert_blockquote(el, text, *args)

# ', 'convert_br', 'convert_code', 'convert_del', 'convert_em', 'convert_hn', 'convert_hr', 'convert_i', 'convert_img', 'convert_kbd', 'convert_li', 'convert_list', 'convert_ol', 'convert_p', 'convert_pre', 'convert_s', 'convert_samp', 'convert_soup', 'convert_strong', 'convert_sub', 'convert_sup', 'convert_table', 'convert_td', 'convert_th', 'convert_tr', 'convert_ul'

def process_file(file_path: Path, out_dir: Path = None) -> None:
    messy_file = file_path.with_suffix(".messy")
    converter = MessyMarkdownConverter()
    messy = converter.convert(file_path.read_text()).strip()
    messy_file.write_text(messy)
    print(f"Created: {messy_file}")
    if out_dir:
        # Copy processed file to the out directory
        shutil.copy(file_path, out_dir / file_path.name)

def process_html_files(directory: Path, out_dir: Path = None) -> None:
    for file_path in directory.rglob('*.html'):
        process_file(file_path, out_dir)

def main() -> None:
    parser = argparse.ArgumentParser(description="Process HTML files in a directory.")
    parser.add_argument("directory", type=Path, help="Directory to search for HTML files.")
    parser.add_argument("-o", "--outdir", type=Path, default=None, help="Directory to output processed files. (Optional)")
    
    args = parser.parse_args()
    process_html_files(args.directory, args.outdir)

if __name__ == "__main__":
    main()

# def md(html, **options):
#     return MessyMarkdownConverter(**options).convert(html)


# print(dir(MarkdownConverter))
# print(md('<b>Yay</b> <a href="http://github.com">GitHub</a>'))  # > '**Yay** [GitHub](http://github.com)'
# print(md('<b>Yay</b> <i>foo</i> <a href="http://github.com">GitHub</a>'))  # > '**Yay** [GitHub](http://github.com)'
