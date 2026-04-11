import json
import threading
import logging
from config import TASK_FILE

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_LOCK_TIMEOUT = 10


def _load() -> list:
    if TASK_FILE.exists() and TASK_FILE.stat().st_size > 0:
        with TASK_FILE.open("r") as f:
            return json.load(f)
    return []


def _save(tasks: list) -> None:
    tmp = TASK_FILE.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(tasks, f, indent=2)
    tmp.replace(TASK_FILE)


def update_tasks(fn) -> None:
    acquired = _lock.acquire(timeout=_LOCK_TIMEOUT)
    if not acquired:
        raise RuntimeError(
            f"Could not acquire storage lock within {_LOCK_TIMEOUT}s."
        )
    try:
        tasks = _load()
        tasks = fn(tasks)
        _save(tasks)
    finally:
        _lock.release()


def read_tasks() -> list:
    acquired = _lock.acquire(timeout=_LOCK_TIMEOUT)
    if not acquired:
        raise RuntimeError(
            f"Could not acquire storage lock within {_LOCK_TIMEOUT}s."
        )
    try:
        return _load()
    finally:
        _lock.release()
