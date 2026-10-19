from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="Privacy Policy — PFPA",
    page_icon="🔒",
    layout="centered",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 900px; padding-top: 2.5rem; padding-bottom: 4rem;}
      .pfpa-meta {opacity:.72; margin-bottom:.3rem;}
      .pfpa-policy h1 {margin-top:.1rem;}
      .pfpa-policy h2 {font-size:1.28rem; margin-top:2rem;}
      .pfpa-policy p {line-height:1.62;}
      .pfpa-policy-footer {border-top:1px solid rgba(128,128,128,.35); margin-top:2.2rem; padding-top:1rem; opacity:.72;}
      @media (max-width: 640px) {
        .block-container {padding-left:1rem; padding-right:1rem; padding-top:1.5rem;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)

logo_path = Path(__file__).resolve().parent.parent / "puppy-fosters-logo.png"
if logo_path.exists():
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2:
        st.image(logo_path.read_bytes(), width="stretch")

st.markdown('<div class="pfpa-meta">Puppy Fosters of Portugal - Algarve (PFPA)</div>', unsafe_allow_html=True)
st.title("Privacy Policy")
st.caption("Effective date: 19 October 2026")

st.markdown("""
<div class="pfpa-policy">
<h2>1. About this policy</h2>
<p>Puppy Fosters of Portugal - Algarve (PFPA) operates the PFPA Management System and related invitation-based supporter application services (together, the “Service”). This Privacy Policy explains what personal information the Service processes, why it is processed, how it is protected, and the choices available to users and other individuals whose information is recorded in the Service.</p>
<p>PFPA is the controller of personal data processed for its own rescue, fostering, adoption, volunteer and administrative purposes. Where PFPA acts on behalf of another organisation, the responsibilities of the parties may be defined separately.</p>

<h2>2. Information we process</h2>
<p>The Service may process information about authorised users, supporters, foster carers, adopters, volunteers, applicants, veterinary contacts, donors and other people involved in PFPA activities. Depending on the person and purpose, this may include name, email address, telephone number, address or location information, role and application information, correspondence, notes, documents supplied to PFPA, fostering and adoption history, donation records and other information needed to administer PFPA activities.</p>
<p>The Service also stores information about dogs, including identification, health, veterinary, fostering, adoption, cost, donation and document records. Some of those records can be linked to an identifiable person.</p>

<h2>3. Google sign-in and Google user data</h2>
<p>The PFPA Management System uses Google OAuth solely to authenticate approved users and control access to the private management application. The Google sign-in process may provide PFPA with basic account identity information needed for sign-in, such as a Google account identifier, name, email address and, where supplied by Google, a profile image.</p>
<p>PFPA does not use Google OAuth to read Gmail messages, Google Drive files, Google Calendar data, contacts or other Google account content unless the Service is changed in future and the user is clearly informed and asked to authorise the additional access.</p>
<p>Google user data obtained through OAuth is used only for authentication, account matching, access control, security and administration of the Service. It is not used for advertising, profiling for advertising, or sale to third parties.</p>
<p>PFPA’s use and transfer of information received from Google APIs will adhere to the <a href="https://developers.google.com/terms/api-services-user-data-policy" target="_blank">Google API Services User Data Policy</a>, including the Limited Use requirements.</p>

<h2>4. How we use personal information</h2>
<p>PFPA may use personal information to operate and secure the Service; manage authorised user accounts; process supporter, foster, adopter and volunteer applications; manage fostering and adoption activity; maintain animal health and veterinary records; administer donations, costs and documents; communicate with relevant people; maintain audit and operational records; meet legal, safeguarding, accounting and regulatory obligations; and protect the rights, welfare and safety of people and animals.</p>
<p>PFPA will not use personal information for purposes that are incompatible with the reason it was collected without providing appropriate information and, where required, obtaining consent.</p>

<h2>5. Legal bases under data protection law</h2>
<p>Where the EU General Data Protection Regulation (GDPR) or Portuguese data protection law applies, PFPA will process personal data only where it has an appropriate legal basis. Depending on the circumstances, this may include consent, steps taken at the request of an individual before entering into an agreement, performance of an agreement, compliance with a legal obligation, protection of vital interests, or PFPA’s legitimate interests in operating an animal rescue and adoption service safely and effectively.</p>
<p>Where special-category personal data is exceptionally required, PFPA will identify an additional lawful condition before processing it.</p>

<h2>6. Sharing and service providers</h2>
<p>PFPA may share information internally with authorised staff and volunteers who need it for their role, and externally with veterinary practices, adopters, foster carers, service providers, professional advisers, authorities or other parties where necessary for PFPA activities, safety, legal obligations or the individual’s request.</p>
<p>The Service uses third-party technology providers, including cloud hosting, database, authentication and application-hosting providers. These providers may process data on PFPA’s behalf under their own security and contractual arrangements. Google acts as the authentication provider for Google sign-in. PFPA does not sell personal information.</p>

<h2>7. Storage, security and international transfers</h2>
<p>PFPA applies reasonable technical and organisational measures designed to protect information against unauthorised access, loss, misuse or alteration. Access to the private management system is restricted to approved users and is subject to authentication and role-based controls.</p>
<p>Some technology providers may process or store information outside Portugal or the European Economic Area. Where required, PFPA will rely on an appropriate transfer mechanism or other lawful safeguard.</p>

<h2>8. Retention</h2>
<p>PFPA keeps personal information only for as long as reasonably necessary for the purposes described in this policy, including animal welfare and adoption history, safeguarding, legal, accounting, audit and dispute-resolution needs. Retention periods may therefore vary by record type.</p>
<p>Authentication information linked to an authorised user may be retained while the account remains active and for a reasonable period afterwards where required for security, audit or legal purposes.</p>

<h2>9. Your rights</h2>
<p>Subject to applicable law, individuals may have rights to request access to their personal data, correction of inaccurate information, deletion, restriction of processing, objection to certain processing, portability of information, and withdrawal of consent where consent is the legal basis. Exercising a right may be subject to legal exceptions, including records PFPA must retain for legal, safeguarding, accounting or animal-welfare reasons.</p>
<p>Individuals also have the right to lodge a complaint with the Portuguese data protection authority, Comissão Nacional de Proteção de Dados (CNPD), where applicable.</p>

<h2>10. Google account permissions and deletion requests</h2>
<p>Users can review or revoke permissions granted to the Service through their <a href="https://myaccount.google.com/permissions" target="_blank">Google Account security settings</a>. Revoking Google sign-in permission may prevent further access to the PFPA Management System but does not automatically delete records PFPA is otherwise required or entitled to retain.</p>
<p>Requests concerning access, correction or deletion of personal information can be made through PFPA using the contact route stated below. PFPA will verify the requester’s identity where appropriate before acting on a request.</p>

<h2>11. Cookies and session data</h2>
<p>The Service may use essential cookies, session tokens or similar technologies required for authentication, security and operation of the application. PFPA does not use Google OAuth data for advertising cookies or cross-site advertising profiles.</p>

<h2>12. Changes to this policy</h2>
<p>PFPA may update this Privacy Policy when the Service, legal requirements or data practices change. The current version will be published on the Service website with the date of the latest update.</p>

<h2>13. Contact</h2>
<p>For privacy and data protection questions, requests or complaints, please contact PFPA using the contact details published on the PFPA application homepage. The same public contact route should be maintained alongside this policy so that individuals can contact PFPA without signing in.</p>
</div>
<div class="pfpa-policy-footer">PFPA | Privacy Policy | 19 October 2026</div>
""", unsafe_allow_html=True)

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.page_link("public_app.py", label="Supporter Application", icon="🐾", width="stretch")
with c2:
    st.page_link("pages/Terms_of_Service.py", label="Terms of Service", icon="📄", width="stretch")
