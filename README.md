# pandoc-forge filters

pandoc filters for the [pandoc-forge](https://github.com/pandoc-forge) conda channel, one recipe per package. pandoc itself is built in [pandoc-feedstock](https://github.com/pandoc-forge/pandoc-feedstock).

| Package | Upstream |
|---|---|
| `pandoc-amsthm` | [ickc/pandoc-amsthm](https://github.com/ickc/pandoc-amsthm) |

## Install

From the dev channel, with pandoc-forge's pandoc:

```sh
pixi workspace channel add --prepend https://prefix.dev/ickc/pandoc-forge-dev
pixi add pandoc pandoc-amsthm
```

A Lua filter installs to `$CONDA_PREFIX/share/pandoc/filters/`. Until pandoc can search more than one data directory ([jgm/pandoc#11889](https://github.com/jgm/pandoc/pull/11889)), give its full path:

```sh
pandoc -L "$CONDA_PREFIX/share/pandoc/filters/amsthm.lua" ...
```

A filter doesn't install an engine. Add `pandoc`, `pandoc-wasm` or both.

## Dependencies

- `pandoc-api <version>.*`, from [`variants.yaml`](variants.yaml). It keeps the filter on pandoc-forge's pandoc and on the pandoc API it was tested with.
- The minimum pandoc version as run constraints on `pandoc` and `pandoc-wasm`. A Lua filter runs inside pandoc, so it depends on pandoc's version. A run constraint checks whichever engine is installed, and installs none.

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

## Publishing

Every push to `main` builds what isn't already in the dev channel (`ickc/pandoc-forge-dev`, or the repository variable `PREFIX_DEV_CHANNEL`) and uploads it with prefix.dev trusted publishing. Upstream test code runs in a job with no publishing token.
