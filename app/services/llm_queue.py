from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

_queue: asyncio.Queue[tuple[Callable[[], Awaitable[T]], asyncio.Future[T]]] | None = None
_worker_tasks: list[asyncio.Task[None]] = []


async def _worker() -> None:
    assert _queue is not None
    while True:
        fn, future = await _queue.get()
        try:
            result = await fn()
            if not future.done():
                future.set_result(result)
        except Exception as exc:
            if not future.done():
                future.set_exception(exc)
        finally:
            _queue.task_done()


def start_llm_workers(*, concurrency: int = 2) -> None:
    global _queue, _worker_tasks
    if _queue is not None:
        return
    _queue = asyncio.Queue()
    for _ in range(max(1, concurrency)):
        _worker_tasks.append(asyncio.create_task(_worker()))


async def stop_llm_workers() -> None:
    global _queue, _worker_tasks
    for task in _worker_tasks:
        task.cancel()
    for task in _worker_tasks:
        try:
            await task
        except asyncio.CancelledError:
            pass
    _worker_tasks = []
    _queue = None


async def run_llm_job(fn: Callable[[], Awaitable[T]]) -> T:
    if _queue is None:
        return await fn()
    loop = asyncio.get_running_loop()
    future: asyncio.Future[T] = loop.create_future()
    await _queue.put((fn, future))
    return await future
