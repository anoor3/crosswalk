# Local review workspace

Run from the repository root:

```sh
.venv/bin/uvicorn crosswalk_api.app:create_app --factory --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001/workspace/ and choose **Discovery → Load example source**.
Upload your own OpenAPI JSON and optional array of sanitized response objects,
select an endpoint, then inspect and decide mappings in Field review. Decisions
are submitted to the review API and can be exported as JSON.

This first slice uses the built-in Claim model and one integration per browser
session. Reloading clears the browser workspace; importing another endpoint
clears its current decisions from the view. Export before switching sources.
The exported file is a decision record, not executable adapter code.

No frontend build, CDN, font service, or model provider is needed. The Python
API serves the HTML, CSS, and JavaScript on the same origin. This is a local
preview, without customer authentication or project persistence.
