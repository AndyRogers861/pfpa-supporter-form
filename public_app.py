import os
import random
import re
import secrets
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

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
        st.image(logo_bytes, use_container_width=True)
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

ROLE_OPTIONS = ["Adopter", "Foster", "Volunteer"]
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
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("This form is not configured yet. Please contact Puppy Fosters of Portugal – Algarve.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


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

if "human_a" not in st.session_state:
    st.session_state["human_a"] = random.randint(2, 8)
    st.session_state["human_b"] = random.randint(2, 8)

# ---------------------------------------------------------------------
# FORM
# ---------------------------------------------------------------------
with st.form("supporter_application_form"):
    st.markdown("<div class='pfpa-section'>Your details</div>", unsafe_allow_html=True)

    # Single-column order is deliberate: it gives a natural tab order and
    # works cleanly on a telephone screen.
    first_name = st.text_input("First name *")
    last_name = st.text_input("Last name *")

    default_calling_code = "+351 PT"
    phone_code = st.selectbox(
        "Phone country code *",
        CALLING_CODES,
        index=CALLING_CODES.index(default_calling_code)
        if default_calling_code in CALLING_CODES else 0,
    )
    phone_number = st.text_input(
        "Phone number *",
        inputmode="tel",
        help="Enter the local/national number only; the country code is selected above.",
    )

    email_default = invite.get("Email") or ""
    email = st.text_input("Email address *", value=email_default)

    nationality = st.selectbox(
        "Nationality",
        [""] + NATIONALITIES,
        index=0,
        help="Optional at this stage.",
    )

    address = st.text_area(
        "Address *" if any(r in roles for r in ["Adopter", "Foster"]) else "Address",
        height=90,
    )
    postcode = st.text_input(
        "Post code *" if any(r in roles for r in ["Adopter", "Foster"]) else "Post code"
    )
    parish = st.text_input(
        "Parish *" if any(r in roles for r in ["Adopter", "Foster"]) else "Parish"
    )
    country = st.selectbox(
        "Country *",
        COUNTRIES,
        index=COUNTRIES.index("Portugal") if "Portugal" in COUNTRIES else 0,
    )
    nif = st.text_input("NIF", help="Optional at this stage")

    # Shared adopter/foster questions: asked only once, reused in both records.
    household = children = current_pets = house_type = rent_own = ""
    outdoor_description = dog_experience = ""
    private_outdoor = None

    if "Adopter" in roles or "Foster" in roles:
        st.markdown("<div class='pfpa-section'>Your home and experience</div>", unsafe_allow_html=True)
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
            "Please describe your experience with dogs, puppies or fostering *"
        )

    adopter_data = {}
    if "Adopter" in roles:
        st.markdown("<div class='pfpa-section'>Adoption</div>", unsafe_allow_html=True)
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

    foster_data = {}
    if "Foster" in roles:
        st.markdown("<div class='pfpa-section'>Fostering</div>", unsafe_allow_html=True)
        foster_data["animals"] = st.multiselect("What can you foster? *", FOSTER_ANIMALS)
        foster_data["durations"] = st.multiselect(
            "Availability / duration *",
            FOSTER_DURATIONS,
        )

    volunteer_data = {}
    if "Volunteer" in roles:
        st.markdown("<div class='pfpa-section'>Volunteering</div>", unsafe_allow_html=True)
        volunteer_data["interests"] = st.multiselect(
            "Areas of interest *",
            VOLUNTEER_INTERESTS,
        )
        volunteer_data["other_notes"] = st.text_area(
            "Other interest notes",
            help="Complete this if you selected Other.",
        )

    st.markdown("<div class='pfpa-section'>Anything else?</div>", unsafe_allow_html=True)
    additional_notes = st.text_area("Additional information or comments")

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

    st.markdown("<div class='pfpa-section'>Human check</div>", unsafe_allow_html=True)
    human_answer = st.number_input(
        f"What is {st.session_state['human_a']} + {st.session_state['human_b']}? *",
        min_value=0,
        step=1,
    )

    submitted = st.form_submit_button("Submit application", type="primary", use_container_width=True)

if submitted:
    errors = []
    requires_home = "Adopter" in roles or "Foster" in roles

    if not first_name.strip(): errors.append("First name is required.")
    if not last_name.strip(): errors.append("Last name is required.")
    if not phone_code.strip(): errors.append("Phone country code is required.")
    if not phone_number.strip(): errors.append("Phone number is required.")
    if not _valid_email(email): errors.append("Please enter a valid email address.")
    if not country.strip(): errors.append("Country is required.")

    if requires_home:
        for label, value in [
            ("Address", address), ("Post code", postcode), ("Parish", parish),
            ("Home and household", household), ("House type", house_type),
            ("Rent/own", rent_own), ("Children", children), ("Current pets", current_pets),
            ("Outdoor space description", outdoor_description),
            ("Dog/fostering experience", dog_experience),
        ]:
            if not str(value or "").strip():
                errors.append(f"{label} is required.")
        if private_outdoor is None:
            errors.append("Please answer the private outdoor space question.")

    if "Adopter" in roles:
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
    if int(human_answer) != int(st.session_state["human_a"] + st.session_state["human_b"]):
        errors.append("The human-check answer is incorrect.")

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

        try:
            inserted = supabase.table("Supporter_Submission").insert(payload).execute().data or []
            if not inserted:
                raise RuntimeError("No submission record was created.")

            supabase.table("Supporter_Invite").update({
                "Use_Count": int(invite.get("Use_Count") or 0) + 1
            }).eq("Invite_ID", invite.get("Invite_ID")).execute()

            admin_email = _secret("APPLICATION_NOTIFICATION_EMAIL")
            notification_sent = _send_email(
                admin_email,
                f"New PFPA supporter application — {reference}",
                (
                    f"A new supporter application has been received.\n\n"
                    f"Reference: {reference}\n"
                    f"Name: {first_name.strip()} {last_name.strip()}\n"
                    f"Roles: {', '.join(roles)}\n\n"
                    f"Please review it in the secure PFPA administration app."
                ),
            )
            confirmation_sent = _send_email(
                _clean_email(email),
                f"PFPA application received — {reference}",
                (
                    f"Hello {first_name.strip()},\n\n"
                    f"Thank you for your application to Puppy Fosters of Portugal - Algarve.\n"
                    f"We have received your application for: {', '.join(roles)}.\n\n"
                    f"Your reference is {reference}.\n\n"
                    f"A member of the team will review your information and contact you if "
                    f"anything further is required.\n\n"
                    f"Submission does not itself constitute approval as an adopter, foster "
                    f"or volunteer."
                ),
            )

            supabase.table("Supporter_Submission").update({
                "Notification_Sent": bool(notification_sent),
                "Confirmation_Sent": bool(confirmation_sent),
            }).eq("Reference", reference).execute()

            st.session_state["supporter_submit_success"] = reference
            st.rerun()
        except Exception:
            st.error(
                "We could not submit your application at this time. "
                "Please try again or contact Puppy Fosters of Portugal – Algarve."
            )
