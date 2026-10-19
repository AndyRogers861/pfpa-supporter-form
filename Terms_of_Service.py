from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="Terms of Service — PFPA",
    page_icon="📄",
    layout="centered",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 900px; padding-top: 2.5rem; padding-bottom: 4rem;}
      .pfpa-meta {opacity:.72; margin-bottom:.3rem;}
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
st.title("Terms of Service")
st.caption("Effective date: 19 October 2026")

st.markdown("""
<div class="pfpa-policy">
<h2>1. About these Terms</h2>
<p>These Terms of Service govern use of the PFPA Management System and related invitation-based PFPA application services (the “Service”), operated by Puppy Fosters of Portugal - Algarve (PFPA). By accessing or using the Service, you agree to these Terms. If you are using the Service on behalf of PFPA or another authorised organisation, you must have authority to do so.</p>

<h2>2. Purpose of the Service</h2>
<p>The Service is provided to support PFPA’s animal rescue, fostering, adoption, volunteer, veterinary, donation and administrative activities. The private management application is intended for approved PFPA users. Public or supporter-facing functions may be restricted to people who receive a valid invitation or authorised link.</p>

<h2>3. Eligibility and accounts</h2>
<p>You must use the Service only if you are authorised to do so. You are responsible for maintaining the security of your account and sign-in method and for promptly reporting suspected unauthorised access.</p>
<p>Google sign-in is used only as an authentication method for the private PFPA Management System. A successful Google sign-in does not itself create a right to use the Service; PFPA may restrict access to approved email addresses, roles or users.</p>

<h2>4. Acceptable use</h2>
<p>You must use the Service lawfully, responsibly and only for legitimate PFPA purposes. You must not attempt to gain unauthorised access; interfere with the Service; introduce malicious code; scrape or extract data without authority; share credentials; access records without a genuine operational need; misuse personal information; or use the Service in a way that could harm people, animals, PFPA, its volunteers or third parties.</p>
<p>Users must respect confidentiality and data protection obligations when viewing, entering, downloading or sharing information from the Service.</p>

<h2>5. Accuracy of information</h2>
<p>Users should take reasonable care to ensure information entered into the Service is accurate, relevant and up to date. PFPA may correct, archive or remove information where necessary for operational, legal, welfare or data-quality reasons.</p>
<p>Animal health, veterinary, adoption and fostering information in the Service is an administrative record and is not a substitute for professional veterinary, legal or other specialist advice.</p>

<h2>6. Documents and user-provided content</h2>
<p>Where the Service allows documents, photographs, forms or other content to be uploaded, you must have authority to provide that content and must not knowingly upload unlawful, misleading, malicious or irrelevant material. PFPA may restrict, remove or archive uploaded material where appropriate.</p>
<p>You retain any rights you have in material you provide, but you grant PFPA permission to store, reproduce and use it as reasonably necessary to operate PFPA activities and the Service.</p>

<h2>7. Privacy and Google OAuth</h2>
<p>Use of personal information is governed by the PFPA Privacy Policy. Google OAuth is used to authenticate approved users and provide basic account identity information required for sign-in and access control. PFPA does not use Google OAuth data for advertising or sell it to third parties.</p>
<p>By using Google sign-in, you also remain subject to Google’s applicable terms and account policies.</p>

<h2>8. Availability and changes</h2>
<p>PFPA aims to keep the Service available and reliable but does not guarantee uninterrupted or error-free operation. The Service may be changed, suspended or temporarily unavailable for maintenance, security, technical or operational reasons.</p>
<p>PFPA may add, modify or remove features where reasonably necessary. Material changes affecting users or personal-data practices will be communicated where appropriate.</p>

<h2>9. Suspension and termination</h2>
<p>PFPA may suspend or terminate access where a user no longer requires access, leaves an authorised role, breaches these Terms, creates a security or privacy risk, or where suspension is otherwise reasonably necessary to protect the Service, PFPA, people or animals.</p>
<p>Users may stop using the Service at any time. Ending access does not automatically require PFPA to delete records that it must or is entitled to retain for legal, accounting, safeguarding, animal-welfare, audit or operational reasons.</p>

<h2>10. Intellectual property</h2>
<p>The Service, its software, branding, documentation and original content are owned by or licensed to PFPA or its respective rights holders. Except as necessary for authorised use of the Service, no licence is granted to copy, modify, distribute or exploit those materials.</p>

<h2>11. Third-party services</h2>
<p>The Service depends on third-party providers such as Google and cloud, database and application-hosting services. PFPA is not responsible for independent third-party services or for outages or changes outside PFPA’s reasonable control. Third-party services may be subject to their own terms and privacy policies.</p>

<h2>12. Liability</h2>
<p>To the extent permitted by law, the Service is provided for PFPA’s operational use without guarantees that it will meet every requirement or be available at all times. PFPA does not exclude or limit liability where doing so would be unlawful, including liability that cannot legally be excluded under applicable consumer, data protection or other mandatory law.</p>
<p>Users remain responsible for professional, welfare and operational decisions and should not rely solely on the Service where independent verification is reasonably required.</p>

<h2>13. Governing law</h2>
<p>These Terms are governed by the laws of Portugal, subject to any mandatory rights or jurisdiction that applicable law gives an individual. Any dispute should first be raised with PFPA so that the parties can try to resolve it informally.</p>

<h2>14. Changes to these Terms</h2>
<p>PFPA may update these Terms when the Service, legal requirements or operating arrangements change. The latest version will be published on the Service website with its effective date. Continued use after an update constitutes acceptance where permitted by law.</p>

<h2>15. Contact</h2>
<p>Questions about these Terms should be sent to PFPA using the contact details published on the PFPA application homepage.</p>
</div>
<div class="pfpa-policy-footer">PFPA | Terms of Service | 19 October 2026</div>
""", unsafe_allow_html=True)

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.page_link("public_app.py", label="Supporter Application", icon="🐾", width="stretch")
with c2:
    st.page_link("pages/Privacy_Policy.py", label="Privacy Policy", icon="🔒", width="stretch")
