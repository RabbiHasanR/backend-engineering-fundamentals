# Jenkins & CI/CD: A Complete Guide from Beginner to Advanced

---

## What is CI/CD? (Start Here)

Before we talk about Jenkins, you need to understand the problem it solves.

Imagine you are working on a team of five developers. Everyone writes code on their own computer. On Friday, all five people push their code to the same project. Then someone tries to run the app. It breaks. Nobody knows whose code caused the problem. It takes hours to figure out. The release is delayed. This is the old way of working.

CI/CD is how modern software teams avoid this nightmare.

**CI stands for Continuous Integration.** The word "continuous" means "all the time." The word "integration" means "combining code from different people." So CI means: every time someone pushes code, we automatically combine it and check if it still works. We run tests. We catch the problem immediately — not on Friday after everyone has gone home.

**CD stands for Continuous Delivery or Continuous Deployment.** After the code passes all checks, we automatically deliver it to a server. If it goes to a staging environment (for review), that is Continuous Delivery. If it goes directly to production (real users), that is Continuous Deployment.

### A Real-World Analogy

Think of a factory that makes smartphones.

- The old way: workers build pieces separately for a month, then try to assemble everything at the end. If one part does not fit, they have to throw a lot of work away.
- The CI/CD way: there is a conveyor belt. Every part is tested the moment it is made. Bad parts are rejected immediately. The assembly line keeps moving. The factory ships phones every week instead of every six months.

Your code is the parts. Jenkins is the conveyor belt.

### The CI/CD Pipeline in Simple Steps

```
Developer pushes code
        ↓
Git server receives the push (Gogs, GitHub, etc.)
        ↓
Webhook fires — tells Jenkins "new code arrived"
        ↓
Jenkins pulls the code
        ↓
Install dependencies
        ↓
Run tests
        ↓
Build the application
        ↓
Deploy to server
        ↓
Send notification (Slack, email)
```

Each arrow in that list is one step in your **pipeline**. If any step fails, the pipeline stops and you get notified immediately. The bad code never reaches your server.

### CI vs CD — What Is the Difference?

| Term | What it means | Example |
|---|---|---|
| Continuous Integration (CI) | Auto-build and test every push | Every push to `main` runs `pytest` |
| Continuous Delivery (CD) | Auto-deliver to staging, human approves production | Deploy to staging automatically, a human clicks "approve" for production |
| Continuous Deployment (CD) | Fully automatic, goes straight to production | Every green build deploys to real users with no human step |

Most companies do CI + Continuous Delivery. Full Continuous Deployment is only common when you have very high test confidence.

---

## What is Jenkins?

Jenkins is a free, open-source automation server. It is the most widely used CI/CD tool in the world. You install it on a server, connect it to your Git repository, and tell it what to do every time someone pushes code.

Jenkins does not write your tests. It does not deploy your app. It is the **manager** that calls the right people (scripts, tools, commands) at the right time and in the right order.

### Why Jenkins Specifically?

There are other CI/CD tools — GitHub Actions, GitLab CI, CircleCI, Bitbucket Pipelines. Jenkins is different in a few important ways:

- It is self-hosted. You run it on your own server. You have full control.
- It has over 1,800 plugins. It connects to almost any tool that exists.
- It is free. No per-minute cost like cloud CI services.
- It works with any Git server — GitHub, GitLab, Bitbucket, Gogs, or your own.
- Large enterprises run Jenkins for thousands of jobs. It scales.

The tradeoff is that you have to manage the server yourself. But once it is set up, it is extremely powerful.

### Key Jenkins Terms

| Term | Simple meaning |
|---|---|
| **Job / Project** | A single automation task. "Build my Django app." |
| **Build** | One run of a job. Build #42 passed. Build #43 failed. |
| **Pipeline** | A multi-step job defined as code. Has stages like Build → Test → Deploy. |
| **Stage** | One phase inside a pipeline. "Test" is a stage. "Deploy" is a stage. |
| **Step** | The actual command inside a stage. `sh 'pytest tests/'` is a step. |
| **Node / Agent** | The machine where Jenkins runs your job. |
| **Controller** | The Jenkins server you log into. It manages everything. |
| **Executor** | One slot for running a job. If a node has 2 executors, it runs 2 jobs at once. |
| **Workspace** | The folder on the agent where your code is checked out and built. |
| **Plugin** | An extension that adds new features (Docker support, Slack notifications, etc.). |

---

## Part 1: Build Types — Freestyle vs Pipeline

Jenkins gives you two main ways to define a job.

### Freestyle Build

Freestyle is the simplest way to create a job. You click through a form in the Jenkins UI. You fill in your Git URL, choose when to trigger, add shell commands, and configure what happens after. No coding required.

It feels like shell scripting with a web interface. Good for learning Jenkins. Not good for production CI/CD.

**What you configure in a Freestyle job:**

| Section | What you do |
|---|---|
| Source Code Management | Point to your Git repo. Set the branch. |
| Build Triggers | Webhook, schedule (cron), poll every 5 minutes, or manual. |
| Build Environment | Inject environment variables, clean workspace before build. |
| Build Steps | Run shell commands. `pip install -r requirements.txt`, `pytest`, etc. |
| Post-build Actions | Archive files, send email, trigger another job. |

**The big problem with Freestyle:** the job configuration lives only in Jenkins. It is not in your Git repository. There is no history, no code review, no rollback. If you change a setting and it breaks, you cannot easily undo it.

### Pipeline Build

Pipeline is how professional teams work. You define the entire CI/CD process as code in a file called `Jenkinsfile`. This file lives in your repository alongside your application code. It is versioned, reviewed, and stored in Git like everything else.

Pipelines use a language called **Groovy DSL** (Domain Specific Language). You do not need to learn all of Groovy — just the pipeline syntax, which is readable even if you have never seen Groovy before.

There are two styles of writing pipelines: **Declarative** and **Scripted**.

**Declarative** is the modern standard. It has a defined structure and built-in validation. Use this.

**Scripted** is older and gives more raw Groovy power, but it is harder to read and maintain. Avoid it unless you have a specific reason.

```groovy
// Declarative — modern, recommended
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
    }
}

// Scripted — older style
node {
    stage('Build') {
        sh 'pip install -r requirements.txt'
    }
}
```

For everything in this guide, we use Declarative pipelines.

---

## Part 2: The Jenkinsfile

A Jenkinsfile is a text file that defines your pipeline. Place it at the root of your repository (next to your `README.md`). Jenkins reads it automatically when a build triggers.

### What a Jenkinsfile Does

Think of it as a recipe. You write down every step in order. Jenkins follows the recipe every time. Everyone on the team can read the recipe. The recipe is stored in Git, so you can see who changed what and when.

### The Skeleton

Every Declarative Jenkinsfile has this structure:

```groovy
pipeline {           // 1. The outer wrapper. Everything goes inside.
    agent any        // 2. Where to run. "any" = any available machine.

    stages {         // 3. Container for all your stages.

        stage('Name of stage') {   // 4. One phase of your pipeline.
            steps {                // 5. The actual commands.
                sh 'echo hello'
            }
        }

    }
}
```

That is it. Five layers. Once you understand this skeleton, everything else is just adding more blocks inside.

### Single-Stage Jenkinsfile

The simplest possible pipeline — one stage, a few commands:

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Installing dependencies...'
                sh 'pip install -r requirements.txt'
                echo 'Done.'
            }
        }
    }
}
```

When Jenkins runs this, you will see one green box labeled "Build" in the UI. If any command fails, the box turns red and the build stops.

### Multi-Stage Jenkinsfile

Real pipelines have multiple stages. Each stage is a logical phase. Jenkins shows each one as a colored box in the UI — you can see at a glance where a build failed.

```groovy
pipeline {
    agent any

    environment {
        APP_NAME = 'my-fastapi-app'
        DEPLOY_SERVER = 'ubuntu@10.0.1.50'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm  // Pull code from the configured Git repo
            }
        }

        stage('Install') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                sh 'flake8 app/ --max-line-length=120'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest tests/ --junitxml=test-results.xml -v'
            }
            post {
                always {
                    junit 'test-results.xml'  // Publish results in Jenkins UI
                }
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t ${APP_NAME}:${BUILD_NUMBER} .'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'  // Only deploy when pushing to main
            }
            steps {
                sh 'ssh ${DEPLOY_SERVER} "cd /app && ./deploy.sh"'
            }
        }

    }

    post {
        success {
            echo 'Pipeline passed. Application deployed.'
        }
        failure {
            echo 'Pipeline failed. Check the logs above.'
        }
    }
}
```

The stages run in order from top to bottom:

```
Checkout → Install → Lint → Test → Build → Deploy (main only)
```

If the Test stage fails, the Build and Deploy stages never run. The broken code never reaches your server.

---

## Part 3: Pipeline Directives (The Building Blocks)

A Declarative pipeline is made of named blocks called **directives**. Each one has a specific job. Here is each one explained clearly.

### `pipeline { }` — The Outer Wrapper

Required. Everything goes inside this block. Nothing goes outside it.

### `agent` — Where to Run

Tells Jenkins which machine to use. Must appear directly inside `pipeline {}`. You can also put it inside individual stages to run different stages on different machines.

```groovy
agent any                      // Any available agent — simplest option

agent none                     // No global agent. Each stage must declare its own.

agent { label 'linux' }        // A specific machine with this label

agent {
    docker { image 'python:3.11-slim' }  // Run inside a Docker container
}

agent {
    node { label 'ec2-builder' }         // Explicit node syntax — same as label
}
```

**When would you use `agent none`?** When different stages need different machines. For example, your build stage runs on Linux, but your deploy stage needs a Windows machine.

```groovy
pipeline {
    agent none  // No global agent

    stages {
        stage('Build') {
            agent { label 'linux' }
            steps { sh 'make build' }
        }
        stage('Test on Windows') {
            agent { label 'windows' }
            steps { bat 'run-tests.bat' }
        }
    }
}
```

### `environment { }` — Variables

Defines environment variables available to all stages. Variables defined here are available as `env.VARIABLE_NAME` or just `${VARIABLE_NAME}` in shell commands.

Use `credentials()` to pull secrets from Jenkins credential store. The value is injected securely and masked in the console log — it never appears as plain text.

```groovy
environment {
    APP_NAME    = 'my-django-app'
    ENVIRONMENT = 'production'

    // Pull a secret from Jenkins Credentials (masked in logs)
    DB_PASSWORD = credentials('db-password-secret-id')
    API_KEY     = credentials('stripe-api-key')

    // Use built-in Jenkins variables
    BUILD_TAG   = "build-${env.BUILD_NUMBER}"
}
```

You can also define `environment` inside a single stage — those variables only exist for that stage.

### `stages { }` and `stage('name') { }` — The Phases

`stages` is the container block. `stage` is each individual phase. Every stage gets a name — this name appears in the Jenkins UI as a labeled box.

Good stage names describe what happens:

```groovy
stages {
    stage('Checkout')    { ... }
    stage('Install')     { ... }
    stage('Lint')        { ... }
    stage('Test')        { ... }
    stage('Build image') { ... }
    stage('Deploy')      { ... }
}
```

### `steps { }` — The Commands

The actual work happens inside `steps`. These are the shell commands, Jenkins functions, and Groovy calls that do things.

Common steps:

```groovy
steps {
    // Run a shell command (Linux / Mac)
    sh 'pytest tests/'

    // Run a Windows batch command
    bat 'run-tests.bat'

    // Print to the console log
    echo "Building ${env.APP_NAME} version ${env.BUILD_NUMBER}"

    // Clone the repository
    checkout scm

    // Copy files
    sh 'rsync -av dist/ ubuntu@server:/var/www/app/'

    // Run arbitrary Groovy code
    script {
        def gitCommit = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        echo "Deploying commit: ${gitCommit}"
        env.GIT_SHORT_COMMIT = gitCommit
    }

    // Inject credentials for one block only
    withCredentials([string(credentialsId: 'api-key', variable: 'SECRET')]) {
        sh 'curl -H "Authorization: Bearer $SECRET" https://api.example.com'
    }
}
```

### `when { }` — Conditional Stages

Run a stage only when specific conditions are true. Without `when`, every stage runs every time.

```groovy
stage('Deploy to production') {
    when {
        branch 'main'           // Only when pushing to the main branch
    }
    steps {
        sh './deploy-prod.sh'
    }
}

stage('Notify on failure') {
    when {
        expression { currentBuild.result == 'FAILURE' }  // Custom Groovy condition
    }
    steps {
        sh './send-alert.sh'
    }
}

stage('Skip on weekends') {
    when {
        not {
            triggeredBy 'TimerTrigger'  // NOT triggered by a schedule
        }
    }
    steps { sh './build.sh' }
}

stage('Only on release branches') {
    when {
        anyOf {
            branch 'main'
            branch pattern: 'release/.*', comparator: 'REGEXP'
        }
    }
    steps { sh './release.sh' }
}
```

---

## Part 4: Agents — Where Jenkins Runs Your Builds

Jenkins has a **controller** (the server you log into) and one or more **agents** (the machines that actually run your builds). The controller is just the brain — it should not run builds itself. Agents do the work.

### Permanent Agents

Dedicated servers that are always online. Jenkins connects to them via SSH. They stay alive between builds. Your code is cloned into a workspace on the agent, the build runs, and the workspace stays there for the next build (cached).

**When to use:** builds that need GPUs, builds that need large cached dependencies (like npm or pip), or builds that run very frequently and cannot afford startup time.

**The problem with permanent agents:** they cost money even when idle. The environment can drift over time — someone installs something, something gets updated, and builds start behaving differently on different agents.

### Cloud / Ephemeral Agents

Spun up on demand, run one build, then destroyed. Examples:

- **Docker plugin:** Jenkins spins up a Docker container, runs the build inside it, then removes the container.
- **Kubernetes plugin:** Jenkins creates a pod in your Kubernetes cluster, runs the build, deletes the pod.
- **EC2 plugin:** Jenkins launches a new EC2 instance, runs the build, terminates the instance.

**When to use:** most modern CI/CD workflows. Clean environment every time, scales to zero when idle, cost-efficient.

**The problem:** startup time. Launching an EC2 instance takes 1–3 minutes. This is where the Golden AMI strategy helps — pre-bake all your tools (Python, pip packages, Node.js, SSH keys) into a custom AMI so the instance is ready in seconds.

### Configuring a Cloud Agent Template

When you use a cloud plugin (like the EC2 plugin), you create **templates** — blueprints Jenkins uses to spin up each agent. Key settings:

**Instance capacity** — the maximum number of agents Jenkins can launch simultaneously from this template. If you set it to 3 and 5 builds arrive at once, three start immediately and two wait in the queue. This prevents runaway costs when many builds trigger at the same time.

**Remote file system root** — the directory on the agent where Jenkins stores your workspace. Usually `/home/jenkins` or `/var/jenkins`. The user that Jenkins connects as must have read/write access to this path. Your checked-out code, build artifacts, and cached dependencies all live here.

**Labels** — tags you assign to the template. Your Jenkinsfile uses `agent { label 'my-label' }` to say "run this on an agent with this label." One template can have multiple labels separated by spaces.

**AMI / Image** — the base image. For EC2, this is your AMI ID. For Docker, this is the image name like `python:3.11-slim`. This is the single most important setting for build speed and reproducibility.

### node vs cloud in Scripted Pipelines

If you encounter older Scripted pipeline syntax, `node` targets a specific labeled agent:

```groovy
// Scripted: target a specific agent
node('linux-agent') {
    stage('Build') {
        sh './build.sh'
    }
}

// Declarative equivalent
agent { label 'linux-agent' }
```

---

## Part 5: Parameters — Making Builds Flexible

Instead of hardcoding values in your Jenkinsfile, you can make a build accept inputs. When someone triggers the build manually, Jenkins shows a form where they fill in the values. You can also pass parameters from other pipelines or from webhooks.

### In Freestyle

Go to Configure → check "This project is parameterized" → add parameters. Jenkins shows the form when you click "Build with Parameters."

### In Pipeline

Use the `parameters` directive at the top of your pipeline:

```groovy
pipeline {
    agent any

    parameters {
        // A text input
        string(
            name: 'BRANCH',
            defaultValue: 'main',
            description: 'Which branch to deploy?'
        )

        // A checkbox
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run the test suite before deploying?'
        )

        // A dropdown
        choice(
            name: 'ENVIRONMENT',
            choices: ['staging', 'production'],
            description: 'Target environment'
        )

        // A password field (masked in the UI)
        password(
            name: 'DEPLOY_TOKEN',
            defaultValue: '',
            description: 'Deployment token (leave blank to use stored credential)'
        )
    }

    stages {
        stage('Test') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                sh 'pytest tests/'
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying branch '${params.BRANCH}' to '${params.ENVIRONMENT}'"
                sh "./deploy.sh ${params.BRANCH} ${params.ENVIRONMENT}"
            }
        }
    }
}
```

Access parameter values with `params.PARAMETER_NAME`.

**Important:** the first time you run a parameterized pipeline, Jenkins needs to load the Jenkinsfile to discover what parameters exist. The first run will use default values and will not show the form. After the first run, the form appears every time.

### Built-in Environment Variables

Jenkins provides these automatically — no parameters needed:

```groovy
env.BUILD_NUMBER    // "42"
env.BUILD_URL       // "http://jenkins/job/my-app/42/"
env.JOB_NAME        // "my-app"
env.GIT_BRANCH      // "origin/main"
env.GIT_COMMIT      // "abc123def456..."
env.WORKSPACE       // "/var/jenkins/workspace/my-app"
env.NODE_NAME       // "ec2-agent-001"
```

Use them like this in shell commands:

```groovy
sh "docker tag my-app:latest my-app:${env.BUILD_NUMBER}"
sh "echo 'Build ${env.BUILD_NUMBER} from commit ${env.GIT_COMMIT}'"
```

---

## Part 6: Post-Build Actions

Post-build actions run after the pipeline finishes — or after a specific stage. They always run, even if the build failed. This is where you archive files, publish test reports, send notifications, and clean up.

### In Freestyle

At the bottom of Configure, look for the "Post-build Actions" section. Common actions: archive artifacts, publish JUnit test results, trigger another job, send email notification.

### In Pipeline — The `post` Directive

Can be placed at the pipeline level (runs after all stages complete) or inside a stage (runs after that one stage).

```groovy
post {
    always   { /* runs no matter what */ }
    success  { /* runs only when build passed */ }
    failure  { /* runs only when build failed */ }
    unstable { /* runs when tests have failures (yellow build) */ }
    changed  { /* runs when this build's result differs from the last build */ }
    fixed    { /* runs when the build was failing and is now green */ }
    aborted  { /* runs when someone cancelled the build */ }
}
```

### Real-World Post Block

```groovy
pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                sh 'pytest tests/ --junitxml=results.xml --cov=app --cov-report=xml'
            }
        }
        stage('Build') {
            steps {
                sh 'docker build -t my-app:latest .'
            }
        }
    }

    post {
        always {
            // Always publish test results so you can see them in the Jenkins UI
            junit 'results.xml'

            // Always archive built files so you can download them from Jenkins
            archiveArtifacts artifacts: 'dist/**', allowEmptyArchive: true

            // Always clean the workspace after the build
            cleanWs()
        }

        success {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "✓ ${env.JOB_NAME} #${env.BUILD_NUMBER} passed — ${env.BUILD_URL}"
            )
        }

        failure {
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: "✗ ${env.JOB_NAME} #${env.BUILD_NUMBER} FAILED — ${env.BUILD_URL}"
            )
            // Also send email
            mail(
                to: 'team@company.com',
                subject: "Jenkins Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build failed. Check the logs at ${env.BUILD_URL}"
            )
        }

        fixed {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "Build is green again after failure — ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            )
        }
    }
}
```

---

## Part 7: The `tools` Directive

The `tools` directive tells Jenkins to automatically install a specific tool and add it to the `PATH` before your stages run.

### Why Do You Need It?

Without `tools`, your build depends on whatever is installed on the agent machine. If one agent has Maven 3.6 and another has Maven 3.9, your builds behave differently on different machines. Over time this causes subtle bugs that are very hard to track down.

With `tools`, you declare the version by name. Jenkins installs it if it is not already there. Every agent, every time, same version.

### Setup: Global Tool Configuration

Before you can use `tools` in a Jenkinsfile, you must register the tool in Jenkins:

1. Go to **Manage Jenkins → Global Tool Configuration** (or Tools in newer versions)
2. Find the section for your tool (JDK, Maven, NodeJS, etc.)
3. Click "Add" and give it a name like `maven-3.9` or `node-18`
4. Tell Jenkins how to install it (automatic from Apache, from a URL, or already installed at a path)

Then reference that exact name in your Jenkinsfile.

### Using `tools` in a Jenkinsfile

```groovy
pipeline {
    agent any

    tools {
        maven  'maven-3.9'   // Name from Global Tool Configuration
        jdk    'java-17'
        nodejs 'node-18'
    }

    stages {
        stage('Build') {
            steps {
                // These tools are on PATH automatically — no need to specify full paths
                sh 'mvn --version'
                sh 'node --version'
                sh 'java -version'

                sh 'mvn clean package -DskipTests'
            }
        }

        stage('Frontend') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
    }
}
```

### Built-in Tool Types

| Tool | Keyword in Jenkinsfile | Plugin required |
|---|---|---|
| JDK | `jdk` | Built-in |
| Maven | `maven` | Built-in |
| Gradle | `gradle` | Gradle plugin |
| Node.js | `nodejs` | NodeJS plugin |
| Go | `go` | Go plugin |

**Python note:** Python does not have a Jenkins tool plugin. For Python projects (Django, FastAPI), the common approaches are:

- Use a Docker agent with the right Python image (`python:3.11-slim`). Clean and reproducible.
- Pre-install Python on the agent (permanent agent or Golden AMI). Fast but requires maintenance.
- Use `pyenv` on the agent and manage versions yourself in shell steps.

---

## Part 8: Options

The `options` directive configures pipeline-level behavior — timeouts, retry counts, log settings, and more.

```groovy
pipeline {
    agent any

    options {
        // Kill the build if it runs longer than 30 minutes
        // Without this, a hung build blocks your queue forever
        timeout(time: 30, unit: 'MINUTES')

        // Only one build at a time for this job
        // Essential for deploy jobs — you do not want two deploys running simultaneously
        disableConcurrentBuilds()

        // Keep only the last 10 builds to save disk space
        buildDiscarder(logRotator(numToKeepStr: '10'))

        // Add timestamps to every line in the console log
        // Makes it easy to see how long each step takes
        timestamps()

        // Add colors to console output (requires AnsiColor plugin)
        ansiColor('xterm')

        // Do not check out code automatically — do it manually in a step
        skipDefaultCheckout()

        // Retry the entire pipeline up to 2 times if it fails
        retry(2)
    }

    stages {
        stage('Flaky network call') {
            options {
                // Per-stage options
                timeout(time: 5, unit: 'MINUTES')
                retry(3)  // Retry just this stage 3 times
            }
            steps {
                sh 'curl https://flaky-api.example.com/data'
            }
        }
    }
}
```

### Most Important Options and When to Use Them

**`timeout`** — use this always. Builds that hang (waiting for input, network stuck, process frozen) will block your entire executor queue if there is no timeout. Set a generous timeout that is longer than your slowest normal build.

**`disableConcurrentBuilds`** — use this for all deploy jobs. You never want two deploy processes running at the same time on the same server. They will conflict and corrupt each other.

**`buildDiscarder`** — use this always. Jenkins stores logs, artifacts, and test results for every build. Without a discard policy, your server disk will fill up over weeks of builds.

**`timestamps`** — great for performance debugging. When a build is slow, you can see exactly which step is taking the most time.

**`retry`** — useful for tests that have rare, intermittent failures (flaky tests), or for steps that make network calls that occasionally time out.

---

## Part 9: Advanced Patterns

### Parallel Stages

Run independent stages at the same time to speed up your pipeline. Tests and linting do not depend on each other. Run them in parallel and your 10-minute pipeline becomes a 5-minute pipeline.

```groovy
stage('Verify') {
    parallel {
        stage('Unit tests') {
            steps {
                sh 'pytest tests/unit/ -v'
            }
        }
        stage('Integration tests') {
            steps {
                sh 'pytest tests/integration/ -v'
            }
        }
        stage('Lint') {
            steps {
                sh 'flake8 app/ && black --check app/'
            }
        }
        stage('Security scan') {
            steps {
                sh 'bandit -r app/ -ll'
            }
        }
    }
    // If any one parallel stage fails, abort all the others immediately
    // Remove this line if you want all stages to finish even if one fails
    failFast true
}
```

**Practical tip:** only parallelize stages that are truly independent. If stage B uses output from stage A, they cannot run in parallel.

### Matrix Builds

Test across multiple combinations automatically. Instead of writing a separate stage for Python 3.10, 3.11, and 3.12, you write a matrix and Jenkins creates the combinations for you.

```groovy
stage('Test across versions') {
    matrix {
        axes {
            axis {
                name 'PYTHON_VERSION'
                values '3.10', '3.11', '3.12'
            }
            axis {
                name 'DJANGO_VERSION'
                values '4.2', '5.0'
            }
        }
        stages {
            stage('Run tests') {
                agent {
                    docker { image "python:${PYTHON_VERSION}-slim" }
                }
                steps {
                    sh "pip install django==${DJANGO_VERSION}"
                    sh 'pytest tests/'
                }
            }
        }
    }
}
```

This creates 6 parallel test runs: 3 Python versions × 2 Django versions.

### Shared Libraries

When you have many Jenkinsfiles across many repositories, you end up copy-pasting the same pipeline logic everywhere. Shared libraries solve this. You create a separate Git repository with reusable pipeline functions, and any Jenkinsfile can import them.

**Structure of a shared library repo:**

```
my-pipeline-library/
├── vars/
│   ├── deployApp.groovy      // Called as deployApp('staging')
│   ├── runPyTests.groovy     // Called as runPyTests('tests/unit')
│   └── buildDockerImage.groovy
└── src/
    └── com/company/
        └── PipelineUtils.groovy  // Reusable classes
```

**Example: `vars/deployApp.groovy`**

```groovy
def call(String environment, String branch = 'main') {
    echo "Deploying ${branch} to ${environment}"
    sh "ssh deploy@server './deploy.sh ${environment} ${branch}'"
}
```

**Using the shared library in a Jenkinsfile:**

```groovy
@Library('my-pipeline-library') _   // The underscore is required

pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                runPyTests('tests/')
            }
        }
        stage('Deploy') {
            steps {
                deployApp('staging', params.BRANCH)
            }
        }
    }
}
```

Register the library in Jenkins at **Manage Jenkins → Configure System → Global Pipeline Libraries**.

### Build Triggers

Control when a pipeline runs:

```groovy
pipeline {
    agent any

    triggers {
        // Run every night at 2am
        cron('H 2 * * *')

        // Poll Git every 5 minutes (webhook is better — use this as fallback)
        pollSCM('H/5 * * * *')

        // Run automatically after another job succeeds
        upstream(
            upstreamProjects: 'build-my-app',
            threshold: hudson.model.Result.SUCCESS
        )
    }

    stages {
        stage('Nightly tests') {
            steps { sh 'pytest tests/ --slow' }
        }
    }
}
```

**Webhook vs polling:** Webhooks are better. With a webhook, your Git server (Gogs, GitHub) tells Jenkins the moment code is pushed. With polling, Jenkins checks Git every N minutes — wasteful and slower. Only use polling when you cannot configure a webhook.

### Triggering Another Job from a Step

```groovy
stage('Deploy frontend') {
    steps {
        // Trigger another Jenkins job and wait for it to finish
        build job: 'deploy-ember-frontend',
              parameters: [
                  string(name: 'BRANCH', value: env.GIT_BRANCH),
                  string(name: 'BUILD_NUM', value: env.BUILD_NUMBER)
              ],
              wait: true    // false = fire and forget

        // Or trigger without waiting
        build job: 'send-release-notification', wait: false
    }
}
```

### Manual Approval Gate

Pause the pipeline and wait for a human to click "Approve" before continuing. Essential for production deployments — you want a human to confirm before code goes to real users.

```groovy
stage('Deploy to production') {
    steps {
        // Show the approval button in Jenkins UI
        input(
            message: 'Deploy to production?',
            ok: 'Yes, deploy now',
            submitter: 'devops-team,senior-devs'  // Limit who can approve
        )

        // Code below runs only after approval
        sh './deploy-production.sh'
    }
}
```

**Always combine `input` with a timeout** so the pipeline does not hang forever if nobody clicks:

```groovy
stage('Approve production deploy') {
    options {
        timeout(time: 30, unit: 'MINUTES')  // Auto-cancel after 30 minutes
    }
    steps {
        input message: 'Deploy to production?', ok: 'Deploy'
        sh './deploy-production.sh'
    }
}
```

### Stash and Unstash — Sharing Files Between Stages

When different stages run on different agents, they do not share a filesystem. `stash` saves files from one stage and `unstash` retrieves them in another.

```groovy
stage('Build') {
    agent { label 'build-agent' }
    steps {
        sh 'npm run build'
        // Save the dist folder
        stash includes: 'dist/**', name: 'frontend-build'
    }
}

stage('Deploy') {
    agent { label 'deploy-agent' }  // Different machine
    steps {
        // Retrieve the files saved by the Build stage
        unstash 'frontend-build'
        sh 'rsync -av dist/ ubuntu@webserver:/var/www/html/'
    }
}
```

---

## A Complete Real-World Jenkinsfile

Here is a full Jenkinsfile combining everything from this guide — for a Django backend service:

```groovy
pipeline {
    agent none  // Each stage declares its own agent

    options {
        timeout(time: 45, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timestamps()
        ansiColor('xterm')
    }

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['staging', 'production'],
            description: 'Where to deploy'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip tests (use for hotfixes only)'
        )
    }

    environment {
        APP_NAME    = 'my-django-app'
        DEPLOY_HOST = credentials('deploy-host')
        DB_PASSWORD = credentials('db-password')
    }

    stages {

        stage('Checkout') {
            agent { label 'ec2-agent' }
            steps {
                checkout scm
                sh 'git log --oneline -5'  // Show recent commits in log
            }
        }

        stage('Verify') {
            when {
                expression { !params.SKIP_TESTS }
            }
            parallel {
                stage('Unit tests') {
                    agent {
                        docker { image 'python:3.11-slim' }
                    }
                    steps {
                        sh '''
                            pip install -r requirements.txt -q
                            pytest tests/unit/ --junitxml=unit-results.xml -v
                        '''
                    }
                    post {
                        always { junit 'unit-results.xml' }
                    }
                }
                stage('Lint') {
                    agent {
                        docker { image 'python:3.11-slim' }
                    }
                    steps {
                        sh '''
                            pip install flake8 black -q
                            flake8 app/ --max-line-length=120
                            black --check app/
                        '''
                    }
                }
            }
        }

        stage('Build image') {
            agent { label 'ec2-agent' }
            steps {
                sh "docker build -t ${APP_NAME}:${env.BUILD_NUMBER} ."
                sh "docker tag ${APP_NAME}:${env.BUILD_NUMBER} ${APP_NAME}:latest"
            }
        }

        stage('Deploy to staging') {
            agent { label 'ec2-agent' }
            when {
                expression { params.ENVIRONMENT == 'staging' || branch 'develop' }
            }
            steps {
                sh "ssh ubuntu@${DEPLOY_HOST} 'cd /app && ./deploy.sh ${env.BUILD_NUMBER} staging'"
            }
        }

        stage('Approve production') {
            when {
                allOf {
                    expression { params.ENVIRONMENT == 'production' }
                    branch 'main'
                }
            }
            options {
                timeout(time: 30, unit: 'MINUTES')
            }
            steps {
                input(
                    message: "Deploy build #${env.BUILD_NUMBER} to production?",
                    ok: 'Deploy to production',
                    submitter: 'devops-team'
                )
            }
        }

        stage('Deploy to production') {
            agent { label 'ec2-agent' }
            when {
                allOf {
                    expression { params.ENVIRONMENT == 'production' }
                    branch 'main'
                }
            }
            steps {
                sh "ssh ubuntu@${DEPLOY_HOST} 'cd /app && ./deploy.sh ${env.BUILD_NUMBER} production'"
                sh "ssh ubuntu@${DEPLOY_HOST} 'systemctl status gunicorn'"  // Verify it came up
            }
        }

    }

    post {
        always {
            node('ec2-agent') {
                cleanWs()
            }
        }
        success {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "✓ ${APP_NAME} #${env.BUILD_NUMBER} deployed to ${params.ENVIRONMENT} — ${env.BUILD_URL}"
            )
        }
        failure {
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: "✗ ${APP_NAME} #${env.BUILD_NUMBER} FAILED — ${env.BUILD_URL}"
            )
        }
        fixed {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "Build is green again — ${APP_NAME} #${env.BUILD_NUMBER}"
            )
        }
    }
}
```

---

## Quick Reference Card

### Directive Summary

| Directive | Where it goes | What it does |
|---|---|---|
| `pipeline { }` | Top level | Outer wrapper. Required. |
| `agent` | Inside pipeline or stage | Which machine to run on |
| `environment { }` | Inside pipeline or stage | Define env variables |
| `parameters { }` | Inside pipeline | Accept user inputs |
| `options { }` | Inside pipeline or stage | Timeouts, retries, log settings |
| `tools { }` | Inside pipeline or stage | Auto-install tools (Maven, Node, etc.) |
| `triggers { }` | Inside pipeline | Cron schedule, SCM poll, upstream job |
| `stages { }` | Inside pipeline | Container for all stages |
| `stage('name') { }` | Inside stages | One phase of the pipeline |
| `steps { }` | Inside stage | The actual commands |
| `when { }` | Inside stage | Conditional execution |
| `post { }` | Inside pipeline or stage | Run after completion |
| `parallel { }` | Inside stage | Run stages simultaneously |

### Common Shell Step Patterns

```groovy
// Basic command
sh 'command'

// Multi-line commands (triple quotes)
sh '''
    line one
    line two
    line three
'''

// Capture output
def output = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()

// Check exit code without failing
def exitCode = sh(script: 'test -f file.txt', returnStatus: true)
if (exitCode == 0) { echo 'File exists' }

// Run as a specific user
sh 'sudo -u deploy ./deploy.sh'
```

### agent `when` Conditions Cheat Sheet

```groovy
when { branch 'main' }
when { branch pattern: 'release/.*', comparator: 'REGEXP' }
when { environment name: 'DEPLOY', value: 'true' }
when { expression { params.ENVIRONMENT == 'production' } }
when { not { branch 'develop' } }
when { anyOf { branch 'main'; branch 'staging' } }
when { allOf { branch 'main'; expression { params.DEPLOY == true } } }
when { changeRequest() }        // Only on pull request builds
when { triggeredBy 'UserIdCause' }  // Only when triggered manually
```

---

## What to Learn Next

Once you are comfortable with everything in this guide, these are the natural next steps:

**Jenkins Security** — RBAC (role-based access control) to control who can run which jobs. OAuth login via GitHub or Google. Audit logs. HTTPS via Nginx reverse proxy. All essential before exposing Jenkins to a team.

**Multibranch Pipelines** — Jenkins automatically creates a new pipeline job for every branch in your repository. Each branch gets its own build history. Pull requests get their own builds. Very useful for team workflows.

**Blue Ocean UI** — Jenkins' modern visual interface. Shows your pipeline as a graphic flow. Makes it easy to see which stage failed and why.

**Jenkins Configuration as Code (JCasC)** — Define your entire Jenkins configuration (users, credentials, plugins, agent templates) as a YAML file. When you need to rebuild your Jenkins server, you apply the file and it is fully configured automatically. No clicking through the UI.

**Kubernetes agents** — Instead of EC2 instances, spin up Kubernetes pods as agents. Even faster startup than EC2, and Kubernetes handles scaling automatically.

**Observability** — Connect Jenkins to Prometheus and Grafana to monitor build durations, failure rates, queue times, and agent utilization. Know when your pipeline is slow before your team complains about it.