# Running and deploying Akshar

There is **exactly one published deployment**: the Vercel project for `landing/`. The
Streamlit app in `app.py` is a reference implementation for local comparison. The binding
rules are in [`AGENTS.md` §10](../AGENTS.md):

- Never deploy, redeploy, publish, unpublish, or change hosting unless a human explicitly
  asks for it in that task. "Commit and push" is not permission to deploy.
- Never add, switch, or duplicate a hosting platform or project — no new Streamlit Cloud
  app, no Render/Railway/Netlify/Fly/Cloudflare/GitHub Pages site, no second Vercel project.
- Never push to `main` to store or share work: it is the production branch, so a push
  republishes both the app Streamlit Community Cloud watches and the Vercel project. Work on
  a task branch and let a maintainer merge.
- Never create a temporary public deployment to test something. Run it locally.

| Front end | Where it is published | Notes |
|---|---|---|
| `landing/` — the product | Vercel project `akshar-nepluro`, Root Directory `landing` | On this branch `landing/` is still the earlier landing page; the study-app redesign is on a task branch and goes live when it is merged here |
| `app.py` — reference implementation | An **existing** Streamlit Community Cloud app that follows `main` | Kept for local comparison and experiments. **Do not deploy or redeploy it.** |

## 0. Prerequisites

- The repository on GitHub: <https://github.com/sagarxettri000/Akshar>
- A **fresh** Google AI Studio API key (rotate any key that was ever shared publicly)

## 1. Run it locally

```bash
pip install -r requirements-dev.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then fill in GOOGLE_API_KEY
streamlit run app.py
```

The landing page has no build step: open `landing/index.html` directly in a browser.

## 2. The Vercel project (the published front end)

It already exists, so you normally do not touch it. If it ever has to be recreated:

1. Vercel → **Add New…** → **Project** → import this repository.
2. **Root Directory** = `landing`, **Framework Preset** = **Other**, Build Command and
   Output Directory empty.
   > Vercel may otherwise detect **Python** from `requirements.txt` and fail the build.
3. Environment variables: `GOOGLE_API_KEY` for Production and Preview — needed once the
   study app's serverless function is in `landing/`. A variable added after a deployment is
   not picked up by it, so redeploy afterwards.
4. Deploy, then check what the URL actually serves rather than trusting the upload.

Do not change the project's Root Directory, framework preset, connected branch, or
deployment protection as a side effect of another task.

## 3. The Streamlit app (reference implementation — do not deploy it)

An existing Streamlit Community Cloud app follows `main` and rebuilds whenever that branch
changes. Do not create, redeploy, or repurpose a Streamlit deployment: it is a local
reference implementation, and the Vercel web app is the one published front end.

## 4. Security checklist

- [ ] Revoke and rotate any API key that was shared in plain text.
- [ ] Restrict the key to the **Generative Language API** in Google AI Studio.
- [ ] Keep the key in the host's environment variables (Vercel) and in a local, gitignored
      `.streamlit/secrets.toml` for local Streamlit runs — never in the repository, a file,
      chat, a screenshot, or a log.
- [ ] Confirm `.streamlit/secrets.toml` and `.env` are gitignored (they are) and never committed.
- [ ] Set a spending/quota limit on the key to avoid surprise costs.

## Troubleshooting

- **"No Gemma 4 API key found."** — a local Streamlit run needs `GOOGLE_API_KEY` in
  `.streamlit/secrets.toml` or the environment.
- **The Vercel URL returns 404** — the project's Root Directory is not `landing`.
- **`ModuleNotFoundError: google.genai`** — `requirements.txt` must stay at the repository root.
- **Slow first answer** — the first Gemma 4 call can take 20–40 seconds; later calls are
  usually faster.
