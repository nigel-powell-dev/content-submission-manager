# Stratford Oaks Content Submission Manager (prototype)

This is a **first visual prototype**, not the final AI-assisted submission service.

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, `logo.jpg`, and `.streamlit/config.toml` (keep the `.streamlit` folder).
2. Open Streamlit Community Cloud and choose **Create app** / **Deploy from GitHub**.
3. Select the repository, branch, and `app.py`, then deploy.

## Important before using for real submissions
- The prototype uses a local SQLite file. **Streamlit Community Cloud storage is not persistent**: records can disappear when the app restarts, so do not rely on drafts or submitted content until external storage is configured.
- The **Submit** button currently only changes local status. It does **not** email Nigel or feed the Weekly What's On Manager.
- This version uses typed text or the computer's built-in dictation. It does not yet offer an AI conversation or native microphone recording.
- Before wider deployment, add login/access controls, persistent database, email delivery, and AI API integration. Store API keys in Streamlit secrets, never in the GitHub repository.
