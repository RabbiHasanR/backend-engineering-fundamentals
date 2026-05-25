# Walk Me Through Your Current Project — Short Spoken Script
---

## 1. Context — 

I work at a sports-tech company. We build a platform where players can create their own sports profile and join matches and tournaments.

Recently, I worked on a **face verification service**. The goal is simple: when a player signs up, we take their photo, check it is a real person, and make sure the same person is not already in our system. Only after this check, the player can open their sports profile.

So this service protects the platform from duplicate users and fake accounts.

---

## 2. Architecture —

I'm a backend engineer, but I designed the **full flow** for this service — both client side and server side. The mobile team implemented the client part based on my design.

The main idea was: **do cheap work on the client, do expensive work on the server, and never block the user.**

**On the client side**, I moved all basic validation into the mobile app: image must come from the **live camera**, must have **exactly one face**, eyes open, no sunglasses, no mask. We capture **three images from three angles** and the app checks all three are the same person. This gives instant feedback and keeps my server free.

**On the server side**, after validation, the client uploads the images to S3 and calls our API. The API does not do the heavy work — it pushes a task into a **Redis queue** and returns `202 Accepted` right away.

A **Celery worker** then runs a multi-step saga: take a Redis lock per user, call the face service to check duplicates in **Qdrant**, update user status in **PostgreSQL**, promote the S3 image from temporary to permanent, and confirm the face vector. An **hourly cron job** acts as a safety net to fix any broken states.

---

## 3. Role —

I owned the backend service end-to-end — the architecture, API, Celery worker, queue design, failure handling, and the cron reconciliation. I also designed the client validation flow, which my mobile teammates implemented.

---

## 4. Technical depth — Failures I had to handle — 

The hardest part was **failure handling**, because the flow touches S3, the face service, Qdrant, and Postgres — any of them can fail mid-way. I designed for five failure scenarios:

- **Transient errors** (network blip, DB deadlock, face service 503) — Celery retries with exponential backoff, because these are common and recoverable.
- **Logic failures** (duplicate face found, missing S3 file) — stop immediately and notify the user, because retrying will not help.
- **Max retries exhausted** (downstream service down for a long time) — roll back the user status to unverified and email them to try again, so they are never stuck in a half-state.
- **Hard worker crash** (killed mid-flow, e.g. after DB update but before face confirm) — every step is idempotent and a Redis lock per user prevents double-processing, so a new worker can safely resume.
- **Zombie users** (verified in DB but vector missing in Qdrant) — an hourly cron job finds them, resets them to unverified, and asks them to retry, because the saga alone cannot self-heal this case.

The trade-off I accepted: the user waits a few seconds for the async result instead of an instant response — in return, the system is safe under crashes and self-healing, which matters more for an identity check.

---

## 5. Impact —

Verification is now fully async and non-blocking, survives partial failures of any downstream service, and duplicate accounts are caught before a profile is opened. Bad images are rejected on the client, so server load stays low.

---

## 6. Outlook — 

My **most important next goal is proper observability** — metrics, dashboards, and alerts on queue depth, retries, and zombie-user fixes. Right now we recover from failures but can't easily *see* them in real time. After that, worker autoscaling and chaos testing.

I'm happy to go deeper into any part.

---

### Speaking tips

- Pause briefly between sections — let the interviewer interrupt.
- Concrete names (Redis, Qdrant, S3, Celery) build trust — don't skip them.
- If they look engaged on section 4, stretch it; if impatient, jump to Impact and Outlook.
