from typing import Any, TypeVar

from omegaconf import DictConfig, OmegaConf

from ncdgen.generation_configuration import DiagramGenerationConfig

TConfig = TypeVar("TConfig")


def hydra_to_pydantic_generation_config(config: DictConfig) -> DiagramGenerationConfig:
    """Converts Hydra config to Pydantic config."""
    # use to_container to resolve
    config_dict: dict[str, Any] = OmegaConf.to_object(config)  # type: ignore[assignment]
    return DiagramGenerationConfig(**config_dict)
