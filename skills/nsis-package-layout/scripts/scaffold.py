#!/usr/bin/env python3
"""Write README.md, .gitattributes and .github/workflows/ci.yml for the Package in the working directory.

Usage: scaffold.py NAME [--sources GLOB ...] [--project PATH] [--targets LIST] [--repo REPO] [--owner OWNER] [--force]

Run it once the files are in place: the license, usage guide, headers and binary
types are read from the tree. Plugins/ makes it a prebuilt Package; neither
--sources nor --project nor Plugins/ makes it a data Package.
"""

import argparse
import re
from pathlib import Path

DOC_EXT = [".md", ".txt", ".htm", ".html", ".rtf", ".chm", ".pdf", ".doc", ".docx", ".hlp"]
BINARY_EXT = {
    ".chm", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".rtf", ".hlp", ".odt",
    ".bmp", ".ico", ".gif", ".png", ".jpg", ".jpeg", ".cur", ".ani", ".wav", ".avi", ".swf",
    ".zip", ".7z", ".gz", ".tgz", ".tlz", ".bz2", ".lzma", ".tar", ".arc", ".cab",
    ".exe", ".sys", ".dcr", ".res", ".dll",
}

README = """# {title} for NSIS

![License](https://img.shields.io/github/license/{slug}?color=blue&style=for-the-badge)
![Release](https://img.shields.io/github/v/release/{slug}?style=for-the-badge)
![CI](https://img.shields.io/github/actions/workflow/status/{slug}/ci.yml?style=for-the-badge)
{note}
{about}

## Installation

Download the installer or archive from the [Releases page](https://github.com/{slug}/releases).

If you downloaded the zip archive, extract it into your NSIS folder: {adds}.
{license}"""

ABOUT = """This repository mirrors {title}, which was previously hosted on the [NSIS wiki](https://nsis.sourceforge.io/). {how}

**Are you the author?** You're welcome to take it over: [open an issue](https://github.com/{slug}/issues/new) and we'll transfer the repository to you."""

ABOUT_PREBUILT = """This repository mirrors {title}, which was previously hosted on the [NSIS wiki](https://nsis.sourceforge.io/). Its source code was never published or is lost, so this repository ships the original DLL unchanged. Nobody can rebuild, audit or fix it, or port it to other targets.

**Are you the author, or do you have the source?** [Open an issue](https://github.com/{slug}/issues/new): with the source, this repository can build the plug-in instead, or be transferred to you."""

WORKFLOW = """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  release:
    types: [published]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    permissions:
      contents: write
      id-token: write
      attestations: write

    steps:
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0

      - name: {step}
        uses: nsis-dev/release-package@d97a40353b77be7ebbc08524012befbf1275efd8 # v0.4.0
        with:
          name: {name}
{inputs}          release: ${{{{ github.event_name == 'release' }}}}
"""


def stem(path):
    s = re.split(r"[.\-_]", path.name, maxsplit=1)[0].upper()
    return "license" if s in ("LICENSE", "LICENCE", "COPYING", "UNLICENSE") else "readme" if s == "README" else None


def url(path):
    return path.as_posix().replace(" ", "%20")


def usage_guide(root, name):
    """The doc a reader opens first: a readme, else one named after the Package, else the shallowest."""
    docs = [p.relative_to(root) for p in (root / "Docs" / name).rglob("*")
            if p.is_file() and stem(p) != "license" and (p.suffix.lower() in DOC_EXT or stem(p) == "readme")]

    def rank(p):
        ext = p.suffix.lower()
        return (stem(p) != "readme", p.stem.lower() not in (name.lower(), "wiki"), p.stem.lower() == "wiki",
                len(p.parts), DOC_EXT.index(ext) if ext in DOC_EXT else 99, p.as_posix().lower())
    return min(docs, key=rank, default=None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--sources", nargs="+", default=[])
    ap.add_argument("--project")
    ap.add_argument("--targets")
    ap.add_argument("--repo", help="default: the working directory's name")
    ap.add_argument("--owner", default="nsis-community")
    ap.add_argument("--force", action="store_true", help="overwrite an existing README.md")
    a = ap.parse_args()

    root = Path.cwd()
    name = a.name
    slug = f"{a.owner}/{a.repo or root.name}"
    prebuilt = (root / "Plugins").is_dir()
    data = not (a.sources or a.project or prebuilt)
    files = [p.relative_to(root) for p in root.rglob("*")
             if p.is_file() and not any(part.startswith(".") for part in p.relative_to(root).parts)]

    if (root / "README.md").exists() and not a.force:
        raise SystemExit("README.md exists: move the upstream readme to Docs/%s/ first, or pass --force" % name)

    lic = sorted((p for p in files if len(p.parts) == 1 and stem(p) == "license"), key=lambda p: (len(p.name), p.name)) or \
        sorted((p for p in files if p.parts[:2] == ("Docs", name) and stem(p) == "license"), key=lambda p: (len(p.parts), p))
    doc = usage_guide(root, name)
    note = f"\n> [!NOTE]\n> **Looking for the usage guide?** See [{doc.as_posix()}]({url(doc)}).\n" if doc else ""
    license = f"\n## License\n\nSee [{lic[0].name}]({url(lic[0])}).\n" if lic else ""

    if data:
        title = name
        dirs = [d for d in ("Contrib", "Include", "Examples", "Docs") if (root / d).is_dir()]
        listed = [f"`{d}/`" for d in dirs]
        adds = "it adds files to " + (" and ".join([", ".join(listed[:-1]), listed[-1]]) if len(listed) > 1 else "".join(listed))
        about = ABOUT.format(title=name, slug=slug, how="Its files have been rearranged so that they install into NSIS.")
    else:
        title = f"{name} plug-in"
        adds = f"it adds `{name}.dll` to `Plugins/<variant>/`" + (" and its headers to `Include/`" if (root / "Include").is_dir() else "")
        about = (ABOUT_PREBUILT if prebuilt else ABOUT).format(
            title=f"the {name} plug-in", slug=slug,
            how="Its source has been rearranged so that it builds automatically; code changes are limited to build fixes.")
    (root / "README.md").write_text(README.format(title=title, slug=slug, note=note, about=about, adds=adds, license=license))

    binexts = sorted({p.suffix.lower() for p in files} & BINARY_EXT)
    ga = ["* text=auto", ""] + [f"*{e} binary" for e in binexts] + ([""] if binexts else []) + ["/README.md export-ignore", ""]
    (root / ".gitattributes").write_text("\n".join(ga))

    inputs = []
    if prebuilt:
        inputs.append("toolchain: prebuilt")
    elif a.project:
        inputs.append(f"project: {a.project}")
    elif a.sources:
        inputs.append("sources: |\n" + "\n".join(f"            {s}" for s in a.sources))
    if a.targets and not data:
        inputs.append(f"targets: {a.targets}")
    if not lic:
        inputs.append("strict: false")
    wf = root / ".github" / "workflows" / "ci.yml"
    wf.parent.mkdir(parents=True, exist_ok=True)
    wf.write_text(WORKFLOW.format(name=name, step="Package" if data else "Build plug-in", inputs="".join(f"          {i}\n" for i in inputs)))
    print(f"wrote README.md, .gitattributes, {wf.relative_to(root)}" + ("" if lic else " (no license: strict: false)"))


main()
