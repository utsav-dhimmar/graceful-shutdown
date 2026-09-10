```py

import asyncio

async def worker():
    print("worker started")
    await asyncio.sleep(1)
    print("worker finished")


task = asyncio.Task(coro=worker(), name="worker_task")
```
- schedule a coroutine for concurrent execution
- it register a coroutine with current running event loop
- allow switch between background task

- `asyncio.TaskGroup()`
- is modern way to manage multiple tasks
- it is context manager
- it will wait for all tasks to finish
- it will cancel all tasks if one of them fails

```py
async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(worker())
        tg.create_task(worker())
```
