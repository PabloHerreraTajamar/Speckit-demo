# Contracts - Task File Attachments

**Date**: 2026-01-19  
**Feature**: 003-task-attachments  
**Version**: 1.0.0

## Purpose

This directory contains interface contracts for the Task Attachments feature. Contracts define pre-conditions, post-conditions, and invariants for all public interfaces.

## Contracts

1. **views.md** - View layer contracts (upload, download, delete endpoints)
2. **models.md** - Model layer contracts (Attachment model, validators)
3. **storage.md** - Storage backend contracts (Azure Blob Storage operations)

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
