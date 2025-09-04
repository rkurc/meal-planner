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
(Note: You may need to add the `format` script to `frontend/package.json` if it does not exist. It should run `prettier --write .`)

## Task Management

### The `.ai/next_step.md` File

Before committing your work, you should always update the `.ai/next_step.md` file. This file should contain a summary of the work you have completed and a clear description of the next steps for the project. This ensures a smooth handover to the next agent.

When starting a new task, always read the `.ai/next_step.md` file first to understand the current state of the project and what needs to be done next.
