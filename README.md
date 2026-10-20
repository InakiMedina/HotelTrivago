# HotelTrivago

Final academic testing project for Quality Assurance and Software Engineering.

A monolithic, multi-portal booking and management platform built with a Python REST API, vanilla JavaScript multi-page client/employee frontends, and MongoDB, fully containerized for local development and AWS deployment.

---

## Architecture & Technology Stack

| Domain | Technology | Details |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+ | REST API (FastAPI / Flask) |
| **Frontend** | Vanilla JS / HTML5 / CSS3 | Multi-portal architecture (Client & Employee dashboards) |
| **Tooling / Bundler** | Vite | Multi-Page App (MPA) build system |
| **Database** | MongoDB | Document store managed via PyMongo / Motor |
| **Testing & QA** | Playwright & Pytest | Full browser E2E workflows, API regression, unit test suites |
| **Linting & Code Quality** | Pylint, ESLint, Prettier | Enforced across pre-commit hooks and CI pipelines |
| **DevOps & Infra** | Docker Compose, AWS | Local multi-service orchestration and containerized deployment |

---

## Repository Structure

```text
HotelTrivago/
├── .github/
│   └── workflows/              # Path-filtered CI/CD pipelines (Lint, Test, Deploy)
├── backend/                    # Python API service
│   ├── src/                    # API routes, business logic, MongoDB connection
│   ├── tests/                  # Unit and integration tests (pytest)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Vanilla JS client applications
│   ├── public/                 # Static assets (images, common styling)
│   ├── src/
│   │   ├── shared/             # Common API wrappers, auth, formatting utilities
│   │   ├──
```

## Roles and Responsibilities

While all 6 team members contribute across the entire codebase, domain leads oversee verification and standards for each area:

##### Inaki Medina Munguia
**Project Manager (PM):** Scope management, backlog tracking, acceptance criteria, milestone releases.

##### Carlos Emilio Olmedo Navarro
**Frontend Lead:** Multi-portal architecture (/src/client, /src/employee), state flow, shared API consumers.

##### Isaac Ernesto Vasquez Sandoval
**Backend Lead:** API endpoint design, business logic, route handlers, backend performance.

##### Angel Isaac Barbarin Cuevas
**Database (DB) Lead:** MongoDB collections, schema validation, index optimization, initial seed datasets.

##### Gilberto Anaya Mercado
**Quality Assurance (QA) Lead:** End-to-end tests (/e2e), API automated checks, bug tracking, edge case coverage.

##### Fabian Patricio Gaxiola Valades
**DevOps Lead:** Docker container setups, GitHub Actions CI workflows, AWS deployment infrastructure.

## Getting Started

#### Prerequisites
- Docker Desktop (v24+)
- Node.js (v18+)
- Python (v3.11+)
- Make utility (GNU Make)

#### Local Environment Setup

1) Clone the repository:
```
git clone https://github.com/InakiMedina/HotelTrivago.git

cd HotelTrivago
```

2) Environment Variables:
Copy the example environment file and configure variables:
```
cp .env.example .env
```

3) Start All Services (Docker):
Copy the example environment file and configure variables:
```
docker compose up --build
```

- Client Portal: http://localhost:5173/client/
- Employee Portal: http://localhost:5173/employee/
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MongoDB Engine: localhost:27017

#### Branching Strategy

**main** deploy branch, can't be modified. 
Update on deliveries or deploys by PR beta -> main
Merge Commit (never Squash or Rebase here, or main and deploy histories will diverge).

**beta** working branch, can't be merged
Updated by pr accepted by another member
requirement to merge:
- All tests passed
- Code coverage > 70%
- No linter errors

**personal branches**
examples:
- docs/api-endpoints-guide
- fix/login-session-timeout
- feat/stripe-webhook-handler
- chore/upgrade-node-runtime
- refactor/auth-middleware

after pr is accepted, branch is deleted
for cleaning them in your local machine:
```
git fetch --prune
```
