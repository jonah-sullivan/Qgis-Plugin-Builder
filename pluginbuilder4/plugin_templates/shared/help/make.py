#!/usr/bin/env python3
"""Cross-platform documentation build helper.

Run as: python make.py <target>

Equivalent to the Makefile/make.bat targets, without needing GNU make or a
platform-specific shell script — useful on Windows, where `make` isn't
available out of the box.
"""

import os
import sys

from sphinx.cmd.build import main as sphinx_main

SOURCEDIR = "source"
BUILDDIR = "build"

TARGETS = [
    "html",
    "dirhtml",
    "singlehtml",
    "pickle",
    "json",
    "htmlhelp",
    "qthelp",
    "devhelp",
    "epub",
    "latex",
    "text",
    "man",
    "changes",
    "linkcheck",
    "doctest",
]


def build(target):
    out_dir = os.path.join(BUILDDIR, target)
    doctrees_dir = os.path.join(BUILDDIR, "doctrees")
    argv = ["-b", target, "-d", doctrees_dir]
    sphinx_opts = os.environ.get("SPHINXOPTS")
    if sphinx_opts:
        argv.extend(sphinx_opts.split())
    argv.extend([SOURCEDIR, out_dir])
    exit_code = sphinx_main(argv)
    if exit_code == 0:
        print(f"\nBuild finished. Output is in {out_dir}")
    return exit_code


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in TARGETS:
        print("Usage: python make.py <target>")
        print("Targets:", ", ".join(TARGETS))
        return 0 if len(sys.argv) == 1 else 1
    return build(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
