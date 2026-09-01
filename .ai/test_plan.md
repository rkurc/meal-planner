# Detailed Test Plan

Test strategy for the Meal Planner, aligned with `.ai/feature_summary.md` and `.ai/requirements.md`. **Status reconciled 2026-09-02.**

## 1. Introduction

This plan maps requirements to tests. It is not the test implementation (that lives under `meal_planner_app/tests/` and `frontend/e2e/`).

## 2. Scope

**Inventory (functions in tree, not a fresh Docker run in this docs session):**
- Backend: **83** pytest tests.
- E2E: **10** Playwright tests in `frontend/e2e/main.spec.js` (includes recipe search).
- Automatic Discovery: still unimplemented (TC-ARD-* future).
- Ingredient **master CRUD**: still unimplemented (TC-ING-001/003 future). Ingredient **list** exists but has no dedicated test.
- PDF from React: backend pytest covers persisted PDF; **no E2E** for the Download PDF button.
- Jinja form HTML tests are **gone** (removed with the templates). Legacy **GET redirect** tests exist in `test_api.py`.

### 2.1 In Scope

*   Recipe / meal-plan / shopping CRUD and generation (API + React).
*   Shopping persistence, standalone lists, PDF of persisted lists.
*   Meal-plan recipe counts (API/CRUD tests).
*   Suggestion endpoints (`/api/ingredients`, `/locations`, `/units`).
*   Recipe search (CRUD unit tests + `GET /api/recipes?q=&ingredient=` + React E2E).
*   Legacy HTML GET redirects into `/ui/`.

### 2.2 Out of Scope (or future)

*   Implementing tests (this document is the plan).
*   Third-party framework internals.
*   Discovery (TC-ARD-*) until the feature exists.
*   Master ingredient write tests until a master exists.
*   NFR load / AI accuracy.
*   E2E for PDF, ingredients page, standalone shopping delete (gaps).
*   Jinja HTML / form POST tests (UI decommissioned).

## 3. Test Strategy

*   **Unit / integration:** `pytest` against in-memory CRUD and Flask `test_client`.
*   **API:** same pytest modules (`test_api.py`, `test_shopping_list_api.py`).
*   **E2E:** Playwright against `/ui/` (CI: gunicorn in the bake `ci` image, `TESTING=true` for `/api/test/seed-db`).
*   **Frontend unit tests:** not present (no Jest/RTL).
*   **Manual:** exploratory UX.

All automated runs should go through Docker (AGENTS.md).

## 4. Test Cases

### 4.1 Automatic Recipe Discovery *(NOT IMPLEMENTED — ALL TESTS FUTURE)*

#### 4.1.1 Search-Based Discovery
| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type | Status |
|---|---|---|---|---|---|---|
| **TC-ARD-S-001** | FR-1.1.1.1, FR-1.1.1.2 | Verify user can search for recipes by dish type. | 1. Navigate to "Discover Recipes".<br>2. Enter "chicken pasta".<br>3. Submit. | List of related recipe links. | E2E | Future |
| **TC-ARD-S-002** | FR-1.1.1.3, FR-1.1.1.4 | Verify user can select a search result for extraction. | 1. Search.<br>2. Click Import/Extract. | Starts URL extraction for that link. | E2E | Future |

#### 4.1.2 URL-Based Extraction
| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type | Status |
|---|---|---|---|---|---|---|
| **TC-ARD-U-001** | FR-1.1.2.1, FR-1.1.2.2 | Submit a URL for extraction. | 1. Import from URL.<br>2. Valid recipe URL.<br>3. Extract. | Progress indicator; extraction starts. | E2E | Future |
| **TC-ARD-U-002** | FR-1.1.2.3, FR-1.1.2.4 | Extracted data presented for confirmation. | Submit a valid URL. | Add Recipe form pre-filled. | Integration | Future |
| **TC-ARD-U-003** | NFR-2.3.2 | Non-recipe URL handled. | Submit google.com. | User-friendly error. | E2E | Future |

### 4.2 Recipe Management *(IMPLEMENTED)*

Covered by pytest + Playwright (create/edit/delete/view/list). Prep-time / shelf-life fields do not exist — no tests, and TC-REC-001 does not actually assert those metadata fields.

| Test ID | Requirement(s) | Test Description | Test Type | Status |
|---|---|---|---|---|
| **TC-REC-001** | FR-1.2.1, FR-1.2.2 | Create a recipe (name, instructions, ingredients; not times/shelf life). | E2E | Implemented (passes; times/shelf life not in product) |
| **TC-REC-002** | FR-1.2.3, FR-1.2.4 | List + detail. | E2E | Implemented (passes) |
| **TC-REC-003** | FR-1.2.5 | Edit. | E2E | Implemented (passes) |
| **TC-REC-004** | FR-1.2.6 | Delete. | E2E | Implemented (passes) |
| **TC-REC-005** | FR-1.2.7 | `GET /api/recipes` (and `?q=` / `?ingredient=`). | API | Implemented (passes) |
| **TC-REC-006** | FR-1.6.3 | Recipes on React `/ui/`. | E2E | Implemented (passes) |
| **TC-REC-007** | FR-1.3.4 | Flexible ingredient units. | E2E | Implemented (passes) |
| **TC-REC-008** | UX | Default unit auto-fill on name; do not overwrite pre-filled unit. | E2E | Implemented (`should auto-populate default unit...`) |

### 4.3 Ingredient Management *(PARTIAL)*

Master CRUD tests remain future. List/summary have **no** dedicated pytest or E2E.

| Test ID | Requirement(s) | Test Description | Test Type | Status |
|---|---|---|---|---|
| **TC-ING-001** | FR-1.3.1 | Create a master ingredient. | E2E | Future (feature missing) |
| **TC-ING-002** | FR-1.3.2 | Ingredient list page shows aggregated names. | E2E | **Gap** — UI exists at `/ui/ingredients`, no test |
| **TC-ING-003** | FR-1.3.3 | Edit or delete a master ingredient. | E2E | Future (feature missing) |
| **TC-ING-004** | — | `GET /api/ingredients` unique names. | API | Implemented (passes) |
| **TC-ING-005** | — | `GET /api/ingredients/summary` and `/info`. | API | **Gap** — endpoints exist, no tests |
| **TC-ING-006** | — | `GET /api/locations`, `GET /api/units`. | API | Implemented (passes) |

### 4.4 Meal Plan Management *(IMPLEMENTED)*

| Test ID | Requirement(s) | Test Description | Test Type | Status |
|---|---|---|---|---|
| **TC-MP-001** | FR-1.4.1, FR-1.4.2 | Create plan and add recipes. | E2E / API | Implemented (API + generate-from-plan E2E; no dedicated create-plan E2E) |
| **TC-MP-002** | FR-1.4.4 | Edit or delete a plan. | API | Implemented (pytest); no E2E |
| **TC-MP-003** | — | Recipe counts on create/update; shopping qty × count. | API / CRUD | Implemented (passes) |

### 4.5 Shopping List Generation *(IMPLEMENTED)*

| Test ID | Requirement(s) | Test Description | Test Type | Status |
|---|---|---|---|---|
| **TC-SL-001** | FR-1.5.1, FR-1.5.3 | Generate from a meal plan in React. | E2E | Implemented (passes; button "Generate from Meal Plan") |
| **TC-SL-002** | FR-1.5.2 | Consolidation of compatible units. | Integration | Implemented (unit tests). **Note:** no g↔kg conversion; same-unit only |
| **TC-SL-003** | FR-1.5.4 | Manually edit a persisted list. | E2E | Implemented (passes) |
| **TC-SL-004** | — | Standalone `POST /api/shopping-lists` `{name}` → empty list. | API | Implemented (passes) |
| **TC-SL-005** | — | Delete list from `/ui/shopping-lists`. | E2E | **Gap** (API delete tested) |
| **TC-SL-006** | FR-1.7.2 | PDF of persisted list; purchased excluded; `location_id` grouping. | API | Implemented (3 pytest). E2E **gap** |

### 4.6 Future/Desired Features

| Test ID | Requirement(s) | Test Description | Test Type | Status |
|---|---|---|---|---|
| **TC-FF-001** | FR-1.7.2 | PDF export from UI. | E2E | Partial (backend + React link; no Playwright) |
| **TC-FF-002** | FR-1.7.1 | Local recipe search in React. | E2E | **Implemented** (`should filter recipes by search query and ingredient`; API tests for `q` / `ingredient`) |

### 4.7 Legacy HTML redirects *(IMPLEMENTED)*

Former Jinja GET paths 302 into `/ui/`. Form HTML tests (`test_*_via_form`, `test_generate_shopping_list_route`) were deleted with the templates.

| Test ID | Requirement(s) | Test Description | Test Type | Status |
|---|---|---|---|---|
| **TC-UI-001** | FR-1.6.3 | `GET /` → 302 `/ui/` | API | Implemented (`test_root_redirects_to_ui`) |
| **TC-UI-002** | — | `GET /recipes` and `/recipes/<id>` → `/ui/recipes…` | API | Implemented |
| **TC-UI-003** | — | `GET /meal-plans` and `/meal-plans/<id>` → `/ui/meal-plans…` | API | Implemented |
| **TC-UI-004** | — | `GET /meal-plans/<id>/shopping-list` → `/ui/meal-plans/<id>` (not a shopping HTML page) | API | Implemented |

## 5. Non-Functional Testing

| Test ID | Requirement(s) | Test Description | Test Type | Status |
|---|---|---|---|---|
| **TC-NFR-001** | NFR-2.1.1, NFR-2.1.3 | Page load and API times. | Performance | Not measured |
| **TC-NFR-002** | NFR-2.1.2 | Discovery timing. | Performance | Future |
| **TC-NFR-003** | NFR-2.2.1, NFR-2.2.2 | Usability. | Manual | Applies to the React UI |
| **TC-NFR-004** | NFR-2.3.2 | Invalid input / 404s. | API | Covered in CRUD/API tests |
| **TC-NFR-005** | NFR-2.5.1 | Extraction accuracy. | Manual | Future |
