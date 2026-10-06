# pandoc-forge filters

pandoc filters for the [pandoc-forge](https://github.com/pandoc-forge) conda channel, one recipe per package. pandoc itself is built in [pandoc-feedstock](https://github.com/pandoc-forge/pandoc-feedstock).

| Package | Upstream |
|---|---|
| `pandoc-amsthm` | [ickc/pandoc-amsthm](https://github.com/ickc/pandoc-amsthm) |
| `panflute` | [sergiocorreia/panflute](https://github.com/sergiocorreia/panflute) |
| `pantable` | [ickc/pantable](https://github.com/ickc/pantable) |

## Install

From the dev channel, with pandoc-forge's pandoc:

```sh
pixi workspace channel add --prepend https://prefix.dev/pandoc-forge/dev
pixi add pandoc pandoc-amsthm
```

A Lua filter installs to `$CONDA_PREFIX/share/pandoc/filters/`. Until pandoc can search more than one data directory ([jgm/pandoc#11889](https://github.com/jgm/pandoc/pull/11889)), give its full path:

```sh
pandoc -L "$CONDA_PREFIX/share/pandoc/filters/amsthm.lua" ...
```

A Lua filter doesn't install an engine. Add `pandoc`, `pandoc-wasm` or both.

A JSON filter such as pantable installs pandoc, and is used as on conda-forge:

```sh
pixi add pantable
pandoc -F pantable ...
```

Its other dependencies (Python, numpy, pyyaml, ...) come from conda-forge.

## Dependencies

Every package depends on `pandoc-api <version>.*`, from [`variants.yaml`](variants.yaml). It keeps the package on pandoc-forge's pandoc and on the pandoc API it was tested with. This is where these recipes differ from conda-forge's, which bound pandoc's version (`pandoc >=2.11.0.4,<4`) as a proxy for the API.

| Kind | Example | Engine dependencies |
|---|---|---|
| Lua filter | pandoc-amsthm | The minimum pandoc version as run constraints on `pandoc` and `pandoc-wasm`. A Lua filter runs inside pandoc, so it depends on pandoc's version. A run constraint checks whichever engine is installed, and installs none. |
| JSON filter | pantable | `pandoc`, with upstream's minimum version. pandoc runs it as a subprocess, which pandoc.wasm can't do. |
| Filter library | panflute | None: `pandoc-api` alone. It reads and writes the AST without pandoc, and a filter built on it brings the engine. |

Python packages are `noarch: python`, built and tested with `python_min` from `variants.yaml`, which is kept equal to conda-forge's.

## Adding a Lua filter

The upstream repository must be a Quarto extension: `_extensions/<name>/_extension.yml` lists its filters under `contributes.filters`. It declares two more keys, which Quarto ignores:

```yaml
pandoc-required: ">=3.1.1"            # the pandoc versions the filter supports
pandoc-test: pandoc lua spec/run.lua  # the command that tests it, run from the repository root
```

Add an entry to [`filters.yaml`](filters.yaml), then generate its recipe:

```sh
pixi run gen      # write recipes/ from filters.yaml and the upstream tag
pixi run build    # build and test into output/
```

The generated recipe installs each filter. Its test copies the installed filter over the repository's own copy and runs `pandoc-test` against pandoc-forge's pandoc, so upstream's suite tests the file that ships. Don't edit `recipes/`: CI runs `pixi run check` and fails if a recipe differs from what `pixi run gen` writes.

For a new upstream tag, update `tag` and reset `build` to 0. For a packaging fix, bump `build`.

## Adding a Python filter

Python packages aren't generated: write `recipes/<package>/recipe.yaml` by hand, starting from [`recipes/pantable/recipe.yaml`](recipes/pantable/recipe.yaml). `pixi run check` ignores recipes not listed in `filters.yaml`. Keep to the dependencies above, use the build string `pandoc_forge_${{ build_number }}`, and run upstream's own test suite against the installed package, with `src/` left out of the test files. Prefer the tag archive to the sdist when the sdist leaves out test fixtures.

## Publishing

Every push to `main` builds what isn't already in the dev channel (`pandoc-forge/dev`, or the repository variable `PREFIX_DEV_CHANNEL`) and uploads it with prefix.dev trusted publishing. Upstream test code runs in a job with no publishing token.

Releases go to the release channel (`pandoc-forge`, or the repository variable `PREFIX_RELEASE_CHANNEL`) one package at a time, from a tag `<package>-v<version>`, or `<package>-v<version>-<build>` for a build number above 0:

```sh
git tag pandoc-amsthm-v3.1.1 && git push origin pandoc-amsthm-v3.1.1
```

Release a dependency before what needs it (panflute before pantable): the tag's package is built and tested against the release channel's pandoc and packages, and the build fails unless the recipe's version and build number match the tag. The upload runs in the `release` GitHub environment, which only admits `*-v*` tags, and never overwrites a package.
