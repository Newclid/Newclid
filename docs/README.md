# To build documentation localy

## Install doc dependencies

```bash
pip install -e .[doc]
```
## Update the source code docs with sphinx-apidoc

```bash
sphinx-apidoc -M -e -f -o docs/source/ src/newclid --implicit-namespaces --ext-autodoc
```

## Reformat the source code docs with the custom reformat.py script

```bash
python docs/reformat.py
```

## Build the documentation

```bash
docs/make html
```

