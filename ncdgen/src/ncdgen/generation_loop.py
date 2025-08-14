# coding: utf-8
import logging
import multiprocessing
import os
import random
import time
import traceback
from typing import Iterable

import yaml
from pydantic import BaseModel

from ncdgen.build_diagram import DiagramGenerationMetadata
from ncdgen.extract_datapoint import (
    SubProblemDatapoint,
    generate_subproblems_datapoints,
)
from ncdgen.generation_configuration import DiagramGenerationConfig
from ncdgen.solver import NewclidSolver

LOGGER = logging.getLogger(__name__)


class Datapoint(BaseModel):
    subproblem: SubProblemDatapoint
    generation_metadata: DiagramGenerationMetadata


def run_data_generation_loop(generation_config: DiagramGenerationConfig) -> int:
    """Runs the data generation loop.

    Returns the number of datapoints generated.
    """
    LOGGER.info(
        "Starting loop with base configuration:\n%s",
        yaml.dump(generation_config.model_dump(mode="json")),
    )

    dp_idx = 0
    start_time = time.time()
    for datapoints, generation_metadata in _run_parallel_datapoint_generation(
        generation_config
    ):
        datagen_runtime = time.time() - start_time
        for datapoint in datapoints:
            to_write = Datapoint(
                subproblem=datapoint, generation_metadata=generation_metadata
            )
            with generation_config.jsonl_dump_file.open("a") as file:
                file.write(to_write.model_dump_json() + "\n")

            dp_idx += 1

        if (
            generation_config.timeout is not None
            and datagen_runtime > generation_config.timeout
        ):
            LOGGER.info(f"Timeout reached after {datagen_runtime:.2f} seconds.")
            break
    LOGGER.info(f"Finished generating diagrams. {dp_idx} successes.")
    return dp_idx


def _run_parallel_datapoint_generation(
    cfg: DiagramGenerationConfig,
) -> Iterable[tuple[list[SubProblemDatapoint], DiagramGenerationMetadata]]:
    """Returns a stream of datapoints. For each datapoint, we return the configuration
    if we're the first datapoint for that diagram.

    """
    randomness_source = _create_random_source(cfg)
    jgex_solver = NewclidSolver()

    if cfg.debug:
        for seed in randomness_source:
            yield generate_subproblems_datapoints(cfg, seed, jgex_solver=jgex_solver)
        return

    num_processes = os.cpu_count() if cfg.n_workers == "auto" else cfg.n_workers
    print(f"Starting pool with {num_processes} processes...")
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Create iterator of (cfg, seed) tuples
        task_iterator = ((cfg, seed) for seed in randomness_source)

        # Use imap_unordered to get results as soon as they are ready
        # It applies 'expensive_compute_task' to each item from 'task_iterator'
        processes_results_iterator = pool.imap_unordered(
            _safe_generate_subproblems_datapoints, task_iterator
        )

        print("Master process waiting for results...")
        # Iterate through results as they arrive from any worker
        for process_result in processes_results_iterator:
            if process_result is None:
                continue
            yield process_result


def _safe_generate_subproblems_datapoints(
    args: tuple[DiagramGenerationConfig, bytes],
) -> tuple[list[SubProblemDatapoint], DiagramGenerationMetadata] | None:
    try:
        jgex_solver = NewclidSolver()
        return generate_subproblems_datapoints(*args, jgex_solver=jgex_solver)
    except Exception as e:
        LOGGER.error(f"Error uncaught by anything: exception: {e}")
        LOGGER.error("Traceback:")
        LOGGER.error(traceback.format_exc())
        return None


def _create_random_source(cfg: DiagramGenerationConfig) -> Iterable[bytes]:
    if cfg.random_seed is not None:
        seed = cfg.random_seed.to_bytes(8, byteorder="big")
    else:
        seed = _get_current_time_as_seed()
    random.seed(seed)
    while True:
        yield random.randbytes(8)


def _get_current_time_as_seed() -> bytes:
    current_time_ns = time.time_ns()
    # Convert the integer nanoseconds to bytes.
    # 'Q' is for unsigned long long (8 bytes).
    # We use big-endian byte order '>' as a convention.
    return current_time_ns.to_bytes(8, byteorder="big")
