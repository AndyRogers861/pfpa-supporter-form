import os
import re
import io
import html
import secrets
import smtplib
import ssl
from datetime import date, datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import requests
import streamlit as st
from supabase import create_client
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from pypdf import PdfReader, PdfWriter
from public_lookups import CALLING_CODES, COUNTRIES, clean_phone_code


st.set_page_config(
    page_title="Puppy Fosters - Algarve",
    page_icon="🐾",
    layout="centered",
)


# ---------------------------------------------------------------------
# PUBLIC LEGAL PAGES
# ---------------------------------------------------------------------
# These are rendered inside this same Streamlit app using query-string URLs.
# They deliberately run before invitation, Supabase and Turnstile checks so
# Google OAuth reviewers and members of the public can open them anonymously.

def _policy_link_bar():
    st.markdown(
        """
        <div style="margin:.7rem 0 1.2rem 0;">
          <div style="margin-bottom:.3rem;">
            <a href="?" target="_self"
               style="text-decoration:none;font-size:1.08rem;font-weight:700;">
              🐾 Supporter Application
            </a>
          </div>
          <div style="font-size:.82rem;opacity:.78;display:flex;gap:.55rem;flex-wrap:wrap;">
            <a href="?policy=terms" target="_self" style="text-decoration:none;">Terms of Service</a>
            <span aria-hidden="true">·</span>
            <a href="?policy=privacy" target="_self" style="text-decoration:none;">Privacy Policy</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _policy_logo():
    logo = Path(__file__).resolve().parent / "puppy-fosters-logo.png"
    if logo.exists():
        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            st.image(logo.read_bytes(), width="stretch")


def render_privacy_policy():
    _policy_logo()
    st.markdown("**Puppy Fosters - Algarve**")
    st.title("Privacy Policy")
    st.caption("Effective date: 19 October 2026")
    _policy_link_bar()
    st.markdown("""
### 1. About this policy
Puppy Fosters - Algarve operates the Puppy Fosters - Algarve Management System and related invitation-based supporter application services (together, the “Service”). This Privacy Policy explains what personal information the Service processes, why it is processed, how it is protected, and the choices available to users and other individuals whose information is recorded in the Service.

Puppy Fosters - Algarve is the controller of personal data processed for its own rescue, fostering, adoption, volunteer and administrative purposes. Where Puppy Fosters - Algarve acts on behalf of another organisation, the responsibilities of the parties may be defined separately.

### 2. Information we process
The Service may process information about authorised users, supporters, foster carers, adopters, volunteers, applicants, veterinary contacts, donors and other people involved in Puppy Fosters - Algarve activities. Depending on the person and purpose, this may include name, email address, telephone number, address or location information, role and application information, correspondence, notes, documents supplied to Puppy Fosters - Algarve, fostering and adoption history, donation records and other information needed to administer Puppy Fosters - Algarve activities.

The Service also stores information about dogs, including identification, health, veterinary, fostering, adoption, cost, donation and document records. Some of those records can be linked to an identifiable person.

### 3. Google sign-in and Google user data
The Puppy Fosters - Algarve Management System uses Google OAuth solely to authenticate approved users and control access to the private management application. The Google sign-in process may provide Puppy Fosters - Algarve with basic account identity information needed for sign-in, such as a Google account identifier, name, email address and, where supplied by Google, a profile image.

Puppy Fosters - Algarve does not use Google OAuth to read Gmail messages, Google Drive files, Google Calendar data, contacts or other Google account content unless the Service is changed in future and the user is clearly informed and asked to authorise the additional access.

Google user data obtained through OAuth is used only for authentication, account matching, access control, security and administration of the Service. It is not used for advertising, profiling for advertising, or sale to third parties.

Puppy Fosters - Algarve's use and transfer of information received from Google APIs will adhere to the [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy), including the Limited Use requirements.

### 4. How we use personal information
Puppy Fosters - Algarve may use personal information to operate and secure the Service; manage authorised user accounts; process supporter, foster, adopter and volunteer applications; manage fostering and adoption activity; maintain animal health and veterinary records; administer donations, costs and documents; communicate with relevant people; maintain audit and operational records; meet legal, safeguarding, accounting and regulatory obligations; and protect the rights, welfare and safety of people and animals.

Puppy Fosters - Algarve will not use personal information for purposes that are incompatible with the reason it was collected without providing appropriate information and, where required, obtaining consent.

### 5. Legal bases under data protection law
Where the EU General Data Protection Regulation (GDPR) or Portuguese data protection law applies, Puppy Fosters - Algarve will process personal data only where it has an appropriate legal basis. Depending on the circumstances, this may include consent, steps taken at the request of an individual before entering into an agreement, performance of an agreement, compliance with a legal obligation, protection of vital interests, or Puppy Fosters - Algarve's legitimate interests in operating an animal rescue and adoption service safely and effectively.

Where special-category personal data is exceptionally required, Puppy Fosters - Algarve will identify an additional lawful condition before processing it.

### 6. Sharing and service providers
Puppy Fosters - Algarve may share information internally with authorised staff and volunteers who need it for their role, and externally with veterinary practices, adopters, foster carers, service providers, professional advisers, authorities or other parties where necessary for Puppy Fosters - Algarve activities, safety, legal obligations or the individual's request.

The Service uses third-party technology providers, including cloud hosting, database, authentication and application-hosting providers. These providers may process data on Puppy Fosters - Algarve's behalf under their own security and contractual arrangements. Google acts as the authentication provider for Google sign-in. Puppy Fosters - Algarve does not sell personal information.

### 7. Storage, security and international transfers
Puppy Fosters - Algarve applies reasonable technical and organisational measures designed to protect information against unauthorised access, loss, misuse or alteration. Access to the private management system is restricted to approved users and is subject to authentication and role-based controls.

Some technology providers may process or store information outside Portugal or the European Economic Area. Where required, Puppy Fosters - Algarve will rely on an appropriate transfer mechanism or other lawful safeguard.

### 8. Retention
Puppy Fosters - Algarve keeps personal information only for as long as reasonably necessary for the purposes described in this policy, including animal welfare and adoption history, safeguarding, legal, accounting, audit and dispute-resolution needs. Retention periods may therefore vary by record type.

Authentication information linked to an authorised user may be retained while the account remains active and for a reasonable period afterwards where required for security, audit or legal purposes.

### 9. Your rights
Subject to applicable law, individuals may have rights to request access to their personal data, correction of inaccurate information, deletion, restriction of processing, objection to certain processing, portability of information, and withdrawal of consent where consent is the legal basis. Exercising a right may be subject to legal exceptions, including records Puppy Fosters - Algarve must retain for legal, safeguarding, accounting or animal-welfare reasons.

Individuals also have the right to lodge a complaint with the Portuguese data protection authority, Comissão Nacional de Proteção de Dados (CNPD), where applicable.

### 10. Google account permissions and deletion requests
Users can review or revoke permissions granted to the Service through their [Google Account security settings](https://myaccount.google.com/permissions). Revoking Google sign-in permission may prevent further access to the Puppy Fosters - Algarve Management System but does not automatically delete records Puppy Fosters - Algarve is otherwise required or entitled to retain.

Requests concerning access, correction or deletion of personal information can be made through Puppy Fosters - Algarve using the contact route stated below. Puppy Fosters - Algarve will verify the requester's identity where appropriate before acting on a request.

### 11. Cookies and session data
The Service may use essential cookies, session tokens or similar technologies required for authentication, security and operation of the application. Puppy Fosters - Algarve does not use Google OAuth data for advertising cookies or cross-site advertising profiles.

### 12. Changes to this policy
Puppy Fosters - Algarve may update this Privacy Policy when the Service, legal requirements or data practices change. The current version will be published on the Service website with the date of the latest update.

### 13. Contact
For privacy and data protection questions, requests or complaints, please contact Puppy Fosters - Algarve using the contact details published on the Puppy Fosters - Algarve application homepage. The same public contact route should be maintained alongside this policy so that individuals can contact Puppy Fosters - Algarve without signing in.

---
Puppy Fosters - Algarve | Privacy Policy | 19 October 2026
""")


def render_terms_of_service():
    _policy_logo()
    st.markdown("**Puppy Fosters - Algarve**")
    st.title("Terms of Service")
    st.caption("Effective date: 19 October 2026")
    _policy_link_bar()
    st.markdown("""
### 1. About these Terms
These Terms of Service govern use of the Puppy Fosters - Algarve Management System and related invitation-based Puppy Fosters - Algarve application services (the “Service”), operated by Puppy Fosters - Algarve. By accessing or using the Service, you agree to these Terms. If you are using the Service on behalf of Puppy Fosters - Algarve or another authorised organisation, you must have authority to do so.

### 2. Purpose of the Service
The Service is provided to support Puppy Fosters - Algarve's animal rescue, fostering, adoption, volunteer, veterinary, donation and administrative activities. The private management application is intended for approved Puppy Fosters - Algarve users. Public or supporter-facing functions may be restricted to people who receive a valid invitation or authorised link.

### 3. Eligibility and accounts
You must use the Service only if you are authorised to do so. You are responsible for maintaining the security of your account and sign-in method and for promptly reporting suspected unauthorised access.

Google sign-in is used only as an authentication method for the private Puppy Fosters - Algarve Management System. A successful Google sign-in does not itself create a right to use the Service; Puppy Fosters - Algarve may restrict access to approved email addresses, roles or users.

### 4. Acceptable use
You must use the Service lawfully, responsibly and only for legitimate Puppy Fosters - Algarve purposes. You must not attempt to gain unauthorised access; interfere with the Service; introduce malicious code; scrape or extract data without authority; share credentials; access records without a genuine operational need; misuse personal information; or use the Service in a way that could harm people, animals, Puppy Fosters - Algarve, its volunteers or third parties.

Users must respect confidentiality and data protection obligations when viewing, entering, downloading or sharing information from the Service.

### 5. Accuracy of information
Users should take reasonable care to ensure information entered into the Service is accurate, relevant and up to date. Puppy Fosters - Algarve may correct, archive or remove information where necessary for operational, legal, welfare or data-quality reasons.

Animal health, veterinary, adoption and fostering information in the Service is an administrative record and is not a substitute for professional veterinary, legal or other specialist advice.

### 6. Documents and user-provided content
Where the Service allows documents, photographs, forms or other content to be uploaded, you must have authority to provide that content and must not knowingly upload unlawful, misleading, malicious or irrelevant material. Puppy Fosters - Algarve may restrict, remove or archive uploaded material where appropriate.

You retain any rights you have in material you provide, but you grant Puppy Fosters - Algarve permission to store, reproduce and use it as reasonably necessary to operate Puppy Fosters - Algarve activities and the Service.

### 7. Privacy and Google OAuth
Use of personal information is governed by the Puppy Fosters - Algarve Privacy Policy. Google OAuth is used to authenticate approved users and provide basic account identity information required for sign-in and access control. Puppy Fosters - Algarve does not use Google OAuth data for advertising or sell it to third parties.

By using Google sign-in, you also remain subject to Google's applicable terms and account policies.

### 8. Availability and changes
Puppy Fosters - Algarve aims to keep the Service available and reliable but does not guarantee uninterrupted or error-free operation. The Service may be changed, suspended or temporarily unavailable for maintenance, security, technical or operational reasons.

Puppy Fosters - Algarve may add, modify or remove features where reasonably necessary. Material changes affecting users or personal-data practices will be communicated where appropriate.

### 9. Suspension and termination
Puppy Fosters - Algarve may suspend or terminate access where a user no longer requires access, leaves an authorised role, breaches these Terms, creates a security or privacy risk, or where suspension is otherwise reasonably necessary to protect the Service, Puppy Fosters - Algarve, people or animals.

Users may stop using the Service at any time. Ending access does not automatically require Puppy Fosters - Algarve to delete records that it must or is entitled to retain for legal, accounting, safeguarding, animal-welfare, audit or operational reasons.

### 10. Intellectual property
The Service, its software, branding, documentation and original content are owned by or licensed to Puppy Fosters - Algarve or its respective rights holders. Except as necessary for authorised use of the Service, no licence is granted to copy, modify, distribute or exploit those materials.

### 11. Third-party services
The Service depends on third-party providers such as Google and cloud, database and application-hosting services. Puppy Fosters - Algarve is not responsible for independent third-party services or for outages or changes outside Puppy Fosters - Algarve's reasonable control. Third-party services may be subject to their own terms and privacy policies.

### 12. Liability
To the extent permitted by law, the Service is provided for Puppy Fosters - Algarve's operational use without guarantees that it will meet every requirement or be available at all times. Puppy Fosters - Algarve does not exclude or limit liability where doing so would be unlawful, including liability that cannot legally be excluded under applicable consumer, data protection or other mandatory law.

Users remain responsible for professional, welfare and operational decisions and should not rely solely on the Service where independent verification is reasonably required.

### 13. Governing law
These Terms are governed by the laws of Portugal, subject to any mandatory rights or jurisdiction that applicable law gives an individual. Any dispute should first be raised with Puppy Fosters - Algarve so that the parties can try to resolve it informally.

### 14. Changes to these Terms
Puppy Fosters - Algarve may update these Terms when the Service, legal requirements or operating arrangements change. The latest version will be published on the Service website with its effective date. Continued use after an update constitutes acceptance where permitted by law.

### 15. Contact
Questions about these Terms should be sent to Puppy Fosters - Algarve using the contact details published on the Puppy Fosters - Algarve application homepage.

---
Puppy Fosters - Algarve | Terms of Service | 19 October 2026
""")


_policy = str(st.query_params.get("policy", "") or "").strip().lower()
if _policy == "privacy":
    render_privacy_policy()
    st.stop()
if _policy == "terms":
    render_terms_of_service()
    st.stop()

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
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        st.image(logo_path.read_bytes(), width="stretch")
else:
    st.warning("Logo file not found: puppy-fosters-logo.png")
    st.markdown(
        "<div class='pfpa-brand-title'>Puppy Fosters - Algarve</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="pfpa-brand-title">Supporter Application</div>
    <div class="pfpa-brand-subtitle">Adoption · Fostering · Volunteering</div>
    """,
    unsafe_allow_html=True,
)

_policy_link_bar()



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
DOCUMENT_BUCKET = "dog-documents"
QUESTIONNAIRE_PATH = Path(__file__).resolve().parent / "PFPA Adoption Questionnaire EN.pdf"


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
    st.error("This application form is not configured yet. Please contact Puppy Fosters - Algarve.")
    st.stop()

if not TURNSTILE_SITE_KEY or not TURNSTILE_SECRET_KEY:
    st.error("Secure human verification is not configured yet. Please contact Puppy Fosters - Algarve.")
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
    if not token:
        return False, ["missing-input-response"]
    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": TURNSTILE_SECRET_KEY, "response": token},
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException:
        return False, ["internal-error"]

    if not result.get("success"):
        return False, result.get("error-codes") or ["verification-failed"]
    if result.get("action") not in (None, "", "supporter_application"):
        return False, ["action-mismatch"]
    return True, []


def _send_email(to_address, subject, body):
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


def _clean(value):
    return " ".join(str(value or "").strip().split())


def _clean_email(value):
    return _clean(value).lower()


def _valid_email(value):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", _clean_email(value)))


def _make_reference():
    return f"PFA-{datetime.now():%Y%m%d}-{secrets.token_hex(3).upper()}"


def _safe_filename(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(name or "questionnaire.pdf")).strip("-") or "questionnaire.pdf"


def _load_invite(token):
    if not token:
        return None
    rows = (
        supabase.table("Supporter_Invite")
        .select("*")
        .eq("Token", token)
        .eq("Active", True)
        .limit(1)
        .execute()
        .data
        or []
    )
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


def _dog(dog_id):
    if not dog_id:
        return None
    rows = (
        supabase.table("V2_Dog")
        .select("Dog_ID,Name,Status,Active,is_deleted")
        .eq("Dog_ID", int(dog_id))
        .eq("Active", True)
        .eq("is_deleted", False)
        .limit(1)
        .execute()
        .data
        or []
    )
    return rows[0] if rows else None


def _current_adoption(dog_id):
    if not dog_id:
        return None
    rows = (
        supabase.table("V2_Dog_Adoption")
        .select("Dog_Adoption_ID,Dog_ID,Supporter_ID,Status,End_Date")
        .eq("Dog_ID", int(dog_id))
        .is_("End_Date", "null")
        .in_("Status", ["Trial", "Adopted"])
        .limit(1)
        .execute()
        .data
        or []
    )
    return rows[0] if rows else None


def _dog_accepts_adoption_requests(dog):
    if not dog:
        return False
    if not dog.get("Active") or dog.get("is_deleted"):
        return False
    if str(dog.get("Status") or "").strip().lower() in {"adopted", "trial"}:
        return False
    return _current_adoption(dog.get("Dog_ID")) is None


QUESTIONNAIRE_PROFILE_MAP = {
    "household": "Household",
    "children": "Children",
    "current_pets": "Current_Pets",
    "house_type": "House_Type",
    "rent_own": "Rent_Own",
    "private_outdoor": "Private_Outdoor",
    "outdoor_description": "Outdoor_Description",
    "dog_experience": "Dog_Experience",
    "exercise_training": "Exercise_Training",
    "preventative_care": "Preventative_Care",
    "schedule_alone": "Schedule_Alone",
    "sleep_arrangements": "Sleep_Arrangements",
    "vacation_plans": "Vacation_Plans",
    "travel_petsitting": "Travel_Petsitting",
    "future_changes": "Future_Changes",
    "completed_by": "Questionnaire_Completed_By",
    "completed_at": "Questionnaire_Completed_At",
}


def _questionnaire_invite_context(invite):
    if str(invite.get("Invite_Purpose") or "") == "Adoption Contract":
        return None, None
    app_id = invite.get("Adoption_Application_ID")
    if not app_id:
        return None, None
    apps = (
        supabase.table("V2_Adoption_Application")
        .select("*")
        .eq("Adoption_Application_ID", int(app_id))
        .limit(1).execute().data or []
    )
    if not apps:
        return None, None
    app = apps[0]
    supporters = (
        supabase.table("V2_Supporter")
        .select("*")
        .eq("Supporter_ID", int(app["Supporter_ID"]))
        .eq("is_deleted", False)
        .limit(1).execute().data or []
    )
    return app, (supporters[0] if supporters else None)



CONTRACT_TEMPLATE = Path(__file__).resolve().parent / "assets" / "BlankAdoptionContract.pdf"
CONTRACT_TERMS = [
    "I agree to keep an identification tag attached to a properly fitted collar which will remain on the adopted animal at all times, whether inside or outside of the house, and to obtain all necessary local licences including microchipping.",
    "I agree to have the dog sterilised at the appropriate age as advised by my veterinary surgeon and to provide proof of sterilisation to Puppy Fosters - Algarve on request.",
    "I agree to provide the adopted dog with necessary vaccinations at the intervals advised by my veterinary surgeon.",
    "I agree to have the adopted dog under my control when it is not within the confines of my property. The adopted dog will not be tied or chained.",
    "If for any reason I cannot keep the adopted dog, I agree to notify Puppy Fosters - Algarve and return the adopted dog upon request. The dog shall not be sold on or used for purposes other than as a family pet.",
    "I agree to properly care for the dog, provide adequate food, water, training and sufficient exercise for optimum health, and consult a veterinary surgeon in the case of sickness, injury or accident and carry out necessary treatment.",
    "I agree not to abuse or neglect the adopted dog.",
    "I understand that the dog covered by this adoption agreement is, as far as can reasonably be determined, in good health and that Puppy Fosters - Algarve is not responsible for medical fees incurred after the adoption date.",
    "With effect from the date and time of signature of this adoption agreement, I accept and assume full and sole responsibility for the care, custody, control, supervision and welfare of the dog, including related liability, whether or not the microchip/SIAC registration has by then been transferred into my name.",
    "I understand that failure to perform the foregoing agreement constitutes a breach of contract and may result in Puppy Fosters - Algarve reclaiming possession of the adopted dog.",
    "I will not euthanise the dog without contacting Puppy Fosters - Algarve except where an emergency veterinary surgeon considers euthanasia necessary to end suffering.",
    "I agree to provide Puppy Fosters - Algarve with an update on how the adopted dog is doing during the two weeks following adoption.",
    "I understand that a €90 adoption donation is requested.",
]


def _contract_invite_context(invite):
    if str(invite.get("Invite_Purpose") or "") != "Adoption Contract":
        return None, None
    app_id = invite.get("Adoption_Application_ID")
    if not app_id:
        return None, None
    apps = (
        supabase.table("V2_Adoption_Application").select("*")
        .eq("Adoption_Application_ID", int(app_id)).limit(1).execute().data or []
    )
    if not apps:
        return None, None
    app = apps[0]
    supporters = (
        supabase.table("V2_Supporter").select("*")
        .eq("Supporter_ID", int(app["Supporter_ID"]))
        .eq("is_deleted", False).limit(1).execute().data or []
    )
    return app, (supporters[0] if supporters else None)


def _current_foster_supporter_public(dog_id):
    rows = (
        supabase.table("V2_Dog_Foster").select("Supporter_ID,Start_Date,End_Date")
        .eq("Dog_ID", int(dog_id)).is_("End_Date", "null")
        .order("Start_Date", desc=True).limit(1).execute().data or []
    )
    if not rows:
        return {}
    supporters = (
        supabase.table("V2_Supporter").select("*")
        .eq("Supporter_ID", int(rows[0]["Supporter_ID"]))
        .eq("is_deleted", False).limit(1).execute().data or []
    )
    return supporters[0] if supporters else {}


def _person_name(person):
    return " ".join(
        x for x in [person.get("First_Name"), person.get("Last_Name")]
        if str(x or "").strip()
    ).strip()


def _contract_pdf_bytes(app, supporter, dog, foster, adoption_date, adopter_signature, issuer):
    if not CONTRACT_TEMPLATE.exists():
        raise RuntimeError("The adoption contract template is unavailable. Please contact Puppy Fosters - Algarve.")
    reader = PdfReader(str(CONTRACT_TEMPLATE))
    writer = PdfWriter()
    writer.append(reader)
    fields = reader.get_fields() or {}
    def digits(v): return re.sub(r"\D", "", str(v or ""))
    def phone_code(v):
        d=digits(v)
        return f"+{d}" if d else ""
    def fmt_date(v):
        try:
            return date.fromisoformat(str(v)[:10]).strftime("%d %b %Y")
        except Exception:
            return str(v or "")
    values = {
        "date_of_adoption": fmt_date(adoption_date),
        "foster_carer_name": _person_name(foster),
        "foster_carer_address": foster.get("Address") or "",
        "foster_carer_country": foster.get("Country") or "",
        "foster_carer_phone_code": phone_code(foster.get("Phone_Code")),
        "foster_carer_phone_number": digits(foster.get("Phone_Number")),
        "dog_name": dog.get("Name") or "",
        "dog_sex": dog.get("Gender") or "",
        "dog_dob": fmt_date(dog.get("Date_of_Birth")),
        "dog_chip_no": dog.get("Microchip_Number") or "",
        "dog_description": dog.get("Colour_Description") or "",
        "adopter_name": _person_name(supporter),
        "adopter_address": supporter.get("Address") or "",
        "adopter_country": supporter.get("Country") or "",
        "adopter_phone_code": phone_code(supporter.get("Phone_Code")),
        "adopter_phone_number": digits(supporter.get("Phone_Number")),
        "adopter_email": supporter.get("Email") or "",
        "foster_carer_signature": f"Electronically approved by {issuer}" if issuer else "Puppy Fosters - Algarve",
        "adopter_signature": f"Electronically signed by {adopter_signature}",
        "foster_carer_sign_date": fmt_date(date.today().isoformat()),
        "adopter_sign_date": fmt_date(date.today().isoformat()),
    }
    form_values = {k:("" if values.get(k) in (None,"") else str(values.get(k))) for k in fields if k in values}
    for page in writer.pages:
        writer.update_page_form_field_values(page, form_values)
    buf=io.BytesIO(); writer.write(buf); return buf.getvalue()


def _save_contract_submission(pending):
    app_id=int(pending["adoption_application_id"]); supporter_id=int(pending["supporter_id"]); dog_id=int(pending["dog_id"])
    apps=(supabase.table("V2_Adoption_Application").select("*").eq("Adoption_Application_ID",app_id).limit(1).execute().data or [])
    if not apps: raise RuntimeError("The adoption application could not be found.")
    app=apps[0]
    supporters=(supabase.table("V2_Supporter").select("*").eq("Supporter_ID",supporter_id).limit(1).execute().data or [])
    dogs=(supabase.table("V2_Dog").select("*").eq("Dog_ID",dog_id).limit(1).execute().data or [])
    if not supporters or not dogs: raise RuntimeError("The adopter or dog record could not be found.")
    supporter=supporters[0]; dog=dogs[0]; foster=_current_foster_supporter_public(dog_id)
    now=datetime.now(timezone.utc).isoformat()
    # Keep supporter contract contact information current.
    supabase.table("V2_Supporter").update({
        "Address": pending["address"], "Country": pending["country"],
        "Phone_Code": pending["phone_code"], "Phone_Number": pending["phone_number"],
        "Email": pending["email"], "Updated_By": "Public adoption contract", "Updated_At": now,
    }).eq("Supporter_ID",supporter_id).execute()
    supporter.update({"Address":pending["address"],"Country":pending["country"],"Phone_Code":pending["phone_code"],"Phone_Number":pending["phone_number"],"Email":pending["email"]})
    pdf_bytes=_contract_pdf_bytes(app,supporter,dog,foster,pending["adoption_date"],pending["signed_name"],pending.get("issued_by"))
    filename=f"{dog.get('Name') or 'Dog'}-Adoption-Contract-Signed-{date.today().isoformat()}.pdf"
    path=f"v2/supporters/{supporter_id}/adoption-applications/{app_id}/{secrets.token_hex(8)}-{_safe_filename(filename)}"
    supabase.storage.from_(DOCUMENT_BUCKET).upload(path=path,file=pdf_bytes,file_options={"content-type":"application/pdf","cache-control":"3600","upsert":"false"})
    try:
        rows=supabase.table("V2_Supporter_Document").insert({
            "Supporter_ID":supporter_id,"Role_Type":"Adopter","Document_Type":"Adoption Contract - Signed",
            "File_Name":filename,"Storage_Path":path,"Mime_Type":"application/pdf",
            "Notes":"Electronically signed online via the Puppy Fosters - Algarve public contract form.",
            "Dog_ID":dog_id,"Adoption_Application_ID":app_id,"Uploaded_By":"Public adoption contract",
        }).execute().data or []
        if not rows: raise RuntimeError("The signed contract document index was not created.")
        doc_id=int(rows[0]["Supporter_Document_ID"])
    except Exception:
        try: supabase.storage.from_(DOCUMENT_BUCKET).remove([path])
        except Exception: pass
        raise
    supabase.table("V2_Adoption_Application").update({
        "Contract_Document_ID":doc_id,"Contract_Signed_Date":date.today().isoformat(),
        "Status":"Contract Signed","Updated_By":"Public adoption contract","Updated_At":now,
    }).eq("Adoption_Application_ID",app_id).execute()
    supabase.table("Supporter_Invite").update({
        "Use_Count":int(pending.get("invite_use_count") or 0)+1,"Active":False,
    }).eq("Invite_ID",int(pending["invite_id"])).execute()
    return filename,pdf_bytes


def _render_contract_form(invite, app, supporter, dog):
    foster=_current_foster_supporter_public(dog["Dog_ID"])
    st.markdown("<div class='pfpa-section'>Adoption contract</div>",unsafe_allow_html=True)
    st.info(
        f"This contract is for **{dog.get('Name') or 'the selected dog'}**. Review the pre-filled details and all contract provisions before electronically signing. A printable signed PDF will be generated automatically after submission."
    )
    st.markdown("#### Contract details")
    st.write(f"**Dog:** {dog.get('Name') or ''} — {dog.get('Gender') or ''}")
    st.write(f"**Microchip:** {dog.get('Microchip_Number') or 'Not recorded'}")
    if foster:
        st.write(f"**Current foster carer / Puppy Fosters contact:** {_person_name(foster)}")
    else:
        st.caption("No current foster carer is recorded; the Foster Carer details on the archived contract will remain blank.")
    with st.form("online_adoption_contract"):
        adoption_date=st.date_input("Adoption / trial commencement date *",value=date.today(),format="DD/MM/YYYY")
        st.markdown("#### Adopter details")
        st.text_input("Name",value=_person_name(supporter),disabled=True)
        address=st.text_area("Address *",value=supporter.get("Address") or "")
        country=st.selectbox("Country *",COUNTRIES,index=COUNTRIES.index(supporter.get("Country")) if supporter.get("Country") in COUNTRIES else (COUNTRIES.index("Portugal") if "Portugal" in COUNTRIES else 0))
        current_code=supporter.get("Phone_Code") or "+351"
        code_display=next((x for x in CALLING_CODES if x.startswith(current_code+" ")), "+351 PT")
        c1,c2=st.columns(2)
        phone_code=c1.selectbox("Country code *",CALLING_CODES,index=CALLING_CODES.index(code_display) if code_display in CALLING_CODES else 0)
        phone_number=c2.text_input("Phone number *",value=supporter.get("Phone_Number") or "")
        email=st.text_input("Email address *",value=supporter.get("Email") or invite.get("Email") or "")
        st.markdown("#### Contract provisions")
        for i,term in enumerate(CONTRACT_TERMS,1): st.markdown(f"**{i}.** {term}")
        st.markdown("#### Data protection and electronic signature")
        st.write(DATA_PROTECTION)
        accept_terms=st.checkbox("I have read and agree to all provisions of this adoption contract. *")
        privacy=st.checkbox("I have read and agree to the Data Protection statement and Privacy Policy. *")
        declaration=st.checkbox("I confirm that the pre-filled details above are accurate and that I intend my typed name below to act as my electronic signature. *")
        signed_name=st.text_input("Electronic signature - type your full name *",value=_person_name(supporter))
        submit=st.form_submit_button("Continue to secure signing",type="primary",width="stretch")
    if submit:
        errors=[]
        for label,val in [("Adoption date",adoption_date),("Address",address),("Country",country),("Phone number",phone_number),("Email",email),("Electronic signature",signed_name)]:
            if not str(val or "").strip(): errors.append(f"{label} is required.")
        if email and not _valid_email(email): errors.append("Please enter a valid email address.")
        if not accept_terms: errors.append("You must accept the adoption contract provisions.")
        if not privacy: errors.append("Data Protection acceptance is required.")
        if not declaration: errors.append("Electronic-signature confirmation is required.")
        if errors:
            for e in errors: st.error(e)
        else:
            st.session_state["pending_contract_submission"]={
                "invite_id":invite["Invite_ID"],"invite_use_count":invite.get("Use_Count") or 0,
                "adoption_application_id":int(app["Adoption_Application_ID"]),"supporter_id":int(supporter["Supporter_ID"]),"dog_id":int(dog["Dog_ID"]),
                "dog_name":dog.get("Name") or "Dog","adoption_date":adoption_date.isoformat(),
                "address":_clean(address),"country":_clean(country),"phone_code":clean_phone_code(phone_code),"phone_number":_clean(phone_number),"email":_clean_email(email),
                "signed_name":_clean(signed_name),"issued_by":invite.get("Created_By") or "Puppy Fosters - Algarve",
            }
            st.rerun()


def _profile_for_supporter(supporter_id):
    rows = (
        supabase.table("V2_Adopter_Profile")
        .select("*")
        .eq("Supporter_ID", int(supporter_id))
        .limit(1).execute().data or []
    )
    return rows[0] if rows else {}


def _pdf_text(value):
    return html.escape(str(value or "").strip()).replace("\n", "<br/>") or "—"


def _questionnaire_pdf_bytes(dog_name, contact, qdata, signed_name, submitted_at):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title=f"Adoption Questionnaire - {dog_name or 'Dog'}",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("PFATitle", parent=styles["Title"], alignment=TA_CENTER, spaceAfter=10)
    h = ParagraphStyle("PFAHead", parent=styles["Heading2"], spaceBefore=8, spaceAfter=5)
    body = styles["BodyText"]
    small = ParagraphStyle("PFASmall", parent=body, fontSize=8.5, leading=10.5)
    story = [
        Paragraph("Puppy Fosters - Algarve", title),
        Paragraph("Adopter's Questionnaire", title),
        Paragraph(f"Dog: <b>{_pdf_text(dog_name)}</b>", body),
        Spacer(1, 5*mm),
        Paragraph("YOUR DETAILS", h),
    ]
    details = [
        ["Name", f"{contact.get('first_name','')} {contact.get('last_name','')}".strip()],
        ["Address", contact.get("address")],
        ["Phone", f"{contact.get('phone_code','')} {contact.get('phone_number','')}".strip()],
        ["Email", contact.get("email")],
    ]
    table = Table([[Paragraph(f"<b>{_pdf_text(a)}</b>", small), Paragraph(_pdf_text(b), small)] for a,b in details], colWidths=[42*mm, 125*mm])
    table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story += [table, Spacer(1, 5*mm), Paragraph("ABOUT YOU, YOUR HOME AND YOUR LIFESTYLE", h)]
    questions = [
        ("Tell us a bit about yourself and your household", "household"),
        ("Do you have children? Ages?", "children"),
        ("Do you currently have pets? What type and ages?", "current_pets"),
        ("Do you live in a house or apartment?", "house_type"),
        ("Do you rent or own?", "rent_own"),
        ("Do you have an enclosed private outdoor space?", "private_outdoor"),
        ("What type of outdoor space do you have, and is it fenced/secure?", "outdoor_description"),
        ("Have you raised a puppy before, or do you have other experience with dogs?", "dog_experience"),
        ("What is your exercise plan for the puppy, and your thoughts about training?", "exercise_training"),
        ("How do you feel about sterilisation, regular vaccines, deworming and flea/tick prevention?", "preventative_care"),
        ("What is your schedule during the day - how long will the puppy be home alone?", "schedule_alone"),
        ("Where will the puppy sleep at night, and stay when no one is home?", "sleep_arrangements"),
        ("Any vacation plans coming up?", "vacation_plans"),
        ("When you travel, where will the puppy be if not travelling with you? Pet-sitting or boarding?", "travel_petsitting"),
        ("If your housing, work, or family situation changes, what would that mean for your dog?", "future_changes"),
    ]
    for label, key in questions:
        value = qdata.get(key)
        if key == "private_outdoor":
            value = "Yes" if value is True else "No" if value is False else ""
        story += [Paragraph(f"<b>{_pdf_text(label)}</b>", small), Paragraph(_pdf_text(value), small), Spacer(1, 3*mm)]
    story += [
        Spacer(1, 3*mm),
        Paragraph("DECLARATION AND ELECTRONIC SIGNATURE", h),
        Paragraph(
            "I confirm that the information provided is complete and accurate and understand that it will be used by Puppy Fosters - Algarve to assess this adoption application. I have read the Privacy Policy.",
            small,
        ),
        Spacer(1, 3*mm),
        Paragraph(f"Electronically signed by: <b>{_pdf_text(signed_name)}</b>", small),
        Paragraph(f"Submitted: <b>{_pdf_text(submitted_at)}</b>", small),
        Spacer(1, 5*mm),
        Paragraph("Puppy Fosters - Algarve | Adopter's Questionnaire", small),
    ]
    doc.build(story)
    return buf.getvalue()


def _save_questionnaire_submission(pending):
    app_id = int(pending["adoption_application_id"])
    supporter_id = int(pending["supporter_id"])
    dog_id = int(pending["dog_id"])
    contact = pending["contact"]
    qdata = pending["questionnaire"]
    now = datetime.now(timezone.utc).isoformat()

    # Contact details are part of the questionnaire and may legitimately update the supporter record.
    supabase.table("V2_Supporter").update({
        "First_Name": contact["first_name"],
        "Last_Name": contact["last_name"],
        "Address": contact["address"],
        "Phone_Code": contact["phone_code"],
        "Phone_Number": contact["phone_number"],
        "Email": contact["email"],
        "Updated_By": "Public questionnaire",
        "Updated_At": now,
    }).eq("Supporter_ID", supporter_id).execute()

    profile_payload = {"Supporter_ID": supporter_id}
    for public_key, db_key in QUESTIONNAIRE_PROFILE_MAP.items():
        profile_payload[db_key] = qdata.get(public_key)
    profile_payload["Notes"] = qdata.get("notes") or None
    supabase.table("V2_Adopter_Profile").upsert(
        profile_payload, on_conflict="Supporter_ID"
    ).execute()

    existing_docs = (
        supabase.table("V2_Supporter_Document")
        .select("Supporter_Document_ID,Storage_Path")
        .eq("Adoption_Application_ID", app_id)
        .eq("Document_Type", "Adoption Questionnaire")
        .order("Uploaded_At", desc=True)
        .limit(1).execute().data or []
    )
    if existing_docs:
        doc_id = int(existing_docs[0]["Supporter_Document_ID"])
    else:
        pdf_bytes = _questionnaire_pdf_bytes(
            pending.get("dog_name"), contact, qdata,
            pending.get("signed_name"), pending.get("submitted_at"),
        )
        filename = f"{pending.get('dog_name') or 'Dog'}-Adoption-Questionnaire-{date.today().isoformat()}.pdf"
        path = f"v2/supporters/{supporter_id}/adoption-applications/{app_id}/{secrets.token_hex(8)}-{_safe_filename(filename)}"
        supabase.storage.from_(DOCUMENT_BUCKET).upload(
            path=path, file=pdf_bytes,
            file_options={"content-type":"application/pdf", "cache-control":"3600", "upsert":"false"},
        )
        try:
            rows = supabase.table("V2_Supporter_Document").insert({
                "Supporter_ID": supporter_id,
                "Role_Type": "Adopter",
                "Document_Type": "Adoption Questionnaire",
                "File_Name": filename,
                "Storage_Path": path,
                "Mime_Type": "application/pdf",
                "Notes": "Completed online via the Puppy Fosters - Algarve public questionnaire.",
                "Dog_ID": dog_id,
                "Adoption_Application_ID": app_id,
                "Uploaded_By": "Public questionnaire",
            }).execute().data or []
            if not rows:
                raise RuntimeError("Questionnaire document index was not created.")
            doc_id = int(rows[0]["Supporter_Document_ID"])
        except Exception:
            try:
                supabase.storage.from_(DOCUMENT_BUCKET).remove([path])
            except Exception:
                pass
            raise

    supabase.table("V2_Adoption_Application").update({
        "Questionnaire_Document_ID": doc_id,
        "Questionnaire_Received_Date": date.today().isoformat(),
        "Status": "Questionnaire Received",
        "Updated_By": "Public questionnaire",
        "Updated_At": now,
    }).eq("Adoption_Application_ID", app_id).execute()

    supabase.table("Supporter_Invite").update({
        "Use_Count": int(pending.get("invite_use_count") or 0) + 1,
        "Active": False,
    }).eq("Invite_ID", int(pending["invite_id"])).execute()


def _render_questionnaire_only_form(invite, app, supporter, dog):
    profile = _profile_for_supporter(supporter["Supporter_ID"])
    st.markdown("<div class='pfpa-section'>Adoption questionnaire</div>", unsafe_allow_html=True)
    st.info(
        f"This questionnaire is for **{dog.get('Name') or 'the selected dog'}**. "
        "Every question is mandatory. Your submitted answers and electronic signature will be stored as a printable PDF in the adoption record."
    )
    with st.form("online_adoption_questionnaire"):
        st.markdown("#### Your details")
        c1, c2 = st.columns(2)
        first_name = c1.text_input("First name *", value=supporter.get("First_Name") or "")
        last_name = c2.text_input("Last name *", value=supporter.get("Last_Name") or "")
        address = st.text_area("Address *", value=supporter.get("Address") or "")
        current_code = supporter.get("Phone_Code") or "+351"
        code_display = next((x for x in CALLING_CODES if x.startswith(current_code + " ")), "+351 PT")
        c1, c2 = st.columns(2)
        phone_code = c1.selectbox("Country code *", CALLING_CODES, index=CALLING_CODES.index(code_display) if code_display in CALLING_CODES else 0)
        phone_number = c2.text_input("Phone number *", value=supporter.get("Phone_Number") or "")
        email = st.text_input("Email address *", value=supporter.get("Email") or invite.get("Email") or "")

        st.markdown("#### About you, your home and your lifestyle")
        household = st.text_area("Tell us a bit about yourself and your household *", value=profile.get("Household") or "")
        children = st.text_area("Do you have children? Ages? *", value=profile.get("Children") or "", placeholder="If none, enter 'None'.")
        current_pets = st.text_area("Do you currently have pets? What type and ages? *", value=profile.get("Current_Pets") or "", placeholder="If none, enter 'None'.")
        house_opts = ["", "House", "Apartment", "Other"]
        current_house = profile.get("House_Type") or ""
        if current_house and current_house not in house_opts: house_opts.insert(1, current_house)
        house_type = st.selectbox("Do you live in a house or apartment? *", house_opts, index=house_opts.index(current_house) if current_house in house_opts else 0)
        own_opts = ["", "Own", "Rent", "Other"]
        current_own = profile.get("Rent_Own") or ""
        if current_own and current_own not in own_opts: own_opts.insert(1, current_own)
        rent_own = st.selectbox("Do you rent or own? *", own_opts, index=own_opts.index(current_own) if current_own in own_opts else 0)
        po = profile.get("Private_Outdoor")
        outdoor_choice = st.selectbox("Do you have an enclosed private outdoor space? *", ["", "Yes", "No"], index=1 if po is True else 2 if po is False else 0)
        outdoor_description = st.text_area("What type of outdoor space do you have, and is it fenced / secure? *", value=profile.get("Outdoor_Description") or "", help="If you have no private outdoor space, state that here.")
        dog_experience = st.text_area("Have you raised a puppy before, or do you have other experience with dogs? Please describe. *", value=profile.get("Dog_Experience") or "")
        exercise_training = st.text_area("What is your exercise plan for the puppy, and your thoughts about training? *", value=profile.get("Exercise_Training") or "")
        preventative_care = st.text_area("How do you feel about sterilisation, regular vaccines, deworming and flea/tick prevention? *", value=profile.get("Preventative_Care") or "")
        schedule_alone = st.text_area("What is your schedule during the day - how long will the puppy be home alone? *", value=profile.get("Schedule_Alone") or "")
        sleep_arrangements = st.text_area("Where will the puppy sleep at night, and stay when no one is home? *", value=profile.get("Sleep_Arrangements") or "")
        vacation_plans = st.text_area("Any vacation plans coming up? *", value=profile.get("Vacation_Plans") or "", placeholder="If none, enter 'None'.")
        travel_petsitting = st.text_area("When you travel, where will the puppy be if not travelling with you? What would you do for pet-sitting or boarding? *", value=profile.get("Travel_Petsitting") or "")
        future_changes = st.text_area("If your housing, work, or family situation changes in the future, what would that mean for your dog? *", value=profile.get("Future_Changes") or "")
        notes = st.text_area("Additional adoption notes (optional)", value=profile.get("Notes") or "")

        st.markdown("#### Data protection and declaration")
        st.write(DATA_PROTECTION)
        consent = st.checkbox("I have read and agree to the Data Protection statement. *")
        declaration = st.checkbox("I confirm that the information supplied is complete and accurate to the best of my knowledge. *")
        signed_name = st.text_input("Electronic signature - type your full name *", value=f"{supporter.get('First_Name','')} {supporter.get('Last_Name','')}".strip())
        submit = st.form_submit_button("Continue to secure submission", type="primary", width="stretch")

    if submit:
        qdata = {
            "household": household, "children": children, "current_pets": current_pets,
            "house_type": house_type, "rent_own": rent_own,
            "private_outdoor": True if outdoor_choice == "Yes" else False if outdoor_choice == "No" else None,
            "outdoor_description": outdoor_description, "dog_experience": dog_experience,
            "exercise_training": exercise_training, "preventative_care": preventative_care,
            "schedule_alone": schedule_alone, "sleep_arrangements": sleep_arrangements,
            "vacation_plans": vacation_plans, "travel_petsitting": travel_petsitting,
            "future_changes": future_changes, "notes": notes,
            "completed_by": signed_name, "completed_at": date.today().isoformat(),
        }
        required = [
            ("First name", first_name), ("Last name", last_name), ("Address", address),
            ("Phone", phone_number), ("Email", email),
            ("Home and household", household), ("Children", children), ("Current pets", current_pets),
            ("House type", house_type), ("Rent / own", rent_own), ("Outdoor description", outdoor_description),
            ("Dog experience", dog_experience), ("Exercise / training", exercise_training),
            ("Preventative care", preventative_care), ("Daily schedule / time alone", schedule_alone),
            ("Sleeping arrangements", sleep_arrangements), ("Vacation plans", vacation_plans),
            ("Travel / pet-sitting", travel_petsitting), ("Future changes", future_changes),
            ("Electronic signature", signed_name),
        ]
        errors = [f"{label} is required." for label, value in required if not _clean(value)]
        if not _valid_email(email): errors.append("Please enter a valid email address.")
        if qdata["private_outdoor"] not in (True, False): errors.append("Private outdoor space must be answered Yes or No.")
        if not consent: errors.append("Data Protection acceptance is required.")
        if not declaration: errors.append("The accuracy declaration is required.")
        if errors:
            for e in errors: st.error(e)
        else:
            st.session_state["pending_questionnaire_submission"] = {
                "invite_id": invite["Invite_ID"],
                "invite_use_count": int(invite.get("Use_Count") or 0),
                "adoption_application_id": int(app["Adoption_Application_ID"]),
                "supporter_id": int(supporter["Supporter_ID"]),
                "dog_id": int(dog["Dog_ID"]),
                "dog_name": dog.get("Name") or "Dog",
                "contact": {
                    "first_name": _clean(first_name), "last_name": _clean(last_name),
                    "address": _clean(address), "phone_code": clean_phone_code(phone_code),
                    "phone_number": _clean(phone_number), "email": _clean_email(email),
                },
                "questionnaire": {k: (_clean(v) if isinstance(v, str) else v) for k,v in qdata.items()},
                "signed_name": _clean(signed_name),
                "submitted_at": datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC"),
            }
            st.session_state["turnstile_version"] = int(st.session_state.get("turnstile_version", 0)) + 1
            st.rerun()


# Show contract success before re-validating the consumed one-use link.
if st.session_state.get("contract_submit_success"):
    dog_name = st.session_state.pop("contract_submit_success")
    st.success("Thank you - your adoption contract has been signed and received.")
    st.markdown(
        f"<div class='pfpa-note'>Your electronically signed adoption contract for <strong>{dog_name}</strong> has been submitted securely. Puppy Fosters - Algarve will contact you about the next step.</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# Show questionnaire success before re-validating the consumed one-use link.
if st.session_state.get("questionnaire_submit_success"):
    dog_name = st.session_state.pop("questionnaire_submit_success")
    st.success("Thank you - your adoption questionnaire has been received.")
    st.markdown(
        f"<div class='pfpa-note'>Your questionnaire for <strong>{dog_name}</strong> has been submitted securely. "
        "Puppy Fosters - Algarve will review it and contact you about the next stage.</div>",
        unsafe_allow_html=True,
    )
    st.stop()


# Show success before re-validating a one-use invitation that has just been consumed.
if st.session_state.get("supporter_submit_success"):
    ref = st.session_state["supporter_submit_success"]
    st.success("Thank you — your application has been received.")
    st.markdown(
        f"""
        <div class="pfpa-note">
        Your reference is <strong>{ref}</strong>.<br><br>
        A member of Puppy Fosters - Algarve will review your information and
        contact you if anything further is required. Submission of this form does not
        itself constitute approval as an adopter, foster or volunteer.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ---------------------------------------------------------------------
# INVITATION GATE - ACCESS REMAINS INVITATION ONLY
# ---------------------------------------------------------------------
invite_token = str(st.query_params.get("invite", "") or "").strip()
invite = _load_invite(invite_token)

if not invite:
    st.info(
        "This application form is available by invitation only. "
        "Please use the link sent to you by Puppy Fosters - Algarve."
    )
    st.stop()

allowed_roles = invite.get("Allowed_Roles") or ROLE_OPTIONS
if isinstance(allowed_roles, str):
    allowed_roles = [allowed_roles]
allowed_roles = [r for r in ROLE_OPTIONS if r in allowed_roles] or ROLE_OPTIONS

invited_dog = _dog(invite.get("Related_Dog_ID"))
if invite.get("Related_Dog_ID") and not invited_dog:
    st.error("The dog linked to this invitation is no longer available. Please contact Puppy Fosters.")
    st.stop()

if invited_dog and not _dog_accepts_adoption_requests(invited_dog):
    st.info(
        f"{invited_dog.get('Name') or 'This dog'} is no longer accepting adoption applications. "
        "The dog already has a current adoption/trial or is otherwise unavailable. "
        "Please contact Puppy Fosters if you would like to discuss another dog."
    )
    st.stop()

questionnaire_application, questionnaire_supporter = _questionnaire_invite_context(invite)
contract_application, contract_supporter = _contract_invite_context(invite)
questionnaire_mode = bool(questionnaire_application)
contract_mode = bool(contract_application)
if invite.get("Adoption_Application_ID") and not questionnaire_mode and not contract_mode:
    st.error("This adoption-workflow link is no longer valid. Please contact Puppy Fosters - Algarve.")
    st.stop()
workflow_application = contract_application if contract_mode else questionnaire_application
workflow_supporter = contract_supporter if contract_mode else questionnaire_supporter
if questionnaire_mode or contract_mode:
    if not invited_dog or int(workflow_application.get("Dog_ID") or 0) != int(invited_dog.get("Dog_ID") or 0):
        st.error("This secure link does not match the adoption application. Please contact Puppy Fosters - Algarve.")
        st.stop()
    if not workflow_supporter or int(workflow_application.get("Supporter_ID") or 0) != int(workflow_supporter.get("Supporter_ID") or 0):
        st.error("The supporter record linked to this secure link could not be found.")
        st.stop()
    if str(workflow_application.get("Status") or "") in {"Rejected", "Withdrawn", "Completed"}:
        st.info("This adoption application is closed. Please contact Puppy Fosters - Algarve if you need assistance.")
        st.stop()
if contract_mode and str(contract_application.get("Status") or "") not in {"Approved", "Contract Pending"}:
    st.info("This adoption contract is no longer awaiting signature. Please contact Puppy Fosters - Algarve if you need assistance.")
    st.stop()


# ---------------------------------------------------------------------
# SECURE SUBMISSION STAGE
# ---------------------------------------------------------------------
contract_pending = st.session_state.get("pending_contract_submission")

if contract_pending:
    st.markdown("<div class='pfpa-section'>Secure contract signing</div>", unsafe_allow_html=True)
    st.info("Your contract has been checked but has not yet been signed and submitted. Complete the Cloudflare security check below.")
    if st.session_state.get("turnstile_error"):
        st.error(st.session_state.pop("turnstile_error"))
    version=int(st.session_state.get("turnstile_version",0)); component_key=f"pfpa_contract_turnstile_{version}"
    turnstile_result=turnstile_component(data={"sitekey":TURNSTILE_SITE_KEY},default={"token":""},on_token_change=lambda:None,key=component_key,width="stretch",height=120)
    turnstile_token=getattr(turnstile_result,"token","") or ""
    if turnstile_token:
        valid_turnstile,_=_verify_turnstile(turnstile_token)
        if not valid_turnstile:
            st.session_state["turnstile_error"]="The security check could not be validated. Please complete it again."
            st.session_state["turnstile_version"]=version+1; st.rerun()
        try:
            filename,pdf_bytes=_save_contract_submission(contract_pending)
            admin_email=_secret("APPLICATION_NOTIFICATION_EMAIL")
            _send_email(admin_email,f"Adoption contract signed - {contract_pending['dog_name']}",(
                f"The online adoption contract has been signed.\n\nDog: {contract_pending['dog_name']}\nAdoption application ID: {contract_pending['adoption_application_id']}\n\nReview it in the private Puppy Fosters - Algarve Applications page."
            ))
            _send_email(contract_pending["email"],f"Puppy Fosters - Algarve - adoption contract signed for {contract_pending['dog_name']}",(
                f"Hello {contract_pending['signed_name']},\n\nThank you. Your electronically signed adoption contract for {contract_pending['dog_name']} has been received securely.\n\nKind regards,\nPuppy Fosters - Algarve"
            ))
            st.session_state.pop("pending_contract_submission",None)
            st.session_state["contract_submit_success"]=contract_pending["dog_name"]
            st.rerun()
        except Exception:
            st.session_state["turnstile_error"]="The security check passed, but the adoption contract could not be saved. Please complete the fresh security check and try again."
            st.session_state["turnstile_version"]=version+1; st.rerun()
    if st.button("← Edit contract",width="stretch"):
        st.session_state.pop("pending_contract_submission",None); st.session_state["turnstile_version"]=version+1; st.rerun()
    st.stop()

questionnaire_pending = st.session_state.get("pending_questionnaire_submission")

if questionnaire_pending:
    st.markdown("<div class='pfpa-section'>Secure submission</div>", unsafe_allow_html=True)
    st.info("Your questionnaire has been checked but has not yet been submitted. Complete the Cloudflare security check below.")
    if st.session_state.get("turnstile_error"):
        st.error(st.session_state.pop("turnstile_error"))
    version = int(st.session_state.get("turnstile_version", 0))
    component_key = f"pfpa_q_turnstile_{version}"
    turnstile_result = turnstile_component(
        data={"sitekey": TURNSTILE_SITE_KEY}, default={"token": ""},
        on_token_change=lambda: None, key=component_key, width="stretch", height=120,
    )
    turnstile_token = getattr(turnstile_result, "token", "") or ""
    if turnstile_token:
        valid_turnstile, _ = _verify_turnstile(turnstile_token)
        if not valid_turnstile:
            st.session_state["turnstile_error"] = "The security check could not be validated. Please complete it again."
            st.session_state["turnstile_version"] = version + 1
            st.rerun()
        try:
            _save_questionnaire_submission(questionnaire_pending)
            admin_email = _secret("APPLICATION_NOTIFICATION_EMAIL")
            _send_email(
                admin_email,
                f"Adoption questionnaire received - {questionnaire_pending['dog_name']}",
                (
                    f"A completed adoption questionnaire has been received.\n\n"
                    f"Dog: {questionnaire_pending['dog_name']}\n"
                    f"Applicant: {questionnaire_pending['contact']['first_name']} {questionnaire_pending['contact']['last_name']}\n"
                    f"Adoption application ID: {questionnaire_pending['adoption_application_id']}\n\n"
                    "Review it in the private Puppy Fosters - Algarve Applications page."
                ),
            )
            _send_email(
                questionnaire_pending["contact"]["email"],
                f"Puppy Fosters - Algarve - questionnaire received for {questionnaire_pending['dog_name']}",
                (
                    f"Hello {questionnaire_pending['contact']['first_name']},\n\n"
                    f"Thank you. We have received your adoption questionnaire for {questionnaire_pending['dog_name']}. "
                    "The Puppy Fosters - Algarve team will review it and contact you about the next stage.\n\n"
                    "Kind regards,\nPuppy Fosters - Algarve"
                ),
            )
            st.session_state.pop("pending_questionnaire_submission", None)
            st.session_state["questionnaire_submit_success"] = questionnaire_pending["dog_name"]
            st.rerun()
        except Exception:
            st.session_state["turnstile_error"] = (
                "The security check passed, but the questionnaire could not be saved. "
                "Please complete the fresh security check and try again."
            )
            st.session_state["turnstile_version"] = version + 1
            st.rerun()
    if st.button("← Edit questionnaire", width="stretch"):
        st.session_state.pop("pending_questionnaire_submission", None)
        st.session_state["turnstile_version"] = version + 1
        st.rerun()
    st.stop()


pending = st.session_state.get("pending_supporter_submission")

if pending:
    st.markdown("<div class='pfpa-section'>Secure submission</div>", unsafe_allow_html=True)
    st.info(
        "Your application details have been checked but have not yet been submitted. "
        "Complete the Cloudflare security check below."
    )

    if st.session_state.get("turnstile_error"):
        st.error(st.session_state.pop("turnstile_error"))

    version = int(st.session_state.get("turnstile_version", 0))
    component_key = f"pfpa_turnstile_{version}"

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
        valid_turnstile, _ = _verify_turnstile(turnstile_token)
        if not valid_turnstile:
            st.session_state["turnstile_error"] = (
                "The security check could not be validated. Please complete it again."
            )
            st.session_state["turnstile_version"] = version + 1
            st.rerun()

        app_id = None
        storage_path = None
        try:
            app_rows = (
                supabase.table("V2_Application")
                .insert(pending["application_payload"])
                .execute()
                .data
                or []
            )
            if not app_rows:
                raise RuntimeError("No application record was created.")
            app_id = int(app_rows[0]["Application_ID"])

            for role in pending["roles"]:
                role_payload = {
                    "Application_ID": app_id,
                    "Role_Type": role,
                    "Status": "Requested",
                    "Role_Data": pending["role_data"].get(role) or {},
                }
                if role == "Adopter" and pending.get("dog_id"):
                    role_payload["Related_Dog_ID"] = int(pending["dog_id"])
                supabase.table("V2_Application_Role").insert(role_payload).execute()

            if "Adopter" in pending["roles"] and pending.get("dog_id"):
                qdata = pending["role_data"].get("Adopter") or {}
                contact = pending["application_payload"].get("Common_Data") or {}
                filename = f"{pending.get('dog_name') or 'Dog'}-Adoption-Questionnaire-{date.today().isoformat()}.pdf"
                pdf_bytes = _questionnaire_pdf_bytes(
                    pending.get("dog_name"), contact, qdata,
                    pending["application_payload"].get("Signed_Name"),
                    datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC"),
                )
                storage_path = f"v2/applications/{app_id}/{secrets.token_hex(8)}-{_safe_filename(filename)}"
                storage = supabase.storage.from_(DOCUMENT_BUCKET)
                storage.upload(
                    path=storage_path, file=pdf_bytes,
                    file_options={"content-type":"application/pdf", "cache-control":"3600", "upsert":"false"},
                )
                supabase.table("V2_Application_Document").insert({
                    "Application_ID": app_id, "Role_Type": "Adopter",
                    "Dog_ID": int(pending["dog_id"]),
                    "Document_Type": "Adoption Questionnaire",
                    "File_Name": filename, "Storage_Path": storage_path,
                    "Mime_Type": "application/pdf",
                }).execute()

            # Consume the invitation only after the V2 application, role rows and
            # any questionnaire have all been stored successfully.
            supabase.table("Supporter_Invite").update({
                "Use_Count": int(pending.get("invite_use_count") or 0) + 1
            }).eq("Invite_ID", pending["invite_id"]).execute()

            admin_email = _secret("APPLICATION_NOTIFICATION_EMAIL")
            review_lines = [
                "A new supporter application has been received.",
                "",
                f"Reference: {pending['reference']}",
                f"Name: {pending['first_name']} {pending['last_name']}",
                f"Roles: {', '.join(pending['roles'])}",
            ]
            if pending.get("dog_name"):
                review_lines.append(f"Dog: {pending['dog_name']}")
            review_lines.append("")
            if PRIVATE_APP_REVIEW_URL:
                review_lines.extend([
                    "Review the application in the secure Puppy Fosters - Algarve administration app:",
                    PRIVATE_APP_REVIEW_URL,
                ])
            else:
                review_lines.append("Please review it in the secure Puppy Fosters - Algarve administration app.")

            notification_sent = _send_email(
                admin_email,
                f"New Puppy Fosters - Algarve supporter application — {pending['reference']}",
                "\n".join(review_lines),
            )

            confirmation_body = (
                f"Hello {pending['first_name']},\n\n"
                "Thank you for your application to Puppy Fosters of Portugal - Algarve.\n"
                f"We have received your application for: {', '.join(pending['roles'])}.\n"
            )
            if pending.get("dog_name"):
                confirmation_body += f"Dog: {pending['dog_name']}.\n"
            confirmation_body += (
                f"\nYour reference is {pending['reference']}.\n\n"
                "A member of the team will review your information and contact you if "
                "anything further is required.\n\n"
                "Submission does not itself constitute approval as an adopter, foster "
                "or volunteer."
            )
            confirmation_sent = _send_email(
                pending["email"],
                f"Puppy Fosters - Algarve application received — {pending['reference']}",
                confirmation_body,
            )

            supabase.table("V2_Application").update({
                "Notification_Sent": bool(notification_sent),
                "Confirmation_Sent": bool(confirmation_sent),
            }).eq("Application_ID", app_id).execute()

            st.session_state.pop("pending_supporter_submission", None)
            st.session_state["supporter_submit_success"] = pending["reference"]
            st.rerun()

        except Exception:
            # Best-effort rollback so a failed secure submission does not leave
            # a half-created application behind.
            try:
                if storage_path:
                    supabase.storage.from_(DOCUMENT_BUCKET).remove([storage_path])
            except Exception:
                pass
            try:
                if app_id:
                    supabase.table("V2_Application").delete().eq("Application_ID", app_id).execute()
            except Exception:
                pass

            st.session_state["turnstile_error"] = (
                "The security check passed, but the application could not be saved. "
                "Please complete the fresh security check and try again."
            )
            st.session_state["turnstile_version"] = version + 1
            st.rerun()

    if st.button("← Edit application", width="stretch"):
        st.session_state.pop("pending_supporter_submission", None)
        st.session_state["turnstile_version"] = version + 1
        st.rerun()

    st.stop()


if contract_mode:
    _render_contract_form(invite, contract_application, contract_supporter, invited_dog)
    st.stop()

if questionnaire_mode:
    _render_questionnaire_only_form(invite, questionnaire_application, questionnaire_supporter, invited_dog)
    st.stop()


st.markdown(
    "<div class='pfpa-note'>You only need to enter your personal details once. "
    "The roles available below are those included in your invitation.</div>",
    unsafe_allow_html=True,
)

default_roles = allowed_roles if len(allowed_roles) == 1 else []

if "Adopter" in allowed_roles and not invited_dog:
    st.error(
        "Adopter applications must be linked to a specific dog. "
        "Please ask Puppy Fosters - Algarve for a dog-specific invitation."
    )
    st.stop()

if invited_dog and "Adopter" in allowed_roles:
    default_roles = list(dict.fromkeys(default_roles + ["Adopter"]))

roles = st.multiselect(
    "How would you like to support us? *",
    allowed_roles,
    default=default_roles,
    help="You can select more than one role if your invitation allows it.",
)

if invited_dog and "Adopter" not in roles:
    st.caption(
        f"This invitation is linked to {invited_dog.get('Name') or 'a specific dog'}. "
        "Keep Adopter selected to continue."
    )
    st.stop()

if not roles:
    st.caption("Select at least one role to continue.")
    st.stop()


# ---------------------------------------------------------------------
# ADOPTION QUESTIONNAIRE
# ---------------------------------------------------------------------
if "Adopter" in roles and invited_dog:
    st.markdown("<div class='pfpa-section'>Adoption questionnaire</div>", unsafe_allow_html=True)
    st.info(
        f"This application is for **{invited_dog.get('Name') or 'the selected dog'}**. "
        "Complete every questionnaire field online below. A printable PDF copy will be generated automatically when you submit."
    )


# ---------------------------------------------------------------------
# APPLICATION FORM
# ---------------------------------------------------------------------
with st.form("supporter_application_form"):
    st.markdown("<div class='pfpa-section'>Your details</div>", unsafe_allow_html=True)
    st.caption(
        "Core contact fields marked * are mandatory. "
        "If you are applying to adopt, every adoption-questionnaire field is mandatory."
    )

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
    email = st.text_input("E-mail *", value=invite.get("Email") or "")
    postcode = st.text_input("Postcode *")
    parish = st.text_input("Parish *")
    country = st.selectbox(
        "Country *",
        COUNTRIES,
        index=COUNTRIES.index("Portugal") if "Portugal" in COUNTRIES else 0,
    )

    address = ""
    if "Adopter" in roles:
        address = st.text_area(
            "Address *",
            help="Required for a dog-specific adoption application and the adoption contract.",
        )

    volunteer_data = {}
    if "Volunteer" in roles:
        st.markdown("<div class='pfpa-section'>Volunteer</div>", unsafe_allow_html=True)
        volunteer_data["interests"] = st.multiselect(
            "Areas of interest (optional)", VOLUNTEER_INTERESTS
        )
        volunteer_data["other_notes"] = st.text_area("Other interest / notes (optional)")

    foster_data = {}
    if "Foster" in roles:
        st.markdown("<div class='pfpa-section'>Foster</div>", unsafe_allow_html=True)
        foster_data["animals"] = st.multiselect("What could you foster? (optional)", FOSTER_ANIMALS)
        foster_data["durations"] = st.multiselect("Availability (optional)", FOSTER_DURATIONS)
        foster_data["experience"] = st.text_area("Experience with dogs/puppies (optional)")
        foster_data["home_description"] = st.text_area("Home / household information (optional)")
        outdoor_choice = st.selectbox("Private outdoor space? (optional)", ["", "Yes", "No"])
        foster_data["private_outdoor"] = (
            True if outdoor_choice == "Yes"
            else False if outdoor_choice == "No"
            else None
        )
        foster_data["notes"] = st.text_area("Fostering notes (optional)")

    adopter_data = {}
    if "Adopter" in roles:
        st.markdown("<div class='pfpa-section'>Adopter questionnaire</div>", unsafe_allow_html=True)
        st.info(
            f"This application is for **{invited_dog.get('Name') or 'the selected dog'}**. "
            "Every questionnaire question below is mandatory. A printable PDF copy will be created automatically from your submitted answers."
        )

        adopter_data["household"] = st.text_area(
            "Tell us about your home and household *"
        )
        adopter_data["children"] = st.text_area(
            "Do you have children? If yes, what ages? *",
            placeholder="If none, enter 'None'.",
        )
        adopter_data["current_pets"] = st.text_area(
            "Do you currently have pets? What type and ages? *",
            placeholder="If none, enter 'None'.",
        )
        adopter_data["house_type"] = st.selectbox(
            "Do you live in a house or apartment? *",
            ["", "House", "Apartment", "Other"],
        )
        adopter_data["rent_own"] = st.selectbox(
            "Do you rent or own? *",
            ["", "Own", "Rent", "Other"],
        )
        private_outdoor_choice = st.selectbox(
            "Do you have an enclosed private outdoor space? *",
            ["", "Yes", "No"],
        )
        adopter_data["private_outdoor"] = (
            True if private_outdoor_choice == "Yes"
            else False if private_outdoor_choice == "No"
            else None
        )
        adopter_data["outdoor_description"] = st.text_area(
            "What type of outdoor space do you have, and is it fenced / secure? *",
            help="If you have no private outdoor space, state that here.",
        )
        adopter_data["dog_experience"] = st.text_area(
            "Have you raised a puppy before, or do you have other experience with dogs? Please describe. *"
        )
        adopter_data["exercise_training"] = st.text_area(
            "What is your exercise plan for the puppy, and your thoughts about training? *"
        )
        adopter_data["preventative_care"] = st.text_area(
            "How do you feel about sterilisation, regular vaccines, deworming and flea/tick prevention? *"
        )
        adopter_data["schedule_alone"] = st.text_area(
            "What is your schedule during the day — how long will the puppy be home alone? *"
        )
        adopter_data["sleep_arrangements"] = st.text_area(
            "Where will the puppy sleep at night, and stay when no one is home? *"
        )
        adopter_data["vacation_plans"] = st.text_area(
            "Any vacation plans coming up? *",
            placeholder="If none, enter 'None'.",
        )
        adopter_data["travel_petsitting"] = st.text_area(
            "When you travel, where will the puppy stay if not travelling with you? "
            "What would you do for pet-sitting or boarding? *"
        )
        adopter_data["future_changes"] = st.text_area(
            "If your housing, work or family situation changes in the future, "
            "what would that mean for your dog? *"
        )
        adopter_data["notes"] = st.text_area("Additional adoption notes (optional)")
        adopter_data["completed_by"] = st.text_input(
            "Questionnaire completed by *",
            value=f"{first_name} {last_name}".strip(),
        )
        adopter_data["completed_at"] = date.today().isoformat()

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

    # The dog may have been adopted after the invitation was issued or while
    # the applicant had the form open, so re-check at submission time.
    if invited_dog and not _dog_accepts_adoption_requests(_dog(invited_dog["Dog_ID"])):
        errors.append(
            f"{invited_dog.get('Name') or 'This dog'} is no longer available for a new adoption application."
        )

    required = [
        ("First name", first_name),
        ("Last name", last_name),
        ("Country code", phone_code),
        ("Phone", phone_number),
        ("E-mail", email),
        ("Postcode", postcode),
        ("Parish", parish),
        ("Country", country),
    ]
    for label, value in required:
        if not _clean(value):
            errors.append(f"{label} is required.")

    if email and not _valid_email(email):
        errors.append("Please enter a valid e-mail address.")

    if "Adopter" in roles:
        if not invited_dog:
            errors.append("An adopter application must be linked to a specific dog.")
        if not _clean(address):
            errors.append("Address is required for an adoption application.")
        adopter_required = [
            ("Home and household", adopter_data.get("household")),
            ("Children", adopter_data.get("children")),
            ("Current pets", adopter_data.get("current_pets")),
            ("House type", adopter_data.get("house_type")),
            ("Rent / own", adopter_data.get("rent_own")),
            ("Outdoor description", adopter_data.get("outdoor_description")),
            ("Dog experience", adopter_data.get("dog_experience")),
            ("Exercise / training", adopter_data.get("exercise_training")),
            ("Preventative care", adopter_data.get("preventative_care")),
            ("Daily schedule / time alone", adopter_data.get("schedule_alone")),
            ("Sleeping arrangements", adopter_data.get("sleep_arrangements")),
            ("Vacation plans", adopter_data.get("vacation_plans")),
            ("Travel / pet-sitting", adopter_data.get("travel_petsitting")),
            ("Future changes", adopter_data.get("future_changes")),
            ("Questionnaire completed by", adopter_data.get("completed_by")),
        ]
        for label, value in adopter_required:
            if not _clean(value):
                errors.append(f"{label} is required for an adoption application.")
        if adopter_data.get("private_outdoor") not in (True, False):
            errors.append("Private outdoor space must be answered Yes or No.")

    if not consent:
        errors.append("Data Protection acceptance is required.")
    if not declaration:
        errors.append("The accuracy declaration is required.")
    if not _clean(signed_name):
        errors.append("Please type your full name as your electronic signature.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        common_data = {
            "first_name": _clean(first_name),
            "last_name": _clean(last_name),
            "email": _clean_email(email),
            "phone_code": clean_phone_code(phone_code),
            "phone_number": _clean(phone_number),
            "postcode": _clean(postcode),
            "parish": _clean(parish),
            "country": _clean(country),
            "address": _clean(address) if "Adopter" in roles else "",
        }

        role_data = {
            "Volunteer": volunteer_data if "Volunteer" in roles else {},
            "Foster": foster_data if "Foster" in roles else {},
            "Adopter": adopter_data if "Adopter" in roles else {},
        }

        reference = _make_reference()
        application_payload = {
            "Invite_ID": invite.get("Invite_ID"),
            "Source": "Online",
            "Status": "New",
            "Requested_Roles": list(roles),
            "Common_Data": common_data,
            "Role_Data": role_data,
            "Applicant_Email": common_data["email"],
            "Reference": reference,
            "Consent_Accepted": True,
            "Declaration_Accepted": True,
            "Signed_Name": _clean(signed_name),
            "Notification_Sent": False,
            "Confirmation_Sent": False,
        }

        st.session_state["pending_supporter_submission"] = {
            "application_payload": application_payload,
            "role_data": role_data,
            "invite_id": invite.get("Invite_ID"),
            "invite_use_count": int(invite.get("Use_Count") or 0),
            "first_name": common_data["first_name"],
            "last_name": common_data["last_name"],
            "email": common_data["email"],
            "roles": list(roles),
            "reference": reference,
            "dog_id": int(invited_dog["Dog_ID"]) if invited_dog else None,
            "dog_name": invited_dog.get("Name") if invited_dog else None,
        }
        st.session_state["turnstile_version"] = int(
            st.session_state.get("turnstile_version", 0)
        ) + 1
        st.rerun()
