You are the implementation agent for a backend-focused hiring task project.

Your job is to fully build the project described below with minimal assumptions, strong structure, clear progress tracking, and handoff safety so another agent can continue later without chat history.

# Project identity

Project name: EduMedia Author

One-line definition:
EduMedia Author is a FastAPI-based subject details page authoring system where an admin/editor can create hierarchical content pages, format text like a word processor, and attach interactive text, image, audio, video, and YouTube explanations to selected text.

# Core interpretation of the employer's task

This is NOT just a static interactive article page.

This IS a dynamic details-page authoring and rendering system with:
- category
- sub-category
- sub-sub-category
- subject details page
- word-processor-like formatting
- selectable text annotations
- multimedia attachment to selected text
- interactive rendered output

The employer explicitly described:
- a category / sub-category / sub-sub-category hierarchy
- a details page under a subject/group/category
- formatting actions similar to Microsoft Word
- text highlight
- bold
- italic
- underline
- text explanation
- image explanation
- audio explanation
- video explanation
- YouTube explanation
- link-like explanation elements
- dynamic implementation, not static hardcoding

Build according to that understanding.

# Technology constraints

Use these versions unless a verified compatibility issue blocks them:
- Python 3.14.4
- FastAPI 0.135.3
- uv 0.11.5
- just 1.49.0
- uvicorn 0.44.0
- pytest 9.0.3
- ruff 0.15.10

If any version cannot be used:
1. record the failed version and reason in tracker/decisions.md
2. record the failed command and error summary in tracker/session-log.md
3. choose the nearest lower compatible version
4. document the final chosen version in README.md

# Required stack

Must use:
- FastAPI
- uv
- just

Recommended:
- Jinja2 templates
- vanilla JavaScript
- SQLite
- SQLAlchemy

Do not introduce unnecessary complexity.

# High-level product goal

Build a mini CMS/editor + renderer where an editor can:
1. create a category hierarchy
2. create a subject details page
3. write content
4. format text with:
   - bold
   - italic
   - underline
   - highlight
5. select part of the text and attach:
   - text note
   - image
   - audio
   - local video
   - YouTube video
   - link-style explanation
6. preview the final rendered page
7. publish or view the public details page
8. let end users click annotations to open modal-based explanations/media

# In scope

- category CRUD
- sub-category CRUD
- sub-sub-category CRUD
- subject page CRUD
- annotation CRUD
- media asset support
- rich text formatting support
- interactive annotation rendering
- public page rendering
- preview flow
- backend APIs
- tests
- documentation
- deployment
- tracker/handoff system

# Out of scope unless time remains

- authentication
- cloud media storage
- advanced permissions
- collaborative editing
- revision history
- production-grade admin authentication
- large WYSIWYG dependency chains unless clearly necessary

# Non-negotiable implementation rules

1. This project must be dynamic, not hardcoded-only.
2. Backend APIs must be implemented to show backend engineering skill.
3. Do not build only a static UI mock.
4. Do not skip tracker updates.
5. Do not end a session without explicit handoff info.
6. Do not add a database-less hacky design unless absolutely necessary.
7. Prefer SQLite + SQLAlchemy to better demonstrate backend ability.
8. Keep architecture clean and understandable.
9. Keep routes thin; use services.
10. Avoid overengineering.

# Recommended architecture

Use layered architecture:

- routes/api
- routes/web
- schemas
- models
- repositories
- services
- templates
- static
- tests
- tracker

# Core data model

Implement these main entities.

## Category
Fields:
- id
- name
- slug
- description
- created_at
- updated_at

## SubCategory
Fields:
- id
- category_id
- name
- slug
- description
- created_at
- updated_at

## SubSubCategory
Fields:
- id
- sub_category_id
- name
- slug
- description
- created_at
- updated_at

## SubjectPage
Fields:
- id
- category_id
- sub_category_id
- sub_sub_category_id
- title
- slug
- summary
- raw_content
- rendered_content
- status
- created_at
- updated_at

## Annotation
Fields:
- id
- subject_page_id
- annotation_type
- trigger_text
- start_offset
- end_offset
- display_mode
- title
- body_text
- media_asset_id nullable
- youtube_url nullable
- link_label nullable
- created_at
- updated_at

## MediaAsset
Fields:
- id
- asset_type
- title
- file_path
- mime_type
- alt_text nullable
- thumbnail_path nullable
- created_at
- updated_at

# Allowed annotation types

Use only:
- text
- image
- audio
- video
- youtube
- link_note

# Required backend API design

Use prefix:
- /api/v1

Implement at least the following APIs.

## Categories API
- GET /api/v1/categories
- POST /api/v1/categories
- GET /api/v1/categories/{category_id}
- PATCH /api/v1/categories/{category_id}
- DELETE /api/v1/categories/{category_id}

## Sub-categories API
- GET /api/v1/sub-categories
- POST /api/v1/sub-categories
- GET /api/v1/sub-categories/{sub_category_id}
- PATCH /api/v1/sub-categories/{sub_category_id}
- DELETE /api/v1/sub-categories/{sub_category_id}

Support filtering by category_id.

## Sub-sub-categories API
- GET /api/v1/sub-sub-categories
- POST /api/v1/sub-sub-categories
- GET /api/v1/sub-sub-categories/{id}
- PATCH /api/v1/sub-sub-categories/{id}
- DELETE /api/v1/sub-sub-categories/{id}

Support filtering by sub_category_id.

## Subject pages API
- GET /api/v1/subject-pages
- POST /api/v1/subject-pages
- GET /api/v1/subject-pages/{page_id}
- PATCH /api/v1/subject-pages/{page_id}
- DELETE /api/v1/subject-pages/{page_id}
- POST /api/v1/subject-pages/{page_id}/publish
- POST /api/v1/subject-pages/{page_id}/preview
- GET /api/v1/subject-pages/{page_id}/rendered

Support filters:
- category_id
- sub_category_id
- sub_sub_category_id
- status
- search

## Annotations API
- GET /api/v1/subject-pages/{page_id}/annotations
- POST /api/v1/subject-pages/{page_id}/annotations
- GET /api/v1/annotations/{annotation_id}
- PATCH /api/v1/annotations/{annotation_id}
- DELETE /api/v1/annotations/{annotation_id}

## Media assets API
- GET /api/v1/media-assets
- POST /api/v1/media-assets
- GET /api/v1/media-assets/{asset_id}
- DELETE /api/v1/media-assets/{asset_id}

If upload handling is too time-consuming, support seeded local media assets and document the limitation.

## Health/meta API
- GET /healthz
- GET /api/v1/meta

# Required web routes

Implement at least:
- GET /
- GET /editor
- GET /editor/pages/new
- GET /editor/pages/{page_id}
- GET /pages/{slug}

# Required editor behavior

Build an editor interface where a user can:
- choose category
- choose sub-category
- choose sub-sub-category
- enter subject page title
- enter summary
- edit main content
- select text
- apply:
  - bold
  - italic
  - underline
  - highlight
- attach annotation/media to selected text
- preview rendered result
- save draft
- publish page

# Required rendering behavior

The public details page must:
- display formatted content
- preserve bold/italic/underline/highlight
- show annotated terms as interactive
- open related content in a modal
- support:
  - text notes
  - images
  - audio
  - local video
  - YouTube embeds

# UI strategy

Keep frontend practical and light.

Preferred approach:
- server-rendered HTML with Jinja2
- vanilla JS for:
  - formatting toolbar actions
  - selection handling
  - annotation creation flow
  - preview update
  - modal open/close
  - accordion or inline explanation support if used

Do not add a heavyweight frontend framework unless absolutely necessary and documented.

# Accessibility requirements

Implement:
- semantic HTML
- real button elements
- visible focus states
- modal close button
- Escape closes modal
- overlay click closes modal
- focus moves into modal
- focus returns to trigger after close
- alt text on images
- aria-modal and dialog roles where appropriate

# Backend quality requirements

To look professional as a backend developer, implement:

1. Pydantic request/response schemas
2. service layer
3. consistent error responses
4. validation for:
   - slug uniqueness
   - hierarchy integrity
   - annotation offsets
   - valid annotation/media type match
   - YouTube URL sanity
5. clean separation between web routes and API routes
6. reasonable tests

Optional but good:
- repository layer
- seed script
- render service that turns raw content + annotations into safe interactive HTML

# Storage recommendation

Preferred:
- SQLite + SQLAlchemy

If using SQLite:
- keep setup simple
- seed sample data
- no need for advanced migration tooling unless time allows

# Required project structure

Use a structure close to:

.
├── PROJECT_SPEC.md
├── README.md
├── justfile
├── pyproject.toml
├── uv.lock
├── .env.example
├── app
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── dependencies.py
│   ├── models
│   │   ├── category.py
│   │   ├── sub_category.py
│   │   ├── sub_sub_category.py
│   │   ├── subject_page.py
│   │   ├── annotation.py
│   │   └── media_asset.py
│   ├── schemas
│   │   ├── category.py
│   │   ├── subject_page.py
│   │   ├── annotation.py
│   │   └── media_asset.py
│   ├── repositories
│   │   ├── category_repository.py
│   │   ├── page_repository.py
│   │   ├── annotation_repository.py
│   │   └── media_repository.py
│   ├── services
│   │   ├── category_service.py
│   │   ├── page_service.py
│   │   ├── annotation_service.py
│   │   ├── media_service.py
│   │   └── render_service.py
│   ├── api
│   │   └── v1
│   │       ├── categories.py
│   │       ├── sub_categories.py
│   │       ├── sub_sub_categories.py
│   │       ├── subject_pages.py
│   │       ├── annotations.py
│   │       └── media_assets.py
│   ├── web
│   │   ├── editor.py
│   │   └── pages.py
│   ├── templates
│   │   ├── base.html
│   │   ├── editor.html
│   │   ├── page_view.html
│   │   └── partials
│   └── static
│       ├── css
│       ├── js
│       └── media
├── tests
│   ├── test_health.py
│   ├── test_categories_api.py
│   ├── test_subject_pages_api.py
│   ├── test_annotations_api.py
│   └── test_render_api.py
└── tracker

# justfile requirements

Implement at least:
- just install
- just dev
- just run
- just test
- just lint
- just format
- just check
- just clean

Expected meanings:
- install dependencies
- run dev server
- run production-style local server
- run tests
- run lint
- format code
- run all checks
- clean caches

# Tracker system requirements

Create tracker/ and keep it updated continuously.

Required files:
- tracker/project-brief.md
- tracker/backlog.md
- tracker/current-state.md
- tracker/decisions.md
- tracker/session-log.md
- tracker/qa-checklist.md
- tracker/handoff.md
- tracker/api-contracts.md

## tracker/project-brief.md
Must contain:
- goal
- scope
- non-goals
- locked stack
- acceptance criteria

## tracker/backlog.md
Must contain:
- task ID
- task title
- status
- dependencies
- blocker
- owner
- timestamp

Only allowed statuses:
- TODO
- IN_PROGRESS
- BLOCKED
- DONE

## tracker/current-state.md
Must always contain:
- branch
- completed tasks
- current task
- blockers
- test status
- deployment status
- repo cleanliness status
- exact next command
- exact next file to edit

## tracker/decisions.md
For each meaningful decision:
- timestamp
- decision
- reason
- alternatives considered
- consequences

## tracker/session-log.md
Append-only.
For each session:
- start/end time
- actor
- commands run
- files changed
- results
- blockers
- next recommended action

## tracker/qa-checklist.md
Must include:
- automated checks
- manual UI checks
- API checks
- deployment checks

## tracker/handoff.md
Must include:
- what is done
- what remains
- risks
- what not to casually change
- exact resume command
- exact resume file

## tracker/api-contracts.md
Must include:
- endpoint list
- request schema summary
- response schema summary
- validation rules
- open questions

# Mandatory tracker protocol

Before starting a major task:
1. read all tracker files
2. update tracker/current-state.md
3. mark backlog item as IN_PROGRESS
4. append a session start entry to tracker/session-log.md

After finishing a major task:
1. mark task status
2. update current-state
3. update backlog
4. update decisions if needed
5. append results to session-log

Before ending a session:
- leave one explicit next action
- leave one exact next command
- leave one exact next file path

This is mandatory.

# Initial backlog

Initialize with these tasks:

- T001 Initialize repository and toolchain
- T002 Create tracker system and project files
- T003 Configure database and base models
- T004 Create FastAPI app skeleton
- T005 Create justfile and developer commands
- T006 Implement Category CRUD API
- T007 Implement Sub-category CRUD API
- T008 Implement Sub-sub-category CRUD API
- T009 Implement Subject Page CRUD API
- T010 Implement Media Asset model and API
- T011 Implement Annotation model and API
- T012 Implement render service for interactive output
- T013 Implement preview endpoint
- T014 Build editor dashboard page
- T015 Build details page editor UI
- T016 Build formatting toolbar
- T017 Build annotation creation flow
- T018 Build rendered public details page
- T019 Build modal renderer for interactive media
- T020 Add validation and error handling
- T021 Add automated tests
- T022 Add sample seed data
- T023 Complete QA checklist
- T024 Write README
- T025 Prepare deployment config
- T026 Deploy app
- T027 Final polish and submission prep

# Required implementation order

Follow this order unless blocked:

Phase 1:
- T001
- T002
- T003
- T004
- T005

Phase 2:
- T006
- T007
- T008
- T009

Phase 3:
- T010
- T011
- T012
- T013

Phase 4:
- T014
- T015
- T016
- T017
- T018
- T019

Phase 5:
- T020
- T021
- T022
- T023

Phase 6:
- T024
- T025
- T026
- T027

# Definition of done

The project is done only when all of the following are true:

1. category CRUD works
2. sub-category CRUD works
3. sub-sub-category CRUD works
4. subject page CRUD works
5. annotation CRUD works
6. media asset flow works
7. editor screen works
8. formatting actions work
9. text annotation works
10. image annotation works
11. audio annotation works
12. local video annotation works
13. YouTube annotation works
14. public rendered page works
15. just check passes
16. README is complete
17. tracker files are current
18. live deployment works

# Anti-failure rules

1. Do not reduce this to a static page.
2. Do not ignore hierarchy support.
3. Do not skip APIs.
4. Do not skip tracker updates.
5. Do not end a session without handoff info.
6. Do not invent extra scope that delays the MVP.
7. Do not introduce auth unless time clearly allows.
8. Do not leave broken media or UI controls.
9. Do not deploy before local checks pass.
10. Do not leave blockers undocumented.

# Final instruction

Execute this project as a professional backend-focused implementation.

Prioritize:
- correctness
- clarity
- backend structure
- dynamic behavior
- resumable workflow
- professional API design

At the end of every session, assume a different agent will continue next.
The tracker must be sufficient for immediate takeover without chat history.