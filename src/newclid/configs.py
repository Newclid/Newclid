import newclid


from pathlib import Path


def default_configs_path() -> Path:
    return Path(newclid.__file__).parent.joinpath("default_configs")


def default_defs_path() -> Path:
    return default_configs_path().joinpath("defs.txt")


def default_rules_path() -> Path:
    return default_configs_path().joinpath("rules.txt")
