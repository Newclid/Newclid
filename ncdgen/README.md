# Data generation based on Newclid JGEX constructions

## Installation

From root:
```bash
uv sync --package ncdgen
```


## Usage

### Run localy

Local CLI is using [hydra](https://hydra.cc/docs/advanced/override_grammar/basic/) for specifying configurations overrides if needed for quick experiments.

```bash
uv run --no-sync ncdgen --config-name baseline
```

To see all available configuration fields for data generation see [DiagramGenerationConfig](src/ncdgen/generation_configuration.py#L19).
