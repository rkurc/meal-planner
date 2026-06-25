# Agent Instructions

This document provides guidelines for AI agents working in this repository.

## Development Workflow

### Code Quality: Linting and Formatting

This project uses `pre-commit` to enforce code quality standards using `black` for formatting and `pylint` for linting.

#### One-Time Setup

Before you start working, you need to set up the pre-commit hooks.

1.  **Install Dependencies:** Make sure all development dependencies, including `pre-commit`, are installed. You can find them in `pyproject.toml` under `[project.optional-dependencies].dev`. If you have a modern `pip`, you can install the project in editable mode with the dev dependencies like this:
    ```bash
    pip install -e .[dev]
    ```

2.  **Install the Git Hook:** Install the hooks so they run automatically before each commit.
    ```bash
    pre-commit install
    ```
    *Note for Agents in Sandboxed Environments:* If the above command fails due to a locked `core.hooksPath` configuration, you can skip this step. The hook will not run automatically, but you **must** run the checks manually before submitting your work.

#### Running the Hooks

The hooks will run automatically on `git commit` if they were installed successfully.

To run the hooks manually on all files at any time, use the following command:
```bash
pre-commit run --all-files
```

You are expected to ensure that all linter and formatter checks pass before submitting your code. If a hook fails, it may modify files. You should review these changes and `git add` them before committing again.

**Important:** Because this project is Docker-first, run black, pylint, and related checks inside a container matching the dev or CI image whenever possible (see "Docker-First Development" section below). The `pre-commit run --all-files` command on the host is acceptable only as a last resort or when the devcontainer already provides the tools.

### Frontend Code Formatting

The frontend code in the `frontend/` directory is formatted using `prettier`.
Before submitting your work, you must ensure that the frontend code is formatted correctly.

To check for formatting issues, run the following command from the `frontend/` directory:
```bash
npm run format-check
```

If there are any formatting issues, you can fix them by running:
```bash
npm run format
```

**These commands must be executed inside Docker** (see "Running Frontend Tooling Inside Docker" below). Do not invoke them with a host `npm`.

(Note: You may need to add the `format` and `format-check` scripts to `frontend/package.json` if they do not exist. They should run `prettier --write .` and `prettier --check .` respectively.)

### Running Frontend Tooling Inside Docker
Even `npm run format-check`, `npm run format`, `npm run lint`, and lockfile operations must be executed inside a container using the same Node image as the build (e.g. `node:20-alpine`).

Examples:

```bash
# Run prettier checks / fixes
docker run --rm -v "$(pwd)/frontend:/app" -w /app node:20-alpine \
  sh -c 'npm ci --no-audit --no-fund --silent && npm run format-check'

# Fix formatting
docker run --rm -v "$(pwd)/frontend:/app" -w /app node:20-alpine \
  sh -c 'npm ci --no-audit --no-fund --silent && npm run format'
```

## Docker-First Development and Build Practices

All development, verification, testing, formatting, and building **must** be performed using Docker. Do not run `python`, `pip`, `node`, `npm`, `black`, `pylint`, `prettier`, or `pytest` directly on the host machine.

### Why Docker-First?
- Guarantees the exact same Node/Python versions, OS base, and native bindings (e.g. @tailwindcss/oxide) as CI and production.
- Prevents "works on my machine" caused by host Node 18 vs required 20, different npm versions, or missing system libs.
- The project uses `docker-bake.hcl` precisely to keep `Dockerfile`, `.devcontainer/Dockerfile`, and CI in sync.

### Lockfile Discipline (npm)
- Dockerfiles use `RUN npm ci` (strict: `package.json` and `package-lock.json` **must** be in sync).
- After any change to `frontend/package.json` (especially eslint, vite, babel, react plugins, tailwind), **immediately** regenerate the lockfile using the matching Node image:
  ```bash
  docker run --rm \
    -v "$(pwd)/frontend:/app" \
    -w /app \
    node:20-alpine \
    sh -c 'rm -rf node_modules package-lock.json && npm install'
  ```
- Then **verify** by running the actual command users/CI use:
  ```bash
  docker buildx bake prod
  ```
- Never commit a `package.json` change without a matching updated lockfile produced in the build image.

### Build Context Hygiene
- Always maintain a root `.dockerignore`.
- At minimum it must exclude:
  - `node_modules/` and `frontend/node_modules/`
  - `__pycache__/`, `*.pyc`
  - `.git/`
  - `dist/`, build outputs, test results
- A missing or incomplete `.dockerignore` leads to slow context transfers, bloated image layers, and accidental inclusion of host artifacts.
- `.dockerignore` must itself be committed (do not list it in `.gitignore`). It is a build-time artifact that must be present for all users and CI.

### Protecting Generated Files from Formatters
- Add (and keep up to date) `frontend/.prettierignore`:
  ```
  package-lock.json
  node_modules/
  dist/
  ```
- `prettier --write .` must never touch `package-lock.json` (npm expects a specific format; reformatting can break subsequent `npm ci`).

### Using docker buildx bake
- Prefer `docker buildx bake prod` / `dev` / `ci` over raw `docker build`.
- Use `docker buildx bake --print` to debug variable/ARG resolution.
- After edits to `Dockerfile`, `docker-bake.hcl`, `.devcontainer/Dockerfile`, or CI workflows, re-run the bake targets that will be used in production/CI.
- Override versions explicitly when testing: `NODE_VERSION=20.19 PYTHON_VERSION=3.9 docker buildx bake prod`.
- Note on CI: The native "backend" and "frontend" jobs in `.github/workflows/ci.yml` are a lightweight exception (they pin versions via setup-python/setup-node to match bake defaults). The dedicated "docker" job + integration tests provide the full bake verification. Prefer bake where possible.

### Verification Discipline
- After fixing a Docker-related failure, actually execute the failing command the user reported and capture key success output (e.g. the `npm ci` step completing and "exporting to image ... DONE").
- Record the verification (command + outcome) when updating `.ai/next_step.md`.
- Do not claim "build fixed" until `docker buildx bake prod` (or equivalent) has been observed to succeed in the current tree.

### Docker Volume Mount Side Effects
- Running `npm install` / `npm ci` inside a volume-mounted container often creates files owned by root (UID 0).
- Git is unaffected (it stores content, not ownership). You may run `chown` after the container exits if desired for local cleanliness:
  ```bash
  chown -R $(id -u):$(id -g) frontend/package-lock.json
  ```
- Clean up temporary `node_modules` created during lock regeneration before committing.

### Running All Checks via the meal-planner-dev Docker Image (Required)

For consistency (especially in sandboxed or CI-like environments), invoke **every** format, lint, pre-commit, pytest, and playwright command through the Docker dev image:

```bash
# All checks via Docker dev image (required)
docker run --rm -v $(pwd):/app -w /app meal-planner-dev python -m pytest meal_planner_app/tests/ -q --tb=no
docker run --rm -v $(pwd)/frontend:/app/frontend -w /app/frontend meal-planner-dev npm run format-check
docker run --rm -v $(pwd)/frontend:/app/frontend -w /app/frontend meal-planner-dev npm run lint
docker run --rm -v $(pwd):/app -w /app meal-planner-dev pre-commit run --all-files
docker run --rm -v $(pwd)/frontend:/app/frontend -w /app/frontend meal-planner-dev npm test
```

See also the `.devcontainer/Dockerfile` and docs/superpowers plans for details. Direct host runs are for convenience only when tools are locally available.

## Task Management

### The `.ai/next_step.md` File

Before committing your work, you should always update the `.ai/next_step.md` file. This file should contain a summary of the work you have completed and a clear description of the next steps for the project. This ensures a smooth handover to the next agent.

When starting a new task, always read the `.ai/next_step.md` file first to understand the current state of the project and what needs to be done next.

#### Updating `.ai/next_step.md`
- Summarize what was actually done (with concrete commands and evidence where possible, e.g. "docker buildx bake prod now succeeds with 'exporting to image ... DONE'").
- Describe clear next steps.
- Commit the update together with the code changes in the same commit.
- This is mandatory before handing off or pushing.

#### Publishing Your Work
- After completing changes on a feature branch, push the branch ("publish your changes").
- When asked, report the last commit SHA (`git log -1 --oneline`).
- Do not leave important fixes only in a local worktree or un-pushed.
