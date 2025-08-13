# Newclid documentation

## Installation of docs dependencies

Run:
```bash
uv sync --extra doc
```

## Build the docs

First parse and reformat the python packages of Newclid and its plugins:
```bash
python ./docs/reformat.py
```

Then run the docs on a local server:
```bash
sphinx-autobuild docs docs/_build/html
```

Click on the IP link at the end of the last command and it will open the local docs on a browser.
