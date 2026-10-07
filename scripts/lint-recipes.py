"""Check every recipe follows pandoc-forge's dependency convention.

Version constraints describe interfaces, not quality: a package constrains
pandoc only for something it can't work without, never to avoid a bug in some
pandoc release. So, for each recipe in recipes/:

- it depends on `pandoc-api ${{ pandoc_api }}.*`, the AST it speaks;
- an engine (`pandoc`, `pandoc-wasm`) in its run requirements is unversioned:
  pandoc-api picks the compatible engines;
- a minimum engine version (`>=` only) goes in the run constraints, for a Lua
  filter that needs a Lua API function added in that pandoc;
- no upper bound or exact version on an engine. Exact pins belong to packages
  that link the pandoc library (pandoc-crossref, in pandoc-feedstock).

Test requirements are exempt. Usage: python scripts/lint-recipes.py
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ENGINES = {"pandoc", "pandoc-wasm"}
PANDOC_API = "pandoc-api ${{ pandoc_api }}.*"


def lint(recipe):
    reqs = recipe.get("requirements", {})
    run = reqs.get("run", [])
    constraints = reqs.get("run_constraints", [])
    errors = []
    if PANDOC_API not in run:
        errors.append(f"run requirements lack `{PANDOC_API}`")
    for spec in run:
        name, _, version = spec.partition(" ")
        if name in ENGINES and version:
            errors.append(f"run requirement `{spec}`: an engine is unversioned, pandoc-api constrains it")
        if name == "pandoc-api" and spec != PANDOC_API:
            errors.append(f"run requirement `{spec}`: use `{PANDOC_API}`")
    for spec in constraints:
        name, _, version = spec.partition(" ")
        if name in ENGINES and not re.fullmatch(r">=[0-9][0-9.]*", version):
            errors.append(f"run constraint `{spec}`: only a minimum version (`>=x`) is allowed on an engine")
    return errors


def main():
    failed = False
    for path in sorted(ROOT.glob("recipes/*/recipe.yaml")):
        for error in lint(yaml.safe_load(path.read_text())):
            print(f"{path.relative_to(ROOT)}: {error}")
            failed = True
    if failed:
        sys.exit("see the dependency convention in README.md")


if __name__ == "__main__":
    main()
