# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RD-Agent is a Microsoft Research framework for automating industrial R&D processes, particularly in data-driven scenarios. It implements an iterative "Research & Development" loop where an agent proposes ideas (R) and implements them (D), with the results feeding back into the next cycle. The framework leads MLE-bench as the top ML engineering agent and supports quantitative finance, data science/Kaggle, LLM fine-tuning, and RL scenarios.

## Build/Test/Lint Commands

```bash
# Install dev environment (all optional deps + pre-commit hook)
make dev

# Install package only
make install

# Lint (executed in order: isort -> black -> toml-sort, then mypy + ruff on rdagent/core)
make lint

# Auto-fix isort + black + toml-sort
make auto-lint

# Run mypy on core only
make mypy

# Run ruff on core only
make ruff

# Run all tests with coverage
make test

# Run offline tests only (no external API calls, marked with @pytest.mark.offline)
make test-offline

# Run a single test file
python -m pytest test/path/to/test_file.py -s -l

# Run tests matching a marker
python -m pytest -m "offline"

# CLI entry
rdagent --help

# Start web UI for log traces
rdagent ui

# Start Flask log server
rdagent server_ui
```

## Environment & Configuration

- Copy `.env.example` to `.env` and fill in LLM API keys
- Settings are defined via `pydantic-settings` (see `rdagent/core/conf.py` and `rdagent/oai/llm_conf.py`)
- The CLI auto-loads `.env` via `dotenv` before any command runs
- **LiteLLM** is the default LLM backend (`rdagent.oai.backend.LiteLLMAPIBackend`)
- APE key and model are configured via env vars: `OPENAI_API_KEY`, `OPENAI_API_BASE`, `CHAT_MODEL`, `EMBEDDING_MODEL`, etc.
- LiteLLM proxy can be used for embedding via `LITELLM_PROXY_API_KEY`/`LITELLM_PROXY_API_BASE`

## Architecture & Key Modules

### Core Framework (`rdagent/core/`)

The framework is built around an iterative **R&D loop** with these abstractions:

- **Scenario** (`scenario.py`): Describes the problem context — background, source data, runtime environment. Acts as configuration context passed through the framework.
- **EvolvableSubjects** (`evolving_framework.py`): The object being evolved (e.g., a set of factors + model). Subclasses of `EvaluableObj`.
- **EvolvingStrategy** (`evolving_framework.py`): Defines how subjects evolve each iteration via `evolve_iter()` — a generator that yields partially-evolved subjects.
- **RAGEvaluator / IterEvaluator** (`evaluation.py`, `evolving_agent.py`): Evaluates evolved subjects iteratively via `evaluate_iter()` — a generator that receives partial evolutions and yields partial feedback. The final `Feedback` determines if the loop should continue.
- **RAGStrategy** (`evolving_framework.py`): Retrieval-Augmented Generation for knowledge querying and self-generation from the evolving trace.
- **RAGEvoAgent** (`evolving_agent.py`): Orchestrator — runs the loop: RAG query → evolving → evaluation → trace update → knowledge self-gen → yield control.
- **Experiment / Task** (`experiment.py`): Organizes work units. `Task` has a name, description, and optional user instructions.
- **Hypothesis / ExperimentFeedback / Proposal** (`proposal.py`): Higher-level constructs for generating and validating research hypotheses in the loop.
- **Developer** (`developer.py`) / **Interactor** (`interactor.py`): Abstract interfaces for developing experiments and user interaction.

### Components (`rdagent/components/`)

Reusable building blocks:
- `agent/` — Agent implementations (base, context7, MCP, RAG)
- `coder/` — Code generators (CoSTEER, data_science, factor_coder, model_coder, finetune, RL)
- `runner/` — Execution runners
- `proposal/`, `interactor/`, `loader/`, `benchmark/`, `document_reader/`, `knowledge_management/`, `workflow/`

### LLM Interface (`rdagent/oai/`)

- `backend/` — Backend implementations: `base.py` (abstract), `litellm.py` (default), `deprec.py` (legacy), `pydantic_ai.py`
- `llm_conf.py` — All LLM settings via `LLMSettings`
- `llm_utils.py` — Utilities for LLM interaction

### Scenarios (`rdagent/scenarios/`)

Scenario-specific implementations:
- `qlib/` — Quantitative finance (factor discovery, model development, combined quant)
- `data_science/` — General data science / MLE-bench
- `kaggle/` — Kaggle competition agent
- `finetune/` — LLM fine-tuning
- `general_model/` — General model extraction from reports
- `rl/` — Reinforcement learning
- `shared/` — Shared code across scenarios

### Applications (`rdagent/app/`)

Entry point is `cli.py` (via `typer`). Each scenario has its own loop:
- `fin_factor`, `fin_model`, `fin_quant`, `fin_factor_report` — Quantitative finance
- `data_science` — Data science / Kaggle / MLE-bench
- `llm_finetune` — LLM fine-tuning
- `general_model` — Model extraction from reports

## Key Technical Patterns

- **Generator-based iteration**: The evolve/evaluate loop uses Python generators. `evolve_iter()` yields partial solutions, `evaluate_iter()` yields partial feedback, and they advance in lockstep via `send()`.
- **In-place mutation**: Evolved subjects are modified in-place during the loop.
- **Knowledge self-generation**: After each loop, RAG can extract new knowledge from the evolving trace and persist it.
- **Conventional commits**: Commit messages follow `@commitlint/config-conventional` with types: build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test.
- **Pre-commit hooks**: Installed as pre-push hooks; configured in `.commitlintrc.js`.
- **Workspace isolation**: Generated artifacts stored in `git_ignore_folder/` (gitignored).
