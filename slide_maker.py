from dataclasses import dataclass

import mistune
import argparse
from pathlib import Path
import jinja2

parent = Path(__file__).resolve().parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "path",
    type=Path,
    help="Path to a directory of markdown documents to turn into slides",
)
parser.add_argument(
    "-o",
    "--output",
    type=Path,
    default=Path("./output"),
    help="Path to a directory to place the output.",
)
args = parser.parse_args()

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(parent), autoescape=jinja2.select_autoescape()
)
template = env.get_template("template.html")
index = env.get_template("index.html")


@dataclass
class Slide:
    ind: int
    rendered: str
    url: Path


@dataclass
class Slides:
    title: str
    slides: list[Slide]


all_slides = []


def convert_one(file: Path):
    text = file.read_text(encoding="utf-8")
    slides = text.split("\n---\n")
    slide = [slide for slide in slides if slide.strip() != ""]

    relpath = file.relative_to(args.path)
    assert ".." not in relpath.parts
    proc_slides = []
    for i, slide in enumerate(slides):
        res = mistune.html(slide)
        res = template.render(content=res, title=file.stem, ind=i, size=len(slides))
        outf = args.output / relpath.with_stem(f"{relpath.stem}.{i}").with_suffix(
            ".html"
        )
        outf.parent.mkdir(exist_ok=True, parents=True)
        with outf.open("w", encoding="utf-8") as f:
            f.write(res)
        proc_slides.append(Slide(i, res, outf))

    all_slides.append(Slides(file.stem, proc_slides))


for file in args.path.rglob("*.md"):
    convert_one(file)

with (args.output / "index.html").open("w") as f:
    f.write(index.render(presentations=all_slides))
