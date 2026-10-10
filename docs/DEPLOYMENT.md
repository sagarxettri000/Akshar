# Running and deploying Akshar

**Vercel only.** One front end, one deployment: the app in `landing/` is served by a single
Vercel project as static files plus one serverless function (`landing/api/gemma.mjs`). There
is nothing to build and no runtime dependency to install. **Streamlit is not used in this
project** — there is no Python app to run, no Streamlit deployment to update, and no reason
to install Python for anything here.

The binding rules are in [`AGENTS.md` §10](../AGENTS.md):

- Never deploy, redeploy, publish, unpublish, or change hosting unless a human explicitly
  asks for it in that task. "Commit and push" is not permission to deploy.
- Never add, switch, or duplicate a hosting platform or project — no second Vercel project,
  no Streamlit Cloud app (or app of any other kind), no Render/Railway/Netlify/Fly/Cloudflare/
  GitHub Pages site.
- Never push to `main` to store or share work: it is the production branch, so a push
  republishes the site students use. Work on a task branch and let a maintainer merge.
- Never create a temporary public deployment to test something. Run it locally.

## 0. Prerequisites

- The repository on GitHub: <https://github.com/sagarxettri000/Akshar>
- Node 18 or newer to run the app and the tests (developed on Node 24)
- A **fresh** Google AI Studio API key (rotate any key that was ever shared publicly)

## 1. Run it locally

```bash
node landing/scripts/dev.mjs                 # http://127.0.0.1:3000 — reading works, AI needs a key
node landing/scripts/dev.mjs --mock=ok       # + a fake Gemma upstream, so the AI flows work without a key
node landing/scripts/dev.mjs --mock=fail     # + an upstream that always fails (error states)
node landing/scripts/dev.mjs --mock=empty    # + an upstream that returns nothing usable
node landing/scripts/dev.mjs --host=0.0.0.0 --port 3000   # bind all interfaces (containers, previews)

GOOGLE_API_KEY="your-key" node landing/scripts/dev.mjs    # real Gemma 4 calls
```

The mock upstream speaks the same HTTP shape as the Gemini API, so the real handler, the
real prompts, and the real validators all run. It is a development tool only and is never
part of a deployment.

## 2. Deploy the Vercel project

The project already exists, so you normally leave it alone. If it ever has to be recreated:

1. Vercel → **Add New…** → **Project** → import this repository.
2. Set **Root Directory** to `landing`.
3. Set **Framework Preset** to **Other**.
   > There is no framework here: no package manifest, no build command, one plain function.
   > If Vercel guesses a preset, the build will try to do something the repository does not
   > support.
4. Leave **Build Command** and **Output Directory** empty.
5. Add the environment variable under **Settings → Environment Variables**:
   - `GOOGLE_API_KEY` = your key, for **Production** and **Preview**.
   A variable added *after* a deployment is not picked up by that deployment, so redeploy
   after adding it.
6. Click **Deploy**. `landing/vercel.json` registers the one function with a 60-second
   budget (`maxDuration: 60`) because a cold Gemma 4 answer can take 20–40 s, and sets the
   security headers.
7. If the URL asks you to log in to Vercel, disable **Settings → Deployment Protection →
   Vercel Authentication** to make it public.

Do not change the project's Root Directory, framework preset, connected branch, or
deployment protection as a side effect of another task.

### What is served

| Route | Source |
|------|--------|
| `/` | `landing/index.html` (the study app) |
| `/app.js`, `/styles.css` | `landing/app.js`, `landing/styles.css` |
| `/data/lessons.json` | `landing/data/lessons.json` |
| `POST /api/gemma` | `landing/api/gemma.mjs` — `{action, lessonId, …}` in, validated JSON out (prompts live in `landing/lib/ai.mjs` so Vercel builds exactly one endpoint) |
| `GET /api/gemma` | Availability probe: `{ok: true, aiAvailable: true|false}` |

`landing/.vercelignore` keeps `scripts/` and `tests/` out of the deployment. Every push to
the production branch redeploys automatically.

### Verify the deployment, not the upload

1. The **dashboard** renders: pathways list NEB, CEE, and IOE, and **Continue learning** is
   honest on a fresh browser ("Nothing studied yet in this browser") instead of claiming
   progress.
2. Opening a pathway reaches **Study**, and the goal → grade → subject → chapter → language
   filters cascade (the grade step is disabled for CEE/IOE, which have no grades).
3. A chapter opens as a lesson with its source panel, and **Practise** can write and mark a
   set while the AI is available.
4. The header chip reads **Gemma 4 ready** or, without a key, the honest **AI off — notes only**.
5. `GET /api/gemma` returns `{"ok": true, …}`.
6. `/tests/*` and `/scripts/*` return 404.

## 3. Tests

```bash
node --test landing/tests/*.mjs
```

| File | Covers |
|------|--------|
| `landing/tests/ai.test.mjs` | Prompts, defensive parsing, MCQ and flashcard validation, transport errors |
| `landing/tests/app.test.mjs` | Study-path resolution, including stale-selection repair |
| `landing/tests/dashboard.test.mjs` | The dashboard model, reading progress, quiz scoring, suggested questions, text sizes |
| `landing/tests/lessons.test.mjs` | Lesson data: structure, required fields, unique ids, language codes, track/language coverage |
| `landing/tests/deploy.test.mjs` | Function registration and budget, security headers, key stays server-side, no secret value committed under `landing/` |

## 4. Security checklist

- [ ] Rotate any API key that was ever shared in plain text.
- [ ] Restrict the key to the **Generative Language API** in Google AI Studio.
- [ ] Keep the key only in the Vercel project's environment variables — never in the
      repository, a file, chat, a screenshot, or a log.
- [ ] Set a spending/quota limit on the key to avoid surprise costs.
- [ ] Remember the function's rate limit is best-effort per instance.

## Troubleshooting

- **Header says "AI off — notes only"** — `GOOGLE_API_KEY` is not set for that environment,
  or the deployment predates the variable. Add it, then redeploy.
- **"Gemma 4 is temporarily unavailable"** — the upstream returned 5xx or the request timed
  out; retry. The message never contains the key, and a failure is never shown as an answer.
- **"The Gemma 4 API key was rejected"** — 400/403 from Google: wrong key, or the key is not
  enabled for the Generative Language API.
- **`/api/gemma` returns 404** — the Vercel Root Directory is not `landing`.
- **"Cross-origin request refused"** — the function refuses POSTs whose `Origin` host is
  neither the deployment host nor localhost.
- **Slow first answer** — a cold Gemma 4 call can take 20–40 seconds; later calls are faster.
