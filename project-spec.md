# Interactive Teaching Platform - Full Build Specification

## 1. Mission

Build a production-quality FastAPI project that reproduces the interactive teaching/article platform shown in the provided hiring-task video.

This specification is written so that an AI agent can execute the project with minimal or no reasoning, minimal assumptions, and safe handoff across multiple sessions or multiple agents.

The project must be completed with:
- FastAPI as the framework
- uv as the package manager and environment manager
- just as the command runner
- latest stable versions pinned below unless a verified compatibility issue occurs
- a persistent tracker system so work can resume in a later session or by a different agent

Do not assume unstated requirements.
When uncertain, choose the smallest correct implementation that matches the video demonstration.
Do not add speculative features unless they improve reliability, maintainability, accessibility, testing, or deployment.

---

## 2. Locked Toolchain

Use these versions unless installation or dependency resolution proves they are incompatible in practice:

- Python 3.14.4
- FastAPI 0.135.3
- uv 0.11.6
- just 1.49.0
- uvicorn 0.44.0
- pytest 9.0.3
- ruff 0.15.10

If any exact version cannot be used:
1. Record the failure in `tracker/decisions.md`
2. Record the error summary and failed command in `tracker/session-log.md`
3. Choose the nearest lower compatible version
4. Document exactly why the change was required
5. Update this spec or the README with the actual chosen version

---

## 3. Deliverables

The finished project must include all of the following:

1. Complete source code in a clean Git repository
2. Working local development setup
3. Automated formatting, linting, and testing commands
4. Live deployed application
5. README with setup, run, test, architecture, and deployment instructions
6. Tracker files that make the project resumable across sessions
7. Submission-ready summary text for the employer
8. A project that visually and functionally matches the task video closely

---

## 4. Product Summary

Build a web application called:

**Interactive Teaching Platform**

With subtitle:

**Click on highlighted terms to explore multimedia content**

The application is a two-column interactive learning/demo page.

### Left column
Must contain:
1. A section titled **Multimedia Content Examples**
2. Clickable controls/cards/buttons for:
   - Text
   - Image
   - Audio
   - MyVid
   - YouTube
3. A section titled **News Article with Interactive Elements**
4. An article body with highlighted clickable terms inside the text

### Right column
Must contain:
1. A section titled **Expandable Content**
2. Accordion sections:
   - Introduction
   - Detailed Explanation
   - Additional Resources

---

## 5. Required Feature Behavior

### 5.1 Text interaction
Clicking **Text** opens a modal dialog with text content.

### 5.2 Image interaction
Clicking **Image** opens a modal dialog with an image.

### 5.3 Audio interaction
Clicking **Audio** opens a modal dialog with an HTML audio player and controls.

### 5.4 Local video interaction
Clicking **MyVid** opens a modal dialog with a local/self-hosted video player and controls.

### 5.5 YouTube interaction
Clicking **YouTube** opens a modal dialog with an embedded YouTube video.

Fallback rule:
- If embedding is blocked or broken, open the YouTube URL in a new tab.
- Prefer embedded modal first.

### 5.6 Interactive article behavior
The article must contain highlighted clickable terms.
At minimum:
- one term opens text content
- one term opens image content
- one term opens audio content
- one term opens local video or YouTube
- terms must look visibly interactive

### 5.7 Accordion behavior
Each accordion item must expand and collapse.
At least one expanded panel must include normal text content plus at least one inline interactive item that can trigger a media modal.

---

## 6. Non-Negotiable UX Requirements

1. The page must be responsive
2. Desktop layout should be two columns
3. Mobile layout should stack vertically
4. Keyboard users must be able to tab through all controls
5. Modal must close with Escape
6. Modal must close via overlay click
7. Modal must close via close button
8. Focus must move into the modal when opened
9. Focus must return to the triggering control when the modal closes
10. The UI must look deliberate, clean, and professional
11. Do not use ugly default browser styling as the final design
12. Do not require a database
13. Do not require authentication
14. Keep JavaScript minimal and explicit
15. Prefer server-rendered HTML

---

## 7. Architecture Requirements

Use FastAPI with Jinja2 templates and static assets.

### Required stack
- FastAPI
- Jinja2 templates
- Static CSS
- Minimal vanilla JavaScript
- Local static media assets
- Optional `.env` configuration if needed
- No database

### Required routes
- `GET /` renders the homepage
- `GET /healthz` returns JSON health status
- `GET /api/content/{content_id}` returns content metadata in JSON
- Optional extra route only if strictly useful

### Content management approach
Create a central content registry that maps `content_id` to content metadata.

Do not scatter content definitions across templates and JavaScript.
Use one central source of truth.

### Preferred data flow
- Server renders the page shell and visible sections
- JavaScript opens modal and renders dynamic content
- Modal content may be:
  - preloaded in HTML, or
  - fetched from `/api/content/{content_id}`

Preferred implementation:
- render page structure server-side
- store content definitions centrally
- use lightweight API endpoint for modal content lookup

---

## 8. Content Model

Create a consistent content model with these fields:

- `id`
- `type` where allowed values are:
  - `text`
  - `image`
  - `audio`
  - `video`
  - `youtube`
- `title`
- `description`
- `body_text` optional
- `asset_url` optional
- `embed_url` optional
- `thumbnail_url` optional

Use this model consistently across:
- cards/buttons
- article terms
- accordion inline items
- API responses
- modal renderer

---

## 9. Required Sample Content

The project must include real working sample content so the demo is complete.

Create all of the following:
- 1 text content entry
- 1 image file
- 1 audio file
- 1 local video file
- 1 YouTube content entry
- 1 article with highlighted interactive terms
- 3 accordion sections

Rules:
- Do not leave broken media
- Do not reference files that are missing
- Use safe, distributable assets
- If copyrighted media is risky, use neutral self-created or public-safe demo assets

---

## 10. Design Requirements

### Visual style
Use a clean modern style appropriate for a hiring task:
- centered max-width container
- card-based sections
- soft shadows
- rounded corners
- clear spacing
- readable typography
- accessible contrast
- clear hover and focus states

### Multimedia controls
The multimedia example controls must be obvious clickable elements.
They can be:
- buttons
- cards
- pill buttons
- compact tiles

Do not use plain text links for these top-level controls unless styled strongly.

### Article styling
Interactive terms inside the article must look visibly interactive:
- underline and/or accent background
- pointer cursor
- strong hover state
- visible keyboard focus state

### Modal styling
The modal must include:
- title
- content body
- close button
- overlay
- spacing appropriate for media

Use one reusable modal shell capable of rendering:
- text
- image
- audio
- video
- YouTube iframe

---

## 11. Accessibility Requirements

The agent must explicitly implement the following:

1. Semantic HTML landmarks
2. Real `<button>` elements for actions
3. `aria-expanded` on accordion triggers
4. `aria-controls` on accordion triggers
5. `role="dialog"` on the modal
6. `aria-modal="true"` on the modal
7. Appropriate modal labels
8. Alt text on images
9. Visible focus styles
10. Escape key support
11. Initial focus placement inside the modal
12. Focus trap inside the modal while open
13. Focus restore to trigger after close

These are not optional.

---

## 12. Testing Requirements

Create automated tests for at least the following:

1. Homepage loads successfully
2. Health endpoint returns success JSON
3. Content API returns a valid payload for a valid content ID
4. Content API returns 404 for an invalid content ID

### Manual verification requirements
Perform and document manual checks for:
1. desktop layout
2. mobile layout
3. modal open/close behavior
4. article interactive terms
5. accordion expand/collapse behavior
6. audio playback
7. local video playback
8. YouTube rendering
9. keyboard accessibility basics

Record results in `tracker/qa-checklist.md`.

---

## 13. Deployment Requirements

Deploy to the simplest reliable platform suitable for FastAPI.

Preferred order:
1. Render
2. Railway
3. Fly.io

Use the fastest reliable option that produces a public URL.

Deployment output must include:
- live URL
- reproducible deployment config
- documented start command
- documented environment variables, if any
- confirmation that static assets load

---

## 14. Repository Structure

The project should end with a structure close to this:

```text
.
├── .env.example
├── .gitignore
├── README.md
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── routes
│   │   ├── __init__.py
│   │   └── web.py
│   ├── services
│   │   ├── __init__.py
│   │   └── content_registry.py
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   ├── js
│   │   │   └── app.js
│   │   └── media
│   │       ├── sample-image.jpg
│   │       ├── sample-audio.mp3
│   │       └── sample-video.mp4
│   └── templates
│       ├── base.html
│       ├── index.html
│       └── partials
│           ├── accordion.html
│           ├── article.html
│           ├── media_cards.html
│           └── modal.html
├── tests
│   ├── __init__.py
│   ├── test_content_api.py
│   ├── test_health.py
│   └── test_home.py
├── tracker
│   ├── backlog.md
│   ├── current-state.md
│   ├── decisions.md
│   ├── handoff.md
│   ├── project-brief.md
│   ├── qa-checklist.md
│   └── session-log.md
├── justfile
├── pyproject.toml
└── uv.lock
````

---

## 15. Root File Requirements

The repository must contain:

* `README.md`
* `pyproject.toml`
* `uv.lock`
* `justfile`
* `.gitignore`
* `.env.example`
* `PROJECT_SPEC.md`
* `tracker/`
* `app/`
* `tests/`

---

## 16. Required justfile Commands

Implement the following commands and semantics.

### Required commands

* `just install`
* `just dev`
* `just run`
* `just test`
* `just lint`
* `just format`
* `just check`
* `just clean`

### Required meanings

#### `just install`

Install and sync dependencies using uv.

#### `just dev`

Run the FastAPI development server with reload.

#### `just run`

Run a production-style local server.

#### `just test`

Run pytest.

#### `just lint`

Run ruff check.

#### `just format`

Run ruff format.

#### `just check`

Run all major checks in sequence:

* format check
* lint
* tests

#### `just clean`

Remove caches and temporary artifacts.

### Recommended optional commands

* `just tree`
* `just lock`

### Suggested justfile implementation

```just
set shell := ["bash", "-cu"]

install:
    uv sync

dev:
    uv run fastapi dev app/main.py

run:
    uv run fastapi run app/main.py

test:
    uv run pytest

lint:
    uv run ruff check .

format:
    uv run ruff format .

check:
    uv run ruff format --check .
    uv run ruff check .
    uv run pytest

clean:
    find . -type d -name "__pycache__" -prune -exec rm -rf {} +
    rm -rf .pytest_cache .ruff_cache .mypy_cache dist build
```

---

## 17. Dependency Requirements

Keep dependency count low.

### Production dependencies

* `fastapi[standard]`
* `jinja2`
* `pydantic-settings`
* `uvicorn`

### Development dependencies

* `pytest`
* `httpx`
* `ruff`

Only add extra dependencies if strictly necessary.
If extra dependencies are added:

* record them in `tracker/decisions.md`
* explain why they were necessary

---

## 18. Tracker System

Create a `tracker/` directory and keep it updated continuously throughout the project.

The tracker is the source of truth for project continuation.
Assume future sessions may have no chat history.
Assume a different agent may continue the work later.

### Required tracker files

#### `tracker/project-brief.md`

Must contain:

* exact project goal
* scope
* non-goals
* locked stack
* acceptance criteria

#### `tracker/backlog.md`

Must contain:

* task IDs
* task titles
* status values
* dependencies
* blocker column
* owner
* last updated timestamp

Use only these status values:

* `TODO`
* `IN_PROGRESS`
* `BLOCKED`
* `DONE`

#### `tracker/decisions.md`

For each meaningful technical decision, record:

* date and time
* decision made
* reason
* alternatives considered
* consequences

#### `tracker/session-log.md`

Append-only file containing:

* session timestamp start and end
* actor name or agent label
* commands run
* files changed
* outcomes
* blockers
* next recommended action

#### `tracker/current-state.md`

This is the most important file.

It must always contain:

* current branch
* completed task IDs
* current in-progress task
* blocker summary
* exact next command to run
* exact next file to inspect or edit
* deployment status
* test status
* repository cleanliness status

#### `tracker/qa-checklist.md`

Must contain automated and manual verification checklist entries.

#### `tracker/handoff.md`

Short handoff note including:

* what is done
* what remains
* what must not be changed casually
* highest-risk area
* exact resume command
* exact resume file

---

## 19. Tracker Update Protocol

The agent must follow this protocol exactly.

### Before starting any major task

1. Read all files in `tracker/`
2. Update `tracker/current-state.md`
3. Mark the selected backlog item as `IN_PROGRESS`
4. Append a session start entry to `tracker/session-log.md`

### After finishing any major task

1. Mark task status appropriately
2. Update `tracker/current-state.md`
3. Update `tracker/backlog.md`
4. Append architectural decisions if any were made
5. Append progress details to `tracker/session-log.md`

### Before ending any session

The agent must always leave:

* one explicit next action
* one exact next command
* one exact next file path to inspect or edit

This is mandatory.

---

## 20. Initial Backlog

Initialize `tracker/backlog.md` with the following task IDs and titles:

* T001 Initialize repository and toolchain
* T002 Create FastAPI app skeleton
* T003 Configure templates and static assets
* T004 Implement base layout and responsive page shell
* T005 Build multimedia example controls
* T006 Implement modal system
* T007 Implement article with interactive terms
* T008 Implement accordion sidebar
* T009 Add content registry and API endpoint
* T010 Add accessibility behavior and keyboard support
* T011 Add local media assets and wire content
* T012 Write automated tests
* T013 Create justfile commands
* T014 Write README
* T015 Prepare deployment config
* T016 Deploy app
* T017 Run QA checklist
* T018 Final polish and submission prep

---

## 21. Recommended Phase Order

Follow this order unless blocked.

### Phase 1 - foundation

* T001 Initialize repository and toolchain
* T002 Create FastAPI app skeleton
* T013 Create justfile
* T003 Configure templates and static assets

### Phase 2 - page shell

* T004 Implement base layout and responsive page shell
* T005 Build multimedia example controls
* T008 Implement accordion sidebar

### Phase 3 - content mechanics

* T009 Add content registry and API endpoint
* T006 Implement modal system
* T007 Implement article with interactive terms
* T011 Add local media assets and wire content

### Phase 4 - quality

* T010 Add accessibility behavior and keyboard support
* T012 Write automated tests
* T017 Run QA checklist

### Phase 5 - release

* T014 Write README
* T015 Prepare deployment config
* T016 Deploy app
* T018 Final polish and submission prep

---

## 22. Definition of Done

The project is done only when all of the following are true:

1. `just install` works on a clean machine
2. `just dev` starts the app locally
3. `just check` passes
4. Homepage reproduces the demo structure
5. All five media types work
6. Article interactive terms work
7. Accordion works
8. Health endpoint works
9. Content API works
10. README is complete
11. Tracker files are current
12. Live deployment is accessible
13. Final repo is clean and understandable

---

## 23. Coding Rules

1. Keep code simple and explicit
2. Use Python type hints
3. Prefer small functions
4. Avoid dead code
5. Avoid premature abstraction
6. Keep naming clear and boring
7. Do not leave placeholder TODO comments in final code unless also tracked in backlog
8. Do not commit secrets
9. Do not leave broken links or missing assets
10. Every interactive UI element must have a clear purpose
11. Prefer maintainability over cleverness

---

## 24. Template Strategy

Use:

* `base.html` for the main page shell
* `index.html` for page composition
* partials for repeatable sections

### Required partials

* `partials/media_cards.html`
* `partials/article.html`
* `partials/accordion.html`
* `partials/modal.html`

Do not place the entire application in one monolithic template.

---

## 25. JavaScript Strategy

Use minimal vanilla JavaScript only.

### JavaScript responsibilities

* open modal
* close modal
* render modal content
* trap focus in modal
* restore focus on close
* handle Escape key
* handle overlay click
* toggle accordion
* optionally fetch content JSON from `/api/content/{content_id}`

Do not add a frontend framework unless absolutely required and documented.

No build step is preferred.

---

## 26. CSS Strategy

Use one main stylesheet:

* `app/static/css/styles.css`

Organize sections clearly:

1. reset/base
2. typography
3. layout
4. cards/buttons
5. article
6. accordion
7. modal
8. media containers
9. utility states
10. responsive rules
11. focus states

---

## 27. Content Details

### Required example content IDs

Use at least the following pattern or equivalent:

* `interactive-learning` -> text
* `visual-example` -> image
* `spoken-note` -> audio
* `demo-video` -> local video
* `external-reference` -> youtube

These IDs should be used consistently across:

* media cards
* article terms
* accordion inline items
* API responses

### Article requirement

The article text may be in English or Bengali.
It must include at least four highlighted interactive terms linked to content IDs.

### Accordion requirement

Accordion panels should reinforce the educational theme and at least one panel must contain an inline interactive media trigger.

---

## 28. Anti-Failure Rules

The agent must obey all of the following:

1. Do not skip tracker updates
2. Do not deploy before local checks pass
3. Do not add a database
4. Do not add authentication
5. Do not over-engineer the backend
6. Do not leave media assets broken
7. Do not rely only on remote assets except YouTube
8. Do not ignore mobile layout
9. Do not ignore keyboard behavior
10. Do not end a session without updating `tracker/current-state.md`
11. Do not invent hidden requirements
12. Do not leave silent blockers undocumented

---

## 29. Exact Startup Procedure for Any Agent

Any agent beginning work must do this in order:

1. Read `PROJECT_SPEC.md`
2. Read all files in `tracker/`
3. Open `tracker/current-state.md`
4. Confirm current task
5. Update `tracker/backlog.md` to mark the selected task `IN_PROGRESS`
6. Append a new entry in `tracker/session-log.md`
7. Perform implementation
8. Run relevant checks
9. Update tracker files
10. End with one exact next command and one exact next file path

---

## 30. Exact Initial Setup Procedure

The first working session must do this:

1. Create repository root structure
2. Create `PROJECT_SPEC.md`
3. Create `tracker/` folder and all required tracker files
4. Initialize project with uv
5. Add FastAPI and required dependencies
6. Add justfile
7. Add app skeleton
8. Add tests skeleton
9. Run the initial app locally
10. Update tracker files

The first session must prioritize structure and tracking before UI work.

---

## 31. Suggested Tracker File Templates

### `tracker/project-brief.md`

```md
# Project Brief

## Goal
Build a FastAPI-based interactive teaching platform demo that matches the hiring-task video.

## In Scope
- responsive landing page
- multimedia example controls
- modal system for text/image/audio/video/youtube
- interactive article terms
- accordion sidebar
- tests
- deployment
- documentation
- tracker system

## Out of Scope
- database
- authentication
- admin panel
- CMS
- user uploads

## Locked Stack
- Python 3.14.4
- FastAPI 0.135.3
- uv 0.11.6
- just 1.49.0
- uvicorn 0.44.0
- pytest 9.0.3
- ruff 0.15.10

## Acceptance Criteria
- all required interactions work
- `just check` passes
- deployed URL is live
- tracker files are current
```

### `tracker/backlog.md`

```md
# Backlog

Last updated: YYYY-MM-DD HH:MM UTC

| ID   | Task | Status | Depends On | Blocker | Owner |
|------|------|--------|------------|---------|-------|
| T001 | Initialize repository and toolchain | TODO | - | - | agent |
| T002 | Create FastAPI app skeleton | TODO | T001 | - | agent |
| T003 | Configure templates and static assets | TODO | T002 | - | agent |
| T004 | Implement base layout and responsive page shell | TODO | T003 | - | agent |
| T005 | Build multimedia example controls | TODO | T004 | - | agent |
| T006 | Implement modal system | TODO | T005,T009 | - | agent |
| T007 | Implement article with interactive terms | TODO | T006,T009 | - | agent |
| T008 | Implement accordion sidebar | TODO | T004 | - | agent |
| T009 | Add content registry and API endpoint | TODO | T002 | - | agent |
| T010 | Add accessibility behavior and keyboard support | TODO | T006,T008 | - | agent |
| T011 | Add local media assets and wire content | TODO | T006,T009 | - | agent |
| T012 | Write automated tests | TODO | T002,T009 | - | agent |
| T013 | Create justfile commands | TODO | T001 | - | agent |
| T014 | Write README | TODO | T001-T013 | - | agent |
| T015 | Prepare deployment config | TODO | T014 | - | agent |
| T016 | Deploy app | TODO | T015 | - | agent |
| T017 | Run QA checklist | TODO | T016 | - | agent |
| T018 | Final polish and submission prep | TODO | T017 | - | agent |
```

### `tracker/current-state.md`

```md
# Current State

Last updated: YYYY-MM-DD HH:MM UTC

## Branch
main

## Completed Tasks
- none yet

## Current Task
- T001 Initialize repository and toolchain

## Blockers
- none

## Test Status
- not run

## Deployment Status
- not started

## Repo Status
- initial

## Exact Next Command
uv init

## Exact Next File To Edit
tracker/backlog.md

## Notes
- Start by creating tracker files before app code.
```

### `tracker/decisions.md`

```md
# Decisions

## YYYY-MM-DD HH:MM UTC
Decision:
Reason:
Alternatives considered:
Consequences:
```

### `tracker/session-log.md`

```md
# Session Log

## Session YYYY-MM-DD HH:MM UTC
Actor:
Start state:
Commands run:
Files changed:
Outcome:
Blockers:
Next action:
```

### `tracker/qa-checklist.md`

```md
# QA Checklist

## Automated
- [ ] `just lint`
- [ ] `just test`
- [ ] `just check`

## Manual UI
- [ ] Home page loads
- [ ] Responsive desktop layout
- [ ] Responsive mobile layout
- [ ] Text modal works
- [ ] Image modal works
- [ ] Audio modal works
- [ ] Local video modal works
- [ ] YouTube modal works
- [ ] Article highlighted terms work
- [ ] Accordion expands/collapses
- [ ] Escape closes modal
- [ ] Overlay click closes modal
- [ ] Focus returns after modal close

## Deployment
- [ ] Live URL opens
- [ ] Static assets load
- [ ] Health endpoint works
```

### `tracker/handoff.md`

```md
# Handoff

## Done
-

## In Progress
-

## Remaining
-

## Risks
-

## Avoid Changing
-

## Resume Here
Command:
File:
```

---

## 32. Suggested Implementation Checklist

The agent may use this as its working checklist.

### Foundation

* [ ] Create repo structure
* [ ] Create tracker files
* [ ] Initialize uv project
* [ ] Add dependencies
* [ ] Create justfile
* [ ] Create FastAPI app shell
* [ ] Add Jinja2 template setup
* [ ] Add static file mounting

### Page

* [ ] Create base template
* [ ] Create homepage layout
* [ ] Create multimedia controls section
* [ ] Create article section
* [ ] Create accordion section
* [ ] Create modal shell

### Data and interactions

* [ ] Build content registry
* [ ] Build content API
* [ ] Wire controls to modal
* [ ] Wire article terms to modal
* [ ] Wire accordion inline terms to modal
* [ ] Add image/audio/video/youtube render paths

### Accessibility and quality

* [ ] Add keyboard support
* [ ] Add focus management
* [ ] Add Escape close
* [ ] Add overlay close
* [ ] Add alt text and ARIA
* [ ] Write tests
* [ ] Run checks
* [ ] Update tracker

### Release

* [ ] Write README
* [ ] Deploy app
* [ ] Verify live app
* [ ] Complete QA checklist
* [ ] Prepare submission notes

---

## 33. Final Quality Bar

This is a hiring task. The final output must feel deliberate.

That means:

* no broken layout
* no console errors
* no placeholder unfinished sections
* no missing media
* no dirty repo
* no confusing file names
* no undocumented hacks
* no ignored accessibility basics
* no session ending without tracker updates

---

## 34. Handoff Rule

At the end of every session, assume a different agent will continue next.

Therefore:

* tracker files must be current
* backlog must reflect reality
* decisions must be documented
* current-state must contain the exact next command and next file
* handoff must explain what is done and what remains

The tracker is more important than chat memory.

---

## 35. Final Instruction to Any Agent

Execute the project strictly according to this specification.

When uncertain:

1. prefer minimal correct implementation
2. document the choice
3. keep the tracker current
4. do not assume hidden requirements
5. leave the project resumable for the next session
