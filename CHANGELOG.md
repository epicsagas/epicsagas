# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [0.6.0] - 2026-08-02

### Added
- **code-port** — cross-language file porting skill. Generalized from a production Zig→Rust porting guide into a language-agnostic two-phase methodology: Phase A writes a faithful draft (need-not-compile, optimized for source↔draft diffing), Phase B compiles module-by-module. Preserves structure (names, field order, control flow), infers ownership/error/null/concurrency/generics mappings instead of guessing, preserves safety levels (checked stays checked, `unsafe` stays annotated), and marks every uncertain spot with `TODO(port)` / `PERF(port)` / `PORT NOTE`. Ships per-language pitfall references for Rust, Go, C/C++, Python, TypeScript, JVM (Java/Kotlin), C#, and Zig — covering the most-used language families.

## [0.5.0] - 2026-07-25

### Added
- **korean-polish 윤문 suite** — 오케스트레이터 스킬 + 5개 전문 스킬(`korean-cohesion`, `korean-norm-lint`, `korean-register`, `korean-translationese`, `korean-verbosity`) + 참고자료(academic-connectives, economics-glossary, regex-pack, translationese-table)
- **criticality workflow** — OpenSSF `criticality_score`를 매주 월요일 자동 산출해 커밋하는 GitHub Actions 워크플로 추가

### Fixed
- `git-workspace bump`: Rust 저장소는 태깅 전 `Cargo.toml` 버전을 먼저 올리고 릴리즈 커밋을 남기도록 수정 — 버전 불일치로 인한 cargo-dist 릴리즈 실패(claudy v0.6.0, 2026-07-24) 재발 방지
- `criticality` 워크플로: 출력을 영어로 통일, rate-limit 대기용 저장소별 타임아웃 상향

[0.6.0]: https://github.com/epicsagas/epicsagas/releases/tag/v0.6.0
[0.5.0]: https://github.com/epicsagas/epicsagas/releases/tag/v0.5.0
