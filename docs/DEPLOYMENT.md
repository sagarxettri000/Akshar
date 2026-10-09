# Deploying Akshar

Akshar deploys in two parts:

1. **The app** — `app.py` runs on **Streamlit Community Cloud** (free, made for Streamlit).
2. **The landing page** — `landing/` is a static site hosted on **Vercel**.

Streamlit needs a long-running Python server with a persistent WebSocket and in-memory
session state. Vercel only runs static sites and short-lived serverless functions, so the
app cannot run on Vercel — the landing page can.

## 0. Prerequisites

- The repository is on GitHub: <https://github.com/sagarxettri000/Akshar>
- A **fresh** Google AI Studio API key (rotate any key that was shared publicly).

## 1. Deploy the app on Streamlit Community Cloud

1. Go to <https://share.streamlit.io> and sign in with GitHub.
2. Click **Create app** → **Deploy a public app from GitHub**.
3. Fill in:
   - **Repository:** `sagarxettri000/Akshar`
   - **Branch:** `main`
   - **Main file path:** `app.py` — or leave the default `streamlit_app.py`, which runs the identical app
4. Open **Advanced settings** → **Secrets** and paste:

   ```toml
   GOOGLE_API_KEY = "your-new-google-ai-studio-key"
   ```

5. (Optional) Select **Python 3.12**.
6. Click **Deploy**. Streamlit installs `requirements.txt` and builds the app.
7. Copy the public URL, for example `https://akshar.streamlit.app`.

The app reads the key from Streamlit secrets — it is never in the repository. Every push
to `main` redeploys the app automatically.

## 2. Deploy the landing page on Vercel

1. Go to <https://vercel.com> → **Add New…** → **Project**.
2. Import the same GitHub repository.
3. Set **Root Directory** to `landing`.
4. Set **Framework Preset** to **Other**.
   > Vercel may auto-detect this repository as **Python** (because of `requirements.txt`),
   > which makes the build error out in about a second. Clearing the preset to **Other** is required.
5. Leave **Build Command** and **Output Directory** empty, then click **Deploy**.
6. If the URL asks you to log in to Vercel, open **Project → Settings → Deployment Protection**
   and disable **Vercel Authentication**. The site is then publicly reachable.
7. `landing/index.html` already points at the live Streamlit app. If the app URL changes,
   update the link and push — Vercel redeploys automatically.

## 3. Optional: custom domain

In Vercel → your project → **Settings** → **Domains**, add a domain and follow the DNS
instructions. You can point a subdomain (for example `app.yourdomain.com`) at the
Streamlit app by adding it in Streamlit Cloud's app settings.

## 4. Security checklist

- [ ] Revoke and rotate any API key that was shared in plain text.
- [ ] Restrict the new key to the **Generative Language API** in Google AI Studio.
- [ ] Keep keys only in Streamlit secrets and Vercel environment variables.
- [ ] Confirm `.streamlit/secrets.toml` is gitignored (it is) and never committed.
- [ ] Set a spending/quota limit on the key to avoid surprise costs.

## Troubleshooting

- **"No Gemma 4 API key found."** — Add `GOOGLE_API_KEY` in Streamlit Cloud → Settings → Secrets.
- **`ModuleNotFoundError: google.genai`** — Make sure `requirements.txt` is at the repository root.
- **Landing page shows Vercel 404** — Confirm the Vercel project Root Directory is `landing`.
- **Slow first answer** — The first Gemma 4 call can take 20–40 seconds; later calls are usually faster.
