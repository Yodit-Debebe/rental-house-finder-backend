# Architecture Rules

## Architecture Style

The backend follows:

- Domain-Driven Design
- Hexagonal Architecture
- Modular Monolith

## Dependency Rules

### Domain

Domain must not depend on:

- Django
- Django REST Framework
- PostgreSQL
- Keycloak
- Kafka
- OpenAI

### Application

Application may depend on:

- Domain

Application defines ports/interfaces for external dependencies.

### Infrastructure

Infrastructure implements application/domain ports.

Infrastructure may depend on:

- Django
- PostgreSQL
- Keycloak
- Kafka
- External APIs

### Interfaces

Interfaces translate external requests into application use cases.

## Module Ownership

### Backend Developer 1

- Identity
- Property Management
- Landlord
- Administration

### Backend Developer 2

- Tenant
- AI Search

### Module layout

Each module is organized by layer, and each layer by concept:

```text
<module>/
├── domain/
│   ├── entities/        # one file per entity
│   ├── value_objects/   # one file per value object
│   ├── repositories/    # repository interfaces (ports owned by domain)
│   ├── services/        # stateless domain services
│   ├── events/          # domain events
│   └── exceptions.py    # domain errors
├── application/
│   ├── commands/        # write-operation input DTOs
│   ├── queries/         # read-operation input DTOs
│   ├── dto/             # output DTOs
│   ├── ports/           # outbound interfaces (hashing, tokens, ...)
│   ├── use_cases/       # orchestration, one file per use case
│   └── exceptions.py
├── infrastructure/
│   ├── persistence/     # repository implementations (Django ORM)
│   ├── security/        # password hashing and token adapters
│   └── keycloak/        # identity provider adapter (future)
└── interfaces/
    └── http/            # serializers, views, urls
```

Package `__init__.py` files re-export the public names of each concept, so
consumers import from the package (e.g. `identity.domain.entities`), not from
deep module paths.

## Infrastructure layout

- Top-level `infrastructure/` — shared technical adapters used by all
  modules (database utilities, Keycloak client, Kafka client, storage).
  Contains technology code only, never business rules.
- `<module>/infrastructure/` — module-specific adapters that implement
  that module's application ports (e.g., PropertyRepository via Django ORM).
  Used only inside its own module. Never imported by other modules.
- Top-level `shared/` — code genuinely used by 2+ modules
  (API helpers, base types, exceptions). Never a place to hide
  module-specific logic.

## Cross-module communication

Modules should not directly access another module's internal
implementation.

Use:

- Application ports
- Domain events
- Explicit contracts