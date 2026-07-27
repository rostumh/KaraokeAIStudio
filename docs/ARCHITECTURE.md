# Architecture

## Dependency rule

Dependencies point inward: `ui` and `infrastructure` depend on `application`; `application` depends on `domain`; the domain does not import Qt, FFmpeg, SQLite, PyTorch, or operating-system APIs. `app.bootstrap` is the composition root and is the only place that constructs the process-wide object graph.

## Layer responsibilities

- **domain**: stable business entities, value objects, and rules.
- **application**: use cases and ports; coordinates domain behavior without knowing technologies.
- **infrastructure**: port implementations for SQLite, files, FFmpeg, AI engines, and network services.
- **services**: reusable orchestration that does not belong to a single view.
- **models**: AI model lifecycle, metadata, caching, and inference boundaries.
- **ui**: PySide6 views, reusable widgets, and MVVM view models.
- **core**: configuration, logging, paths, errors, and other cross-cutting concerns.

## Runtime policy

User-writable state never goes into the installation directory. `platformdirs` selects per-user config, data, cache, and log locations. This is required for installed Windows applications, where `Program Files` is not writable by standard users.

## Evolution

Each later module adds use cases and adapters behind explicit interfaces. Long work will run outside the GUI thread through cancellable jobs. SQLite access will be transactional, and schema changes will use numbered migrations. External executables and models will be discovered and validated rather than assumed.
