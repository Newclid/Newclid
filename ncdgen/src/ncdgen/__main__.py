import logging
from pathlib import Path

import hydra
import newclid.api
import newclid.jgex
import newclid.proof_state
import py_yuclid.yuclid_adapter
from omegaconf import DictConfig

from ncdgen.generation_loop import run_data_generation_loop
from ncdgen.hydra_config import hydra_to_pydantic_generation_config

LOGGER = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent.joinpath("conf")


@hydra.main(
    config_path=str(DEFAULT_CONFIG_PATH), config_name="baseline", version_base=None
)
def main(cli_config: DictConfig) -> None:
    generation_config = hydra_to_pydantic_generation_config(cli_config)

    logging.getLogger("ncdgen").setLevel(
        logging.getLevelNamesMapping()[generation_config.log_level]
    )

    # Mute newclid submodules that spams building problems attempts infos
    for logger_name in [
        newclid.api.__name__,
        newclid.proof_state.__name__,
        py_yuclid.yuclid_adapter.__name__,
    ]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    for logger_name in [
        newclid.jgex.__name__,
    ]:
        logging.getLogger(logger_name).setLevel(logging.ERROR)

    run_data_generation_loop(generation_config)


if __name__ == "__main__":
    main()
