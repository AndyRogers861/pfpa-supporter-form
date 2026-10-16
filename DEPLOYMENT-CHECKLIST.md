# Public App Deployment Checklist

- [ ] Separate GitHub repository from private staff app.
- [ ] No `secrets.toml` or credentials committed.
- [ ] Streamlit main file is `public_app.py`.
- [ ] App visibility is Public.
- [ ] Supabase secrets configured.
- [ ] Turnstile keys configured and deployed hostname permitted.
- [ ] SMTP settings configured.
- [ ] `APPLICATION_NOTIFICATION_EMAIL` correct.
- [ ] `PRIVATE_APP_REVIEW_URL` points to private app.
- [ ] Base URL without `?invite=` shows invitation-only message.
- [ ] Volunteer invitation test succeeds.
- [ ] Dog-specific Adopter invitation test succeeds.
- [ ] Questionnaire download/upload succeeds.
- [ ] Confirmation/admin emails arrive.
- [ ] Submission appears in private Applications.
