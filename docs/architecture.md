# Architecture — Assistant Core Lab

## 1. Project Overview

Assistant Core Lab is a modular Python application that processes user messages and provides responses related to university offices, tuition fees, and handbook rules.

The project follows a modular architecture. Each module has a specific responsibility, separating configuration, request routing, data access, business logic, response generation, and logging.

## 2. Project Structure

```text
assistant_core_lab/
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── offices.csv
│   └── handbook.json
├── docs/
│   └── architecture.md
├── src/
│   └── assistant_core/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── errors.py
│       ├── models.py
│       ├── router.py
│       ├── knowledge.py
│       ├── tools.py
│       ├── responder.py
│       ├── service.py
│       └── logging_setup.py
└── tests/
    ├── conftest.py
    ├── test_tools.py
    ├── test_router.py
    └── test_service.py
```

## 3. Module Responsibilities

| Module | Responsibility |
|---|---|
| `config.py` | Loads and validates application settings. |
| `errors.py` | Defines application-specific exceptions. |
| `models.py` | Defines data models, intents, and response structures. |
| `router.py` | Identifies the intent of a user message. |
| `knowledge.py` | Loads and searches office and handbook data. |
| `tools.py` | Implements utility functions, including credit parsing and tuition calculation. |
| `responder.py` | Generates explanations for handbook rules and supports fallback responses. |
| `service.py` | Coordinates request processing and constructs responses. |
| `logging_setup.py` | Configures application logging. |
| `__main__.py` | Provides the application entry point. |
| `__init__.py` | Marks the package and may expose selected package-level objects. |

## 4. Request Processing Flow

1. The application starts through `__main__.py`.
2. Configuration is loaded using `config.py`.
3. The application receives a user message.
4. `router.py` determines the message intent.
5. `service.py` dispatches the message to the appropriate processing logic.
6. For greeting messages, the service returns a greeting response.
7. For tuition questions, `tools.py` parses credit information and calculates tuition fees.
8. For office questions, `knowledge.py` searches the office records in `data/offices.csv`.
9. For handbook questions, `knowledge.py` searches the rules in `data/handbook.json`, and `responder.py` generates an explanation.
10. The service returns a structured response to the caller.

## 5. Error Handling and Fallback

The application uses custom exceptions defined in `errors.py` to represent expected errors, such as invalid requests, configuration errors, data errors, and provider failures.

The service handles expected errors and returns structured responses. If the primary responder encounters a provider failure, a template-based fallback can provide an alternative explanation when configured in the application.

This design helps distinguish expected application errors from unexpected programming errors.

## 6. Configuration and Data Management

Application settings are managed by `config.py`. Environment variables can be documented in `.env.example`, while `.gitignore` helps prevent local environment files and generated artifacts from being committed.

The application stores office information in `data/offices.csv` and handbook rules in `data/handbook.json`.

Keeping data separate from source code makes records easier to update without changing the core application logic.

## 7. Testing and Code Quality

The `tests/` directory contains automated tests:

- `conftest.py` provides shared test fixtures and setup.
- `test_tools.py` tests utility functions and tuition calculations.
- `test_router.py` tests message intent routing.
- `test_service.py` tests the service's request processing and response behavior.

Pytest runs the automated tests, and Ruff checks code quality. GitHub Actions can run these checks automatically when changes are pushed or pull requests are opened.

## 8. RAG Flow (Retrieval-Augmented Generation)

When the router classifies a message as `RULE` intent, the application uses a lightweight retrieve-then-generate pipeline:

```
User message
     │
     ▼
 router.py  ──────── Intent.RULE ─────────────────────┐
                                                       │
                                               knowledge.py
                                           Handbook.search()
                                           (keyword match over
                                            handbook.json rules)
                                                       │
                                               Rule {id, title, text}
                                                       │
                                           ┌───────────┴───────────┐
                                     responder.py           responder.py
                                   StubLLMResponder       TemplateResponder
                                   .explain(q, rule)       (fallback)
                                           │                       │
                                           └───────────┬───────────┘
                                                       │
                                               Response {answer,
                                                sources, degraded}
```

**Retrieve:** `Handbook.search()` scans all rules and returns the first whose title words appear in the user message, falling back to the first rule when no keyword matches.

**Augment:** The retrieved `Rule` object (id, title, full text) is passed alongside the original question to the responder, grounding the answer in real data.

**Generate:** `StubLLMResponder.explain()` formats the rule as a natural-language answer. If the provider raises `ProviderError`, `service.py` catches it and delegates to `TemplateResponder` as a degraded fallback, ensuring the user always receives an answer.

## 9. Design Principles

- **Separation of concerns:** Each module has a focused responsibility.
- **Maintainability:** Individual components can be modified with less impact on unrelated modules.
- **Testability:** Utility functions, routing logic, and service behavior can be tested separately.
- **Extensibility:** Additional intents, data sources, and response providers can be introduced as the project evolves.
- **Error resilience:** Specific exceptions and fallback responses help the application handle expected failures consistently.

## 10. UI & API System Boundary (Lab 07 — `v0.7-mvp`)

### System Overview Diagram

```text
[User / Browser (:8501)]
           │
           ▼
┌──────────────────────────────────────────┐
│   Streamlit Frontend (ui/app.py)         │  Manages st.session_state, validates input,
│   + ui/logic.py                          │  formats sources, shows status notes & 👍/👎
└────────────────────┬─────────────────────┘
                     │  HTTP / JSON via ui/api_client.py (httpx)
                     ▼  (POST /v1/chat, POST /v1/feedback, GET /health)
┌──────────────────────────────────────────┐
│   FastAPI Backend (:8000)                │  schemas.py (escalate: bool), admin auth,
│   (src/assistant_api/)                   │  hashes session_id with SESSION_SALT
└──────────┬───────────────────────┬───────┘
           │                       │
           ▼                       ▼
     [SQLite DB]          [assistant_core] ──► Data (offices.csv, handbook.json), RAG, LLM
```

### Decoupling Boundary & Dependency Rules

- **Strict HTTP/JSON Contract:** The `ui/` package operates purely as an HTTP client (`ui/api_client.py` using `httpx`) communicating with the FastAPI service over `ASSISTANT_API_URL` (`POST /v1/chat`, `POST /v1/feedback`, `GET /health`).
- **Zero Direct Imports:** Modules inside `ui/` **must never import** from `assistant_core` or `assistant_api`. Keeping frontend and backend decoupled allows each layer to be tested, scaled, or replaced independently.

### Lab 07 Runtime & Feedback Flows

1. **Graceful Connection Handling:** If the backend is unreachable or `ASSISTANT_API_URL` points to an inactive port, `ui/api_client.py` catches transport/HTTP errors and renders a user-friendly alert without crashing the Streamlit session.
2. **Escalation & Degraded States (`ui/logic.py`):** When a query falls outside official handbook/office records (`escalate: true`), the UI displays a referral note directing the student to the *Training Office (room I.101)*. When the LLM provider falls back to template generation (`degraded: true`), the UI notifies the user accordingly.
3. **Turn-Level User Feedback (`POST /v1/feedback`):** Each assistant response exposes 👍 (`+1`) and 👎 (`-1`) controls bound to its `request_id`, persisting feedback ratings in SQLite for quality evaluation.
