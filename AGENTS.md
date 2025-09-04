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
