# PFPA Public Supporter Form — Production Release 1.0

Separate public-facing Streamlit app for invitation-only Volunteer, Foster and Adopter applications.

## Production controls
- Valid `Supporter_Invite` token required.
- Invitation expiry, active state and use limits enforced.
- Role permissions fail closed.
- Applicant email is locked to the invited address.
- Dog-specific adoption invitations recheck dog availability.
- Dog availability is checked again immediately before save.
- Dog-specific adopters can download and must upload the questionnaire PDF.
- Cloudflare Turnstile is validated server-side.
- Successful submissions feed the V2 Applications workflow; no live Supporter is auto-created.
- Uploaded V2 documents use the `v2/` Storage prefix.

## Streamlit Cloud
Deploy as a separate PUBLIC Streamlit app. The app URL is public, but the form itself is invitation-gated.
Main file: `public_app.py`.

Copy settings from `.streamlit/secrets.example.toml` into Streamlit Cloud Secrets. Do not commit real secrets.

After deployment, ensure the Cloudflare Turnstile widget allows the final Streamlit hostname.
