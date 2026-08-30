# StockFlow WMS

A warehouse management system designed for real-world inventory and
fulfillment workflows.

[English](README.md) | [Русский](README.ru.md)

## Overview

StockFlow WMS is a modular warehouse management system for managing
inventory, warehouse operations, orders, and related workflows.

The system is built around independently deployable services and
asynchronous processing, with a focus on reliability, observability,
and predictable operation under load.

The project is currently under active development.

## Core Capabilities

- Warehouse and inventory management
- Product and stock tracking
- Order processing
- Inventory reservations
- Warehouse operations and fulfillment workflows
- Asynchronous background processing
- Event-driven service communication
- Authentication and authorization
- Monitoring and system observability

Additional capabilities are being introduced as the system evolves.

## Architecture

The system follows a microservice architecture with clear service
boundaries and isolated responsibilities.

Services communicate through synchronous APIs and asynchronous
messaging where appropriate.

Each service is designed to own its application logic and data,
minimizing direct coupling between services.

Detailed architecture documentation is available in [`docs/`](docs/)
and is updated alongside architectural changes.

## Technology Stack

### Backend

- Python 3.14
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- RabbitMQ
- Celery

### Frontend

- React
- TypeScript

### Infrastructure

- Docker
- Docker Compose
- GitHub Actions

### Observability

- Metrics
- Structured logging
- Distributed tracing
- Service health monitoring

The infrastructure stack is being introduced incrementally as
corresponding system components are implemented.

## Development

The project uses a feature-based Git workflow with pull requests,
automated quality checks, and CI pipelines.

Development tooling includes:

- Ruff
- Mypy
- Pytest
- Pre-commit
- GitHub Actions

Code quality checks are performed automatically before changes are
merged.

## Testing

The project uses multiple levels of automated testing, including:

- Unit tests
- Integration tests
- API tests
- End-to-end tests
- Smoke tests

The test strategy is documented in [`docs/`](docs/) and evolves together
with the system architecture.

## Running Locally

The application and supporting infrastructure are designed to run
through Docker Compose.

Detailed setup instructions, environment configuration, service
startup, and troubleshooting are available in the project
documentation.

## API

API documentation is provided by the backend services and is available
through their OpenAPI interfaces.

Service-specific API documentation will be maintained alongside the
corresponding services.

## Project Status

Active development.

Current implementation and architecture may evolve as new system
components are introduced.

## Documentation

- Architecture
- Development workflow
- Testing strategy
- Deployment
- Observability
- Architecture Decision Records (ADR)

Documentation is maintained alongside the system rather than as a
separate specification.

## License

License information will be provided with the first public release.
