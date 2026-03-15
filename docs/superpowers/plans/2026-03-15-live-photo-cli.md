# Live Photo CLI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal Python CLI that turns a cover image and MOV into a Live Photo-compatible asset pair.

**Architecture:** Use a small Python package with a thin CLI entrypoint and focused services for dependency checks, identifier generation, and external command orchestration. Delegate container and metadata work to `ffmpeg` and `exiftool` rather than reimplementing binary formats in Python.

**Tech Stack:** Python 3.14+, argparse, pathlib, subprocess, unittest, ffmpeg, exiftool

---

## Chunk 1: Project Skeleton

### Task 1: Create package and test layout

**Files:**
- Create: `pyproject.toml`
- Create: `src/isekai_live/__init__.py`
- Create: `src/isekai_live/cli.py`
- Create: `src/isekai_live/deps.py`
- Create: `src/isekai_live/live_photo.py`
- Create: `tests/test_cli.py`
- Create: `tests/test_live_photo.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run tests and verify import / behavior failures**
- [ ] **Step 3: Add the minimal implementation**
- [ ] **Step 4: Re-run the targeted tests**

## Chunk 2: Metadata Workflow

### Task 2: Encode the command plan for image/video pairing

**Files:**
- Modify: `src/isekai_live/live_photo.py`
- Test: `tests/test_live_photo.py`

- [ ] **Step 1: Write failing tests for asset ID generation and command planning**
- [ ] **Step 2: Run targeted tests to verify they fail for the expected reason**
- [ ] **Step 3: Implement minimal command planning and validation**
- [ ] **Step 4: Re-run targeted tests to verify they pass**

## Chunk 3: CLI Surface

### Task 3: Expose a usable command-line interface

**Files:**
- Modify: `src/isekai_live/cli.py`
- Modify: `src/isekai_live/deps.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests for argument parsing and dependency errors**
- [ ] **Step 2: Run targeted tests to verify failures**
- [ ] **Step 3: Implement the minimal CLI behavior**
- [ ] **Step 4: Re-run targeted tests to verify they pass**

## Chunk 4: Docs

### Task 4: Document usage and project scope

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README for open-source installation, usage, and limitations**
- [ ] **Step 2: Verify commands and examples match the implementation**
