import os
import re
import secrets
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import requests
import streamlit as st
from supabase import create_client
from public_lookups import CALLING_CODES, COUNTRIES, NATIONALITIES, clean_phone_code


st.set_page_config(
    page_title="Support Puppy Fosters Algarve",
    page_icon="🐾",
    layout="centered",
)

# ---------------------------------------------------------------------
# BRANDING
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
      .block-container {max-width: 760px; padding-top: 4.2rem; padding-bottom: 3rem;}
      div[data-testid="stForm"] {padding: .2rem 0;}
      .stButton > button, .stFormSubmitButton > button {min-height: 3rem;}
      @media (max-width: 640px) {
        .block-container {padding-left: 1rem; padding-right: 1rem; padding-top: 3.8rem;}
        .pfpa-brand-title {font-size: 1.35rem !important;}
        .pfpa-brand-subtitle {font-size: .95rem !important;}
        div[data-testid="stVerticalBlock"] {gap: .55rem;}
      }
      .pfpa-brand {text-align:center; margin-bottom:1.2rem;}
      .pfpa-brand-title {
          text-align:center; font-size:1.55rem; font-weight:700;
          margin-top:.35rem; margin-bottom:.15rem;
      }
      .pfpa-brand-subtitle {
          text-align:center; font-size:1.02rem; margin-top:0;
          margin-bottom:1.4rem; opacity:.82;
      }
      .pfpa-section {
          font-weight:700; letter-spacing:.04em; text-transform:uppercase;
          border-bottom:1px solid rgba(128,128,128,.35);
          padding-bottom:.3rem; margin-top:1.4rem; margin-bottom:.8rem;
      }
      .pfpa-note {
          padding:.8rem 1rem; border:1px solid rgba(128,128,128,.25);
          border-radius:.5rem; margin:.6rem 0 1rem 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

logo_path = Path(__file__).resolve().parent / "puppy-fosters-logo.png"

if logo_path.exists():
    logo_bytes = logo_path.read_bytes()
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        st.image(logo_bytes, width="stretch")
else:
    st.warning("Logo file not found: puppy-fosters-logo.png")
    st.markdown(
        "<div class='pfpa-brand-title'>Puppy Fosters of Portugal – Algarve</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="pfpa-brand-title">Supporter Application</div>
    <div class="pfpa-brand-subtitle">
      Adoption · Fostering · Volunteering
    </div>
    """,
    unsafe_allow_html=True,
)

DATA_PROTECTION = (
    "I consent to Puppy Fosters of Portugal - Algarve holding and using the personal "
    "information provided in this form for the purposes of managing fostering, adoption "
    "or volunteering activities, contacting me, and maintaining operational records. "
    "Access will be limited to authorised team members and information will be retained "
    "only for as long as reasonably necessary. I understand that I may ask for access to, "
    "correction of, or deletion of my personal information, subject to any legal or "
    "operational requirements."
)

ROLE_OPTIONS = ["Volunteer", "Foster", "Adopter"]
VOLUNTEER_INTERESTS = ["Events", "Transport", "Photography", "Home Visits", "Other"]
FOSTER_ANIMALS = ["Dogs", "Puppies"]
FOSTER_DURATIONS = ["2-6 weeks", "Vacation", "Emergency Cover"]

# ---------------------------------------------------------------------
# CONFIG / SUPABASE
# ---------------------------------------------------------------------
def _secret(name, default=None):
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    if value in (None, ""):
        value = os.environ.get(name)
    return value if value not in (None, "") else default


SUPABASE_URL = _secret("SUPABASE_URL")
SUPABASE_KEY = _secret("SUPABASE_SECRET_KEY")
TURNSTILE_SITE_KEY = _secret("TURNSTILE_SITE_KEY")
TURNSTILE_SECRET_KEY = _secret("TURNSTILE_SECRET_KEY")
PRIVATE_APP_REVIEW_URL = str(_secret("PRIVATE_APP_REVIEW_URL", "") or "").rstrip("/")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("This form is not configured yet. Please contact Puppy Fosters of Portugal – Algarve.")
    st.stop()

if not TURNSTILE_SITE_KEY or not TURNSTILE_SECRET_KEY:
    st.error("Secure human verification is not configured yet. Please contact Puppy Fosters of Portugal – Algarve.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------------------------------------------------------------
# CLOUDFLARE TURNSTILE
# ---------------------------------------------------------------------
TURNSTILE_HTML = """
<div class="pfpa-turnstile">
  <div id="turnstile-container"></div>
  <div id="turnstile-status" aria-live="polite"></div>
</div>
"""

TURNSTILE_CSS = """
.pfpa-turnstile {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: .5rem;
    padding: .75rem 0;
}
#turnstile-status {
    font-size: .88rem;
    opacity: .75;
    text-align: center;
}
"""

TURNSTILE_JS = """
export default function(component) {
    const { parentElement, data, setStateValue } = component;
    const container = parentElement.querySelector("#turnstile-container");
    const status = parentElement.querySelector("#turnstile-status");

    const renderWidget = () => {
        if (!window.turnstile || !container) return;

        container.innerHTML = "";
        status.textContent = "Complete the security check to submit your application.";

        window.turnstile.render(container, {
            sitekey: data.sitekey,
            theme: "auto",
            size: "flexible",
            action: "supporter_application",
            callback: (token) => {
                status.textContent = "Security check completed.";
                setStateValue("token", token);
            },
            "expired-callback": () => {
                status.textContent = "Security check expired. Please complete it again.";
                setStateValue("token", "");
            },
            "error-callback": () => {
                status.textContent = "Security check could not be completed. Please try again.";
                setStateValue("token", "");
            }
        });
    };

    if (window.turnstile) {
        renderWidget();
        return;
    }

    let script = document.querySelector('script[data-pfpa-turnstile="1"]');
    if (!script) {
        script = document.createElement("script");
        script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
        script.async = true;
        script.defer = true;
        script.dataset.pfpaTurnstile = "1";
        document.head.appendChild(script);
    }

    if (window.turnstile) {
        renderWidget();
    } else {
        script.addEventListener("load", renderWidget, { once: true });
    }
}
"""

turnstile_component = st.components.v2.component(
    "pfpa_turnstile",
    html=TURNSTILE_HTML,
    css=TURNSTILE_CSS,
    js=TURNSTILE_JS,
)


def _verify_turnstile(token):
    """Validate a Turnstile token server-side with Cloudflare Siteverify."""
    if not token:
        return False, ["missing-input-response"]

    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": TURNSTILE_SECRET_KEY,
                "response": token,
            },
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException:
        return False, ["internal-error"]

    if not result.get("success"):
        return False, result.get("error-codes") or ["verification-failed"]

    # We set this action in the browser widget. Matching it prevents a valid
    # token generated for another action from being accepted here.
    if result.get("action") not in (None, "", "supporter_application"):
        return False, ["action-mismatch"]

    return True, []


def _send_email(to_address, subject, body):
    """Optional SMTP email; returns True only when successfully sent."""
    host = _secret("SMTP_HOST")
    port = int(_secret("SMTP_PORT", "587"))
    username = _secret("SMTP_USERNAME")
    password = _secret("SMTP_PASSWORD")
    sender = _secret("SMTP_FROM", username)
    if not all([host, username, password, sender, to_address]):
        return False

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls(context=context)
            server.login(username, password)
            server.send_message(msg)
        return True
    except Exception:
        return False


def _clean_email(value):
    return str(value or "").strip().lower()


def _valid_email(value):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", _clean_email(value)))


def _load_invite(token):
    if not token:
        return None
    result = (
        supabase.table("Supporter_Invite")
        .select("*")
        .eq("Token", token)
        .eq("Active", True)
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if not rows:
        return None

    invite = rows[0]
    expiry = invite.get("Expires_At")
    if expiry:
        try:
            expiry_dt = datetime.fromisoformat(str(expiry).replace("Z", "+00:00"))
            if expiry_dt < datetime.now(timezone.utc):
                return None
        except Exception:
            return None

    if int(invite.get("Use_Count") or 0) >= int(invite.get("Max_Uses") or 1):
        return None
    return invite


def _make_reference():
    return f"PFPA-{datetime.now():%Y%m%d}-{secrets.token_hex(3).upper()}"


# Success must be handled before re-validating a now-consumed one-time invite.
if st.session_state.get("supporter_submit_success"):
    ref = st.session_state["supporter_submit_success"]
    st.success("Thank you — your application has been received.")
    st.markdown(
        f"""
        <div class="pfpa-note">
        Your reference is <strong>{ref}</strong>.<br><br>
        A member of Puppy Fosters of Portugal – Algarve will review your information and
        contact you if anything further is required. Submission of this form does not
        itself constitute approval as an adopter, foster or volunteer.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ---------------------------------------------------------------------
# INVITATION GATE
# ---------------------------------------------------------------------
invite_token = str(st.query_params.get("invite", "") or "").strip()
invite = _load_invite(invite_token)

if not invite:
    st.info(
        "This application form is available by invitation. "
        "Please use the link provided by Puppy Fosters of Portugal – Algarve."
    )
    st.stop()

# ---------------------------------------------------------------------
# SECURE SUBMISSION STAGE
# ---------------------------------------------------------------------
pending = st.session_state.get("pending_supporter_submission")

if pending:
    st.markdown(
        "<div class='pfpa-section'>Secure submission</div>",
        unsafe_allow_html=True,
    )
    st.info(
        "Your application details have been checked but have not yet been submitted. "
        "Complete the Cloudflare security check below."
    )

    if st.session_state.get("turnstile_error"):
        st.error(st.session_state.pop("turnstile_error"))

    version = int(st.session_state.get("turnstile_version", 0))
    component_key = f"pfpa_turnstile_{version}"

    # A Components v2 default state key must have a matching
    # on_<state>_change callback.
    turnstile_result = turnstile_component(
        data={"sitekey": TURNSTILE_SITE_KEY},
        default={"token": ""},
        on_token_change=lambda: None,
        key=component_key,
        width="stretch",
        height=120,
    )
    turnstile_token = getattr(turnstile_result, "token", "") or ""

    if turnstile_token:
        valid_turnstile, turnstile_errors = _verify_turnstile(turnstile_token)

        if not valid_turnstile:
            st.session_state["turnstile_error"] = (
                "The security check could not be validated. Please complete it again."
            )
            st.session_state["turnstile_version"] = version + 1
            st.rerun()

        payload = pending["payload"]
        reference = pending["reference"]

        try:
            inserted = (
                supabase.table("Supporter_Submission")
                .insert(payload)
                .execute()
                .data
                or []
            )
            if not inserted:
                raise RuntimeError("No submission record was created.")

            supabase.table("Supporter_Invite").update({
                "Use_Count": int(pending.get("invite_use_count") or 0) + 1
            }).eq("Invite_ID", pending.get("invite_id")).execute()

            admin_email = _secret("APPLICATION_NOTIFICATION_EMAIL")

            review_lines = [
                "A new supporter application has been received.",
                "",
                f"Reference: {reference}",
                f"Name: {pending['first_name']} {pending['last_name']}",
                f"Roles: {', '.join(pending['roles'])}",
                "",
            ]
            if PRIVATE_APP_REVIEW_URL:
                review_lines.extend([
                    "Review the submitted information in the secure PFPA administration app:",
                    PRIVATE_APP_REVIEW_URL,
                ])
            else:
                review_lines.append(
                    "Please review it in the secure PFPA administration app."
                )

            notification_sent = _send_email(
                admin_email,
                f"New PFPA supporter application — {reference}",
                "\n".join(review_lines),
            )
            confirmation_sent = _send_email(
                pending["email"],
                f"PFPA application received — {reference}",
                (
                    f"Hello {pending['first_name']},\n\n"
                    "Thank you for your application to Puppy Fosters of Portugal - Algarve.\n"
                    f"We have received your application for: {', '.join(pending['roles'])}.\n\n"
                    f"Your reference is {reference}.\n\n"
                    "A member of the team will review your information and contact you if "
                    "anything further is required.\n\n"
                    "Submission does not itself constitute approval as an adopter, foster "
                    "or volunteer."
                ),
            )

            supabase.table("Supporter_Submission").update({
                "Notification_Sent": bool(notification_sent),
                "Confirmation_Sent": bool(confirmation_sent),
            }).eq("Reference", reference).execute()

            st.session_state.pop("pending_supporter_submission", None)
            st.session_state["supporter_submit_success"] = reference
            st.rerun()

        except Exception:
            # The Turnstile token is single-use. Keep the form payload, but
            # provide a fresh widget for the retry.
            st.session_state["turnstile_error"] = (
                "The security check passed, but the application could not be saved. "
                "Please complete the fresh security check and try again."
            )
            st.session_state.pop(component_key, None)
            st.session_state["turnstile_version"] = version + 1
            st.rerun()

    if st.button("← Edit application", width="stretch"):
        st.session_state.pop("pending_supporter_submission", None)
        st.session_state["turnstile_version"] = version + 1
        st.rerun()

    st.stop()


allowed_roles = invite.get("Allowed_Roles") or ROLE_OPTIONS
if isinstance(allowed_roles, str):
    allowed_roles = [allowed_roles]
allowed_roles = [r for r in ROLE_OPTIONS if r in allowed_roles] or ROLE_OPTIONS

st.markdown(
    "<div class='pfpa-note'>You only need to enter your personal details once. "
    "If you apply for more than one role, the same information is reused automatically.</div>",
    unsafe_allow_html=True,
)

roles = st.multiselect(
    "How would you like to support us? *",
    allowed_roles,
    default=allowed_roles if len(allowed_roles) == 1 else [],
    help="You can select more than one role.",
)

if not roles:
    st.caption("Select at least one role to continue.")
    st.stop()

# ---------------------------------------------------------------------
# FORM
# ---------------------------------------------------------------------
with st.form("supporter_application_form"):
    st.markdown("<div class='pfpa-section'>Your details</div>", unsafe_allow_html=True)

    # Single-column order is deliberate for natural tab order and mobile use.
    first_name = st.text_input("First name *")
    last_name = st.text_input("Last name *")

    default_calling_code = "+351 PT"
    phone_code = st.selectbox(
        "Country code *",
        CALLING_CODES,
        index=CALLING_CODES.index(default_calling_code)
        if default_calling_code in CALLING_CODES else 0,
    )
    phone_number = st.text_input(
        "Phone *",
        help="Enter the local/national number only; the country code is selected above.",
        placeholder="e.g. 912 345 678",
    )

    email_default = invite.get("Email") or ""
    email = st.text_input("E-mail *", value=email_default)

    postcode = st.text_input("Postcode *")
    parish = st.text_input("Parish *")
    country = st.selectbox(
        "Country *",
        COUNTRIES,
        index=COUNTRIES.index("Portugal") if "Portugal" in COUNTRIES else 0,
    )

    # These variables remain in the stored common-data structure for
    # compatibility with the Admin approval workflow, but are not collected
    # from Volunteer/Foster applicants.
    nationality = ""
    address = ""
    nif = ""
    household = children = current_pets = house_type = rent_own = ""
    outdoor_description = dog_experience = ""
    private_outdoor = None

    volunteer_data = {}
    if "Volunteer" in roles:
        st.markdown("<div class='pfpa-section'>Volunteer</div>", unsafe_allow_html=True)
        volunteer_data["interests"] = st.multiselect(
            "Interests *",
            VOLUNTEER_INTERESTS,
        )
        volunteer_data["other_notes"] = st.text_area(
            "Other interest notes",
            help="Complete this if you selected Other.",
        )

    foster_data = {}
    if "Foster" in roles:
        st.markdown("<div class='pfpa-section'>Foster</div>", unsafe_allow_html=True)
        foster_data["animals"] = st.multiselect(
            "What can you foster? *",
            FOSTER_ANIMALS,
        )
        foster_data["durations"] = st.multiselect(
            "Duration *",
            FOSTER_DURATIONS,
        )

    adopter_data = {}
    if "Adopter" in roles:
        st.markdown("<div class='pfpa-section'>Adopter</div>", unsafe_allow_html=True)

        household = st.text_area("Tell us about your home and household *")
        house_type = st.selectbox(
            "Do you live in a house or apartment? *",
            ["", "House", "Apartment", "Other"],
        )
        rent_own = st.selectbox(
            "Do you rent or own? *",
            ["", "Own", "Rent", "Other"],
        )
        children = st.text_area(
            "Do you have children? If yes, what ages? *",
            placeholder="If none, please enter 'None'.",
        )
        current_pets = st.text_area(
            "Do you currently have pets? What type and ages? *",
            placeholder="If none, please enter 'None'.",
        )
        outdoor_choice = st.selectbox("Private outdoor space? *", ["", "Yes", "No"])
        private_outdoor = (
            True if outdoor_choice == "Yes"
            else False if outdoor_choice == "No"
            else None
        )
        outdoor_description = st.text_area(
            "Please describe the outdoor space and how secure it is *",
            help="If you have no private outdoor space, explain that here.",
            height=90,
        )
        dog_experience = st.text_area(
            "Please describe your experience with dogs and puppies *"
        )

        adopter_data["exercise_training"] = st.text_area(
            "What is your exercise plan for the dog, and your thoughts about training? *"
        )
        adopter_data["preventative_care"] = st.text_area(
            "How do you feel about sterilisation, regular vaccines, deworming and flea/tick prevention? *"
        )
        adopter_data["schedule_alone"] = st.text_area(
            "What is your schedule during the day — how long will the dog be home alone? *"
        )
        adopter_data["sleep_arrangements"] = st.text_area(
            "Where will the dog sleep at night, and stay when no one is home? *"
        )
        adopter_data["vacation_plans"] = st.text_area(
            "Do you have any vacation plans coming up? *",
            placeholder="If none, please enter 'None'.",
        )
        adopter_data["travel_petsit"] = st.text_area(
            "When you travel, where will the dog stay if not travelling with you? *"
        )
        adopter_data["future_change"] = st.text_area(
            "If your housing, work or family situation changes, what would that mean for your dog? *"
        )

    additional_notes = ""

    st.markdown("<div class='pfpa-section'>Data protection and declaration</div>", unsafe_allow_html=True)
    st.write(DATA_PROTECTION)
    consent = st.checkbox("I have read and agree to the Data Protection statement. *")
    declaration = st.checkbox(
        "I confirm that the information supplied is accurate to the best of my knowledge. *"
    )
    signed_name = st.text_input(
        "Electronic signature — type your full name *",
        help="Typing your full name acts as your electronic signature for this application.",
    )

    submitted = st.form_submit_button(
        "Continue to secure submission",
        type="primary",
        width="stretch",
    )

if submitted:
    errors = []

    if not first_name.strip(): errors.append("First name is required.")
    if not last_name.strip(): errors.append("Last name is required.")
    if not phone_code.strip(): errors.append("Country code is required.")
    if not phone_number.strip(): errors.append("Phone is required.")
    if not _valid_email(email): errors.append("Please enter a valid e-mail address.")
    if not postcode.strip(): errors.append("Postcode is required.")
    if not parish.strip(): errors.append("Parish is required.")
    if not country.strip(): errors.append("Country is required.")

    if "Adopter" in roles:
        for label, value in [
            ("Home and household", household),
            ("House type", house_type),
            ("Rent/own", rent_own),
            ("Children", children),
            ("Current pets", current_pets),
            ("Outdoor space description", outdoor_description),
            ("Dog experience", dog_experience),
        ]:
            if not str(value or "").strip():
                errors.append(f"{label} is required for an adopter application.")
        if private_outdoor is None:
            errors.append("Please answer the private outdoor space question.")

        for key, label in [
            ("exercise_training", "Exercise/training"),
            ("preventative_care", "Preventative care"),
            ("schedule_alone", "Daily schedule"),
            ("sleep_arrangements", "Sleeping arrangements"),
            ("vacation_plans", "Vacation plans"),
            ("travel_petsit", "Travel/pet-sitting"),
            ("future_change", "Future changes"),
        ]:
            if not str(adopter_data.get(key) or "").strip():
                errors.append(f"{label} is required for an adopter application.")

    if "Foster" in roles:
        if not foster_data.get("animals"):
            errors.append("Select at least one foster animal type.")
        if not foster_data.get("durations"):
            errors.append("Select at least one foster availability option.")

    if "Volunteer" in roles:
        if not volunteer_data.get("interests"):
            errors.append("Select at least one volunteer interest.")
        if "Other" in volunteer_data.get("interests", []) and not volunteer_data.get("other_notes", "").strip():
            errors.append("Please describe your 'Other' volunteer interest.")

    if not consent:
        errors.append("Data Protection acceptance is required.")
    if not declaration:
        errors.append("The accuracy declaration is required.")
    if not signed_name.strip():
        errors.append("Please type your full name as your electronic signature.")
    if errors:
        for error in errors:
            st.error(error)
    else:
        common_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": _clean_email(email),
            "phone_code": clean_phone_code(phone_code),
            "phone_number": phone_number.strip(),
            "address": address.strip(),
            "postcode": postcode.strip(),
            "parish": parish.strip(),
            "country": country.strip(),
            "nationality": nationality.strip(),
            "nif": nif.strip(),
            "household": household.strip(),
            "children": children.strip(),
            "current_pets": current_pets.strip(),
            "house_type": house_type.strip(),
            "rent_own": rent_own.strip(),
            "private_outdoor": private_outdoor,
            "outdoor_description": outdoor_description.strip(),
            "dog_experience": dog_experience.strip(),
            "additional_notes": additional_notes.strip(),
        }

        reference = _make_reference()
        payload = {
            "Reference": reference,
            "Invite_ID": invite.get("Invite_ID"),
            "Status": "New",
            "Roles": roles,
            "Common_Data": common_data,
            "Adopter_Data": adopter_data if "Adopter" in roles else {},
            "Foster_Data": foster_data if "Foster" in roles else {},
            "Volunteer_Data": volunteer_data if "Volunteer" in roles else {},
            "Consent_Accepted": True,
            "Declaration_Accepted": True,
            "Signed_Name": signed_name.strip(),
            "Notification_Sent": False,
            "Confirmation_Sent": False,
        }

        # Do not write anything to Supabase yet. Hold the validated form
        # temporarily in this Streamlit session until Turnstile has passed.
        st.session_state["pending_supporter_submission"] = {
            "payload": payload,
            "invite_id": invite.get("Invite_ID"),
            "invite_use_count": int(invite.get("Use_Count") or 0),
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": _clean_email(email),
            "roles": list(roles),
            "reference": reference,
        }
        st.session_state["turnstile_version"] = int(
            st.session_state.get("turnstile_version", 0)
        ) + 1
        st.rerun()
