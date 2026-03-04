# Complete Guide to Celery in Django (Professional Blog)

## What is Celery?

Celery is an asynchronous task queue/job queue system based on distributed message passing. It is designed to handle time-consuming tasks in the background, outside of the request-response cycle of a web application. Celery is written in Python but supports multiple languages through its protocol.

---

## Why Use Celery?

Celery helps solve the problem of executing long-running or scheduled tasks without blocking the user experience. Common use cases include:

* Integrating with third-party APIs
* Executing high CPU-bound computations
* Running periodic/scheduled tasks
* Sending emails or SMS notifications
* Processing files, images, or videos in the background

---

## Celery System Components

1. **Producer**: Your Django application that sends the task.
2. **Broker**: The message transport (Redis, RabbitMQ) that queues tasks.
3. **Worker**: The celery process that executes the task.
4. **Result Backend**: Stores the results of the tasks (Redis, Django ORM, etc).
5. **Beat Scheduler**: Used for periodic tasks (with `django-celery-beat`).

---


## How Components Connect (Step-by-Step)

### For a Normal Task:

1. **Producer** (Django app): Sends a task using `task.delay()` or `task.apply_async()`.
2. **Broker** (Redis): Receives the task and places it into a specific queue.
3. **Worker**: Picks up the task from the queue, executes it.
4. **Result Backend**: If configured, the result is stored for retrieval using `AsyncResult(task_id).get()`.

### For a Periodic Task:

1. **Beat Scheduler**: Stores schedule metadata in the DB using `django-celery-beat`.
2. **Beat Scheduler**: Triggers tasks on schedule by sending them to the **Broker**.
3. The rest follows same path: **Broker** → **Worker** → **Result Backend**.

---


## Installation and Setup

### Step 1: Install Required Packages

```bash
pip install celery redis django-celery-results django-celery-beat
```

For eventlet and gevent support:

```bash
pip install eventlet  # or gevent
```

### Step 2: Configure Celery in `settings.py`

```python
CELERY_BROKER_URL = 'redis://127.0.0.1:6369'  # Redis as broker
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'  # Requires django-celery-results
CELERY_TIMEZONE = 'Asia/Dhaka'
CELERY_ENABLE_UTC = False

# Celery Beat (scheduler)
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

Add to `INSTALLED_APPS`:

```python
'django_celery_results',
'django_celery_beat',
```

### Step 3: Create `celery.py`

```python
# celery_config/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['tasks'])
```

### Step 4: Modify `__init__.py`

```python
from celery_config.celery import app as celery_app
__all__ = ['celery_app']
```

### Step 5: Run Celery Workers

```bash
celery -A main worker -l info
```

### Step 6: Run Celery Beat (for Scheduled Tasks)

```bash
celery -A main beat -l info
```

---

## Worker Pool Types in Celery

### 1. **Prefork (Default)**

* Uses multiprocessing
* Best for CPU-bound tasks

```bash
celery -A main worker --pool=prefork --concurrency=4
```

### 2. **Threads**

* Uses multithreading
* Good for I/O-bound tasks

```bash
celery -A main worker --pool=threads --concurrency=10
```

### 3. **Eventlet/Gevent (Green Threads)**

* For async/network I/O tasks
* Monkey patching required

```bash
celery -A main worker --pool=eventlet --concurrency=100
```

### 4. **Solo**

* Single-threaded mode
* Useful for debugging or development

```bash
celery -A main worker --pool=solo -l info
```

---

## What Are Greenlets and Threads?

**Threads** are OS-level concurrent units of execution with their own stack. They allow concurrency using CPU cores, but switching between them is relatively heavy.

**Greenlets** are lightweight user-space pseudo-threads provided by libraries like `gevent` or `eventlet`. They are great for I/O-bound tasks (e.g., network calls), using cooperative multitasking.

| Feature      | Threads         | Greenlets       |
| ------------ | --------------- | --------------- |
| OS-level     | Yes             | No              |
| Switch Cost  | High            | Low             |
| Memory Usage | High            | Low             |
| Best For     | CPU-bound tasks | I/O-bound tasks |

---

## Execution Pool, Concurrency & Autoscaling

```bash
celery -A main worker --pool=prefork --concurrency=5 --autoscale=10,3 -l info
```

* `--concurrency=5`: Start with 5 child processes.
* `--autoscale=10,3`: Max 10, min 3 child processes based on load.

---

## Redis with Multiple Queues and Workers

You can use a single Redis instance to host multiple named queues. Each Celery worker can subscribe to specific queues. Redis creates an internal list for each queue name automatically—**no need to create queues manually**.

### Example:

```bash
celery -A main worker -Q high_priority -n worker1@%h -l info
celery -A main worker -Q low_priority -n worker2@%h -l info
```

### Task Definition:

```python
@app.task(queue='high_priority')
def important_task():
    ...

@app.task(queue='low_priority')
def background_task():
    ...
```

### Ensuring High Priority Tasks are Picked First:

* Assign workers to specific queues.
* Or use one worker with multiple queues in priority order:

```bash
celery -A main worker -Q high_priority,low_priority -l info
```

* Celery polls queues **from left to right**, prioritizing the leftmost one.
* If `high_priority` has tasks, they are always executed before checking `low_priority`.

---

## How Priority Works with Multiple Workers

When multiple Celery workers run concurrently, task prioritization still depends on:

* **Queue assignment**: Workers will only process tasks from queues they’re subscribed to.
* **Polling order**: When a worker subscribes to multiple queues, it polls them in the specified order.
* **Concurrency**: Tasks in the highest-priority queue can still be processed in parallel depending on `--concurrency` value.

### Example Scenario:

```bash
celery -A main worker -Q high_priority,low_priority -n priority_worker@%h -l info --concurrency=4
celery -A main worker -Q low_priority -n backup_worker@%h -l info --concurrency=2
```

* `priority_worker` polls both queues but prioritizes `high_priority`.
* `backup_worker` only handles `low_priority` when no high-priority processing is needed.
* Together they ensure high-priority tasks get more CPU and faster attention.

---

## Tasks, Shared Tasks, Groups, and Chains

### What is a Task?

A task is a Python function decorated with `@app.task`, which Celery can execute asynchronously.

### What is a Shared Task?

`@shared_task` allows defining a task without requiring access to a specific Celery app instance. Useful in reusable Django apps or libraries.

### What is a Group Task?

A group is a collection of tasks executed in parallel, returning a list of results once all tasks are done.

### What is a Chain?

A chain is a sequence of tasks executed one after the other, where the output of one task becomes the input for the next.

### What is a Synchronous Task?

Normally Celery tasks are async, but calling `.apply()` on a task instead of `.delay()` or `.apply_async()` executes it synchronously (blocking).

### Examples:

#### Regular Task

```python
@app.task
def add(x, y):
    return x + y
```

#### Shared Task

```python
from celery import shared_task

@shared_task
def my_shared_task():
    return 'This is a shared task'
```

#### Group Task

```python
from celery import group

job = group(add.s(2, 2), add.s(4, 4))
result = job.apply_async()
print(result.get())  # [4, 8]
```

#### Chain Task

```python
from celery import chain

job = chain(add.s(2, 2), add.s(4))  # (2+2)=4, then (4+4)=8
result = job.apply_async()
print(result.get())  # 8
```

#### Execute Synchronous Task

```python
result = add.apply(args=(3, 5))
print(result.get())  # Blocking execution
```

---

## Assign and Update Periodic Tasks

### Static Periodic Tasks

Defined in Django Admin via `django-celery-beat` models:

* Add periodic task in `PeriodicTask`
* Choose schedule from `IntervalSchedule`, `CrontabSchedule`

### Dynamic Periodic Tasks

```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

schedule, _ = IntervalSchedule.objects.get_or_create(every=10, period='seconds')
PeriodicTask.objects.create(
    interval=schedule,
    name='Dynamic Task',
    task='myapp.tasks.my_task',
    args=json.dumps(['arg1', 'arg2'])
)
```

---

## How Big Should the Execution Pool Be?

* **CPU-bound**: Concurrency = number of CPU cores
* **I/O-bound**: Higher concurrency (e.g., 100+ with threads/eventlet)
* Use autoscaling for load-based adjustment

---

## Interview Questions (Scenario-Based)

### Q1: What happens if your task fails?

**Answer**: Celery retries it based on retry policies. You can set retry logic in the task itself.

### Q2: How to handle long-running tasks?

**Answer**: Use `task.track_started = True` and monitor state. Consider chunking or chaining subtasks.

### Q3: How to prioritize tasks?

**Answer**: Use different queues with different workers and assign priorities.

### Q4: How to gracefully shutdown celery worker?

**Answer**: Send `TERM` signal. Celery will wait for running tasks to complete.

### Q5: What if Redis or RabbitMQ goes down?

**Answer**: Tasks won’t be delivered. Add retry/backoff mechanism. Use durable queues.

### Q6: Difference between shared\_task and @app.task?

**Answer**: `@app.task` vs `@shared_task`
@app.task directly ties your task to a specific Celery app instance. You have to import the app object into every tasks.py file across your project. This creates tight coupling — your task only works in that one project, and it can cause circular import problems as your project grows.
@shared_task doesn't import the app at all. Instead it uses a proxy that asks at runtime "which Celery app is currently running?" and binds to that. This means your tasks are portable, cleaner, and easier to test.
Simple analogy — @app.task is like a contractor who only works for one specific company and needs that company's ID card to do anything. @shared_task is a freelancer who works for whoever hired them that day, no specific ID needed.
In Django projects, always use @shared_task by default. The only time you'd use @app.task is when you need very specific app-level configuration on that task, which is rare. The biggest practical benefit is avoiding circular imports — with @shared_task, your tasks.py files don't need to import from celery.py at all, which keeps your project structure clean.

### Q7: What are groups and chains in Celery?

**Answer**: `group` runs tasks in parallel, `chain` runs sequentially.

### Q8: How to assign periodic task dynamically?

**Answer**: Use `django_celery_beat.models.PeriodicTask` to create/update schedules at runtime.

---

## Summary

Celery is essential for modern Django applications needing background, asynchronous, and scheduled task execution. With Redis or RabbitMQ as brokers and optional result stores like Django ORM, Celery enables you to scale horizontally, process tasks in real-time or schedule them efficiently. By choosing the correct worker pool, concurrency, and queue strategies, you can build robust systems ready for production workloads.

> Start simple. Add advanced pooling, autoscaling, and scheduling once your system grows.


