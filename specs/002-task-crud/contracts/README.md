# Contracts - Task CRUD Operations

**Date**: 2026-01-19  
**Feature**: 002-task-crud  
**Version**: 1.0.0

## Purpose

This directory contains interface contracts for the Task CRUD feature. Contracts define pre-conditions, post-conditions, and invariants for all public interfaces.

## Contracts

1. **views.md** - View layer contracts (CRUD endpoints)
2. **models.md** - Model layer contracts (Task model, QuerySet)

## Versioning

All contracts follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes to public interfaces
- **MINOR**: Backward-compatible additions
- **PATCH**: Documentation or clarification updates

## Usage

Reference contracts during:
- Implementation (to ensure adherence)
- Testing (to derive test cases)
- Code review (to verify correctness)
- Refactoring (to maintain compatibility)
