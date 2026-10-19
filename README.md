# PFPA Update 46 — Public Privacy and Terms pages

This update adds public Streamlit pages suitable for linking from the PFPA supporter-facing app and for supplying as policy URLs during Google OAuth verification.

## Files
- Replace `public_app.py` with the supplied version.
- Add `pages/Privacy_Policy.py`.
- Add `pages/Terms_of_Service.py`.

No SQL changes are required.

## Behaviour
- The supporter application remains invitation-only.
- Privacy Policy and Terms pages do **not** require an invitation token.
- The root supporter page shows Privacy Policy and Terms links before invitation validation, so they remain visible even when a visitor has no invitation.
- Policy pages do not initialise Supabase, OAuth or Turnstile and therefore remain independently accessible.

## Expected Streamlit routes
For a Streamlit Community Cloud application at:

`https://YOUR-APP.streamlit.app/`

the page routes should be:

`https://YOUR-APP.streamlit.app/Privacy_Policy`

`https://YOUR-APP.streamlit.app/Terms_of_Service`

Confirm the final routes in the browser after deployment before entering them in Google Cloud.

## Installation
1. Add the two files under the repository `pages/` directory.
2. Replace `public_app.py`.
3. Commit and push.
4. Let Streamlit redeploy.
5. Test both policy URLs in a private/incognito browser window without an invitation link.
6. Confirm the pages can be opened without Google sign-in or PFPA authentication.

## Google OAuth note
A public policy URL is necessary but Google may also require the application's authorised domain/homepage to satisfy its domain-verification requirements. The Streamlit pages solve the public-page requirement; they do not by themselves establish ownership of a custom domain.
