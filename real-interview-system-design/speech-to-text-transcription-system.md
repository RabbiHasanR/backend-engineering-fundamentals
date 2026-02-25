This video is a walkthrough of a real system design interview for a Senior Backend Engineer role at an AI data processing company. The challenge is to design an asynchronous **Speech-to-Text Transcription System** capable of handling 100,000 daily audio file uploads (averaging 20MB and 10 minutes long) while notifying users upon completion.

Here is a step-by-step summary and explanation of the concepts covered in the interview.

---

### Step 1: Gathering Requirements & Estimations

Before drawing any diagrams, a good engineer clarifies the constraints.

#### Functional Requirements (What the system must do):

* Support multiple languages (English & Spanish).
* Users must be able to upload audio files.
* System must convert audio to text (using a model like OpenAI's Whisper).
* System must notify the user (success or failure) via email.

#### Non-Functional Requirements (How well the system must do it):

* **Scale:** 100K files/day, handling spikes up to 300K/day.
* **Latency:** Transcriptions should complete within 5 minutes.
* **Availability:** 99.99% uptime.
* **Budget:** ~$50,000/month.
* **Accuracy:** 95% transcription accuracy.

#### Estimations (Back-of-the-envelope math):

* **Storage:** 100K files * 20 MB = 2,000 GB (2TB) per day $\rightarrow$ 60TB/month.
* **Processing Time:** 100K files * 10 mins = 1,000,000 minutes of audio processing per day.

---

### Step 2: Designing the Core Architecture (Step-by-Step)

The interviewer explicitly requested an **asynchronous** system so the user doesn't have to leave the app open for 5 minutes waiting for the result.

#### 1. The Upload Flow (Pre-Signed URLs)

Instead of the user sending a massive 20MB file directly to the API Server (which would crash the server under high load), the system uses Amazon S3 directly.

* The **Client App** asks the **API Server** for permission to upload.
* The API Server asks **Amazon S3** for a temporary, secure link called a **Pre-Signed URL**.
* The API Server creates a record in the **SQL Database (RDS)** marking the job status as `pending`.
* The Client App uploads the large audio file directly to S3 using that URL, bypassing the API Server entirely.

#### 2. The Processing Flow (Queues & Workers)

Once the file lands in S3, the system needs to process it without overwhelming the servers.

* **Event Generation:** S3 triggers an event and sends the Job ID to a message queue (**Amazon SQS**).
* **The Queue:** The queue acts as a buffer. If a massive spike of uploads happens, they sit safely in the queue rather than crashing the system.
* **The Workers (EC2 Fleet):** A fleet of backend servers (workers) continuously pull jobs from the queue. These workers already have the AI model (Whisper) **pre-loaded** in memory to save time.
* **Execution:** A worker grabs a job, downloads the audio from S3, transcribes it, and saves the final `.txt` file into a *second* S3 bucket designated for transcripts. It then updates the SQL database status to `success`.

#### 3. Handling Failures (Dead Letter Queues)

Networks fail, and files get corrupted. The system must handle this gracefully.

* If a worker fails to process an audio file, it puts the job back in the queue to try again later (using **Exponential Backoff**—waiting 5 mins, then 25 mins, etc.).
* If it fails 3 times, the job is moved to a **Dead Letter Queue (DLQ)**. The status in the database is updated to `failed`.

#### 4. The Notification Flow

The user needs to know when the job is done.

* Whether the job succeeds or fails, the main worker drops a message into a separate **Notifications SQS Queue**.
* A dedicated **Notification Worker** pulls from this queue and sends an email to the user with a temporary download link to the transcript.

---

### Step 3: Scaling the System

The interviewer will inevitably ask: "How does this handle traffic spikes?"

#### Auto-Scaling Strategy

You cannot afford to run 100 massive AI servers 24/7. You must scale up and down dynamically based on the queue size.

* **The Metric:** The system tracks **Queue Depth per Worker** (Total jobs in queue / Total active workers).
* **The Rule:** If the depth per worker exceeds a limit (e.g., >500 jobs per worker), the system automatically spins up more EC2 instances. If it drops below a limit (e.g., <200), it shuts servers down to save money.
* **The Formula:** Increase/decrease workers by an absolute number (e.g., 10) OR a percentage (e.g., 20%)—whichever is greater.

#### Handling Edge Cases

* **Massive Files (2-hour podcasts):** A single worker will time out trying to process a 2-hour file. The solution is a **Chunking Strategy**: A pre-processor splits the large audio into 10-minute chunks, processes them in parallel across multiple workers, and stitches the text back together at the end.
* **Viral Transcripts:** If a famous influencer uploads a podcast and 1 million people try to download the text file at once, S3 will get expensive and slow. The solution is to put a **CDN (Content Delivery Network like AWS CloudFront)** in front of S3 to cache the text file globally.
* **API Server Load:** To prevent the API Server from crashing during the initial upload requests, place an **Application Load Balancer (ALB)** in front of a fleet of API servers to distribute the traffic.

### Want to go deeper?

Since you work with **Python/Django and PostgreSQL**, would you like to see how you would implement the "Pre-Signed URL" logic using `boto3` in Python, or how you would structure the PostgreSQL database tables for tracking these transcription jobs?








