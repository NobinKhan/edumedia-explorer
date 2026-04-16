# API contracts (`/api/v1`)

Base URL prefix: **`/api/v1`**. JSON request/response bodies unless noted.

## Endpoints (target)

| Method | Path | Summary |
|--------|------|---------|
| GET | `/healthz` | Liveness (outside v1) |
| GET | `/api/v1/meta` | Build/name meta |
| GET/POST | `/api/v1/categories` | List / create categories |
| GET/PATCH/DELETE | `/api/v1/categories/{id}` | Category by id |
| GET/POST | `/api/v1/sub-categories` | List (filter `category_id`) / create |
| GET/PATCH/DELETE | `/api/v1/sub-categories/{id}` | Sub-category by id |
| GET/POST | `/api/v1/sub-sub-categories` | List (filter `sub_category_id`) / create |
| GET/PATCH/DELETE | `/api/v1/sub-sub-categories/{id}` | Sub-sub-category by id |
| GET/POST | `/api/v1/subject-pages` | List (filters) / create |
| GET/PATCH/DELETE | `/api/v1/subject-pages/{id}` | Page CRUD |
| POST | `/api/v1/subject-pages/{id}/publish` | Publish + render |
| POST | `/api/v1/subject-pages/{id}/preview` | Preview render |
| GET | `/api/v1/subject-pages/{id}/rendered` | Stored rendered HTML |
| GET/POST | `/api/v1/subject-pages/{page_id}/annotations` | List / create |
| GET/PATCH/DELETE | `/api/v1/annotations/{id}` | Annotation by id |
| GET/POST | `/api/v1/media-assets` | List / create JSON (`MediaAssetCreate`, e.g. `/static/...` paths) |
| POST | `/api/v1/media-assets/upload` | Multipart upload (form: `asset_type`, `title`, optional `alt_text`, `file`) |
| GET/DELETE | `/api/v1/media-assets/{id}` | Media by id |

## Validation rules (summary)

- **Slugs:** URL-safe; uniqueness per entity rules (see service layer).
- **Hierarchy:** Subject page foreign keys must reference a consistent chain (category ⊃ sub ⊃ sub-sub).
- **Annotations:** `annotation_type` ∈ {`text`,`image`,`audio`,`video`,`youtube`,`link_note`}; offsets within plain-text length of `raw_content`; type-specific fields (media id, YouTube URL) required when applicable.
- **YouTube:** `youtube_url` host allowlist-style check (youtube.com / youtu.be).

## Open questions

- Whether `GET .../rendered` should 404 for empty `rendered_content` or return sanitized `raw_content` fallback (current: prefer stored rendered after publish).
