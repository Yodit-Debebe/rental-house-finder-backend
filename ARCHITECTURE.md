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

### Infrastructure layout

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