# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-09-11
### Added
- `9r skill show`: Print agent skill definition directly.
- `9r skill install`: Self-install agent skill into target directory (`~/.pi/agent/skills/9router/` or `./.pi/skills/9router/`).
- Bundled packaged skill resource.

## [0.1.0] - 2026-09-11
### Added
- Initial project scaffolding and OpenAPI specifications.
- Core HTTP client with automatic `~/.9router/` machine token derivation.
- Support for Combos, Providers, Models, API Keys, Settings, and Tools CLI commands.
- E2E test suite running against local 9Router server.
