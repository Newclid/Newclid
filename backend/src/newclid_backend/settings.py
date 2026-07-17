import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
NEWCLID_QUEUE_NAME = os.getenv("NEWCLID_QUEUE_NAME", "newclid")

# default max runtime for a job
DEFAULT_JOB_TIMEOUT_SECONDS = int(os.getenv("DEFAULT_JOB_TIMEOUT_SECONDS", "120"))

# how long successful results stay in Redis
RESULT_TTL_SECONDS = int(os.getenv("RESULT_TTL_SECONDS", "3600"))

# how long failed job info stays in Redis
FAILURE_TTL_SECONDS = int(os.getenv("FAILURE_TTL_SECONDS", "3600"))

# the cli command that is used to execute newclid application
NEWCLID_COMMAND = os.getenv("NEWCLID_COMMAND", "newclid")
MAX_OUTPUT_CHARS = int(os.getenv("MAX_OUTPUT_CHARS", "200000"))
