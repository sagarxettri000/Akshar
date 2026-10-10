# Running and deploying Akshar

Akshar has two front ends over the same content, the same prompts, and the same
validation:

| Front end | Where it runs | What it is |
|-----------|---------------|------------|
| **Web app** (`landing/`) | **Vercel** — static files + one serverless function | The deployed product: filters, lesson notes, Explain / Ask / Practise / Flashcards |
| Streamlit app (`app.py`) | Streamlit Community Cloud or locally | The reference implementation of the same study loop |

The web app is a plain HTML/CSS/JS page plus one Node function
(`landing/api/gemma.mjs`). It has **no build step and no npm dependencies**, so
Vercel only needs to serve files and run the function.

## 0. Prerequisites

- The repository on GitHub: <https://github.com/sagarxettri000/Akshar>
- A **fresh** Google AI Studio API key (rotate any key that was ever shared publicly)

## 1. Run it locally

### Web app (no key needed for the reading part)

```bash
node landing/scripts/dev.mjs            # http://127.0.0.1:3000
node landing/scripts/dev.mjs --mock=ok  # + a fake Gemma upstream, key not needed
node landing/scripts/dev.mjs --mock=fail   # exercise the error state
node landing/scripts/dev.mjs --mock=empty  # exercise the "nothing usable" state
```

With `--mock`, the real handler, the real prompts, and the real validators run
against a stand-in upstream — useful for UI work and demos without spending quota.
Without `--mock`, export a real key first:

```bash
GOOGLE_API_KEY="your-key" node landing/scripts/dev.mjs
```

### Streamlit app

```bash
pip install -r requirements-dev.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then fill in GOOGLE_API_KEY
streamlit run app.py
```

## 2. Deploy the web app on Vercel

1. Go to <https://vercel.com> → **Add New…** → **Project** → import this repository.
2. Set **Root Directory** to `landing`.
3. Set **Framework Preset** to **Other**.
   > Vercel may otherwise detect **Python** from `requirements.txt` and try to build it.
4. Leave **Build Command** empty and **Output Directory** empty.
5. Add the environment variable under **Settings → Environment Variables**:
   - `GOOGLE_API_KEY` = your key (Production and Preview)
   The key is read only inside `landing/api/gemma.mjs`; it is never sent to the browser.
6. Click **Deploy**. `landing/vercel.json` registers the function and gives it a
   60-second budget (`maxDuration: 60`) because a cold Gemma 4 answer can take 20–40 s.
7. Open the deployment URL. The status chip in the header should read **Gemma 4 ready**.
   If it reads **AI off — notes only**, the environment variable is missing or was added
   after the deployment (redeploy after adding it).
8. If the URL asks you to log in to Vercel, disable **Settings → Deployment Protection →
   Vercel Authentication** to make it public.

### What is served

| Route | Source |
|-------|--------|
| `/` | `landing/index.html` (the study app) |
| `/app.js`, `/styles.css` | `landing/app.js`, `landing/styles.css` |
| `/data/lessons.json` | `landing/data/lessons.json` |
| `POST /api/gemma` | `landing/api/gemma.mjs` — `{action, lessonId, …}` in, validated JSON out |
| `GET /api/gemma` | Availability probe: `{ok: true, aiAvailable: true|false}` |

Every push to the production branch redeploys automatically.

## 3. Optional: `main` branch and the Streamlit app

The Streamlit app is still deployable to Streamlit Community Cloud (branch `main`,
main file `app.py`, secret `GOOGLE_API_KEY`). It is useful for local experiments and as
a second implementation to compare against, but the Vercel web app is what the team
shares with students.

## 4. Tests

```bash
python -m pytest -q                     # Python: AI service, content, design tokens, web assets
node --test landing/api/ai.test.mjs     # JS: prompts, parsing, validation, transport
node --test landing/app.test.mjs        # JS: study-selection resolution
```

`tests/test_web_app.py` fails if the lesson copy served to the browser drifts from
`data/lessons.json`, if the prompts here stop matching `ai_service.py`, or if the Python
and JavaScript validators disagree on a shared corpus of model outputs.

## 5. Security checklist

- [ ] Rotate any API key that was ever shared in plain text.
- [ ] Restrict the key to the **Generative Language API** in Google AI Studio.
- [ ] Keep the key only in Vercel environment variables (and Streamlit secrets if you run it).
- [ ] Confirm `.streamlit/secrets.toml` and `.env` are gitignored and never committed.
- [ ] Set a spending/quota limit on the key.
- [ ] Keep the function's rate limit in mind: requests are capped best-effort per instance.

## Troubleshooting

- **Header says “AI off — notes only”** — `GOOGLE_API_KEY` is not set for that
  environment (or the deployment predates the variable). Add it, then redeploy.
- **“Gemma 4 is temporarily unavailable”** — the upstream returned 5xx or the request
  timed out; retry. The message never contains the key, and a failure is never shown as
  an answer.
- **“The Gemma 4 API key was rejected”** — 400/403 from Google: wrong key, or the key is
  not enabled for the Generative Language API.
- **`/api/gemma` returns 404** — the Vercel Root Directory is not `landing`.
- **`Cross-origin request refused`** — the function refuses POSTs whose `Origin` host is
  neither the deployment host nor localhost.
- **Slow first answer** — a cold Gemma 4 call can take 20–40 seconds; later calls are faster.
