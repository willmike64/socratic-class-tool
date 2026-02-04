
import streamlit as st
from dataclasses import dataclass
from typing import List, Dict
import datetime
import firebase_admin
from firebase_admin import credentials, auth, firestore
import json
import requests

st.set_page_config(
    page_title="Opportunity Identification & Evaluation — Socratic Class Tool",
    page_icon="💡",
    layout="wide",
)

# Login
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase_credentials"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()
INSTRUCTOR_EMAILS = ["mwill1003@gmail.com", "michael.williams@wisc.edu"]

db = firestore.client()

INSTRUCTOR_EMAILS = ["mwill1003@gmail.com", "michael.williams@wisc.edu"]

if not st.session_state.authenticated:
    st.markdown("""<style>
        .login-container {text-align: center; padding: 3rem 0;}
        .login-title {font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;}
        .login-subtitle {color: #666; margin-bottom: 2rem;}
    </style>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('💡')
        st.markdown('<div class="login-title">Socratic Class Tool</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Opportunity Identification & Evaluation</div>', unsafe_allow_html=True)
        
        email = st.text_input("📧 Email", placeholder="your.email@wisc.edu")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        if "@wisc.edu" not in email and email:
            st.warning("⚠️ Please use your @wisc.edu email address")
        
        if st.button("Login / Register", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("❌ Please enter both email and password")
            else:
                try:
                    user = auth.get_user_by_email(email)
                    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={st.secrets['FIREBASE_API_KEY']}"
                    resp = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
                    if resp.status_code == 200:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.is_instructor = email in INSTRUCTOR_EMAILS
                        # Load student progress
                        if not st.session_state.is_instructor:
                            doc = db.collection("students").document(email).get()
                            if doc.exists:
                                st.session_state.student_data = doc.to_dict()
                            else:
                                st.session_state.student_data = {"q_idx": 0, "responses": {}}
                        st.rerun()
                    else:
                        st.error("❌ Invalid password")
                except auth.UserNotFoundError:
                    try:
                        auth.create_user(email=email, password=password)
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.is_instructor = email in INSTRUCTOR_EMAILS
                        if not st.session_state.is_instructor:
                            st.session_state.student_data = {"q_idx": 0, "responses": {}}
                            db.collection("students").document(email).set(st.session_state.student_data)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Registration failed: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------------
# Data (paraphrased from the note)
# -----------------------------
QUESTIONS: List[Dict] = [
    {
        "id": 1,
        "section": "Set the stakes",
        "q": "If most startups fail, what parts of the outcome can founders actually control early on — and what parts can’t they control?",
        "hint": "Try separating *external conditions* from *founder behaviors/choices*.",
        "model": [
            "Founders can influence: who is on the team, what problem they chase, how they learn, who they talk to, and how quickly they iterate/pivot.",
            "Founders can’t fully control: macroeconomy, timing, technology readiness, funding climate, and many shocks.",
            "The note argues internal factors (team + early behaviors) often dominate what founders can control."
        ],
        "followups": [
            "Which one founder-controlled choice is most irreversible early?",
            "If you could only ‘de-risk’ one thing before building, what would it be?"
        ],
        "misconceptions": [
            "‘It’s all luck’ (ignores controllable behaviors).",
            "‘A great product sells itself’ (skips market need and distribution reality)."
        ],
        "refs": "Intro + 'Founder Decisions and Behaviors' (pp. 1–2)"
    },
    {
        "id": 2,
        "section": "Concepts",
        "q": "What’s the difference between an *idea* and an *opportunity*?",
        "hint": "An opportunity includes a *market need* + a plausible way to create *superior value*.",
        "model": [
            "An idea is a concept in your head; an opportunity is an idea that plausibly matches a real, meaningful need/want and can be served with a workable resource combination.",
            "Opportunities are ‘hypotheses’ until tested; they’re partly shaped by external conditions + founder knowledge/confidence."
        ],
        "followups": [
            "Give an example of an idea that’s not an opportunity (yet). What evidence is missing?",
            "What would turn it into an opportunity?"
        ],
        "misconceptions": [
            "Treating any cool tech as an opportunity without a customer pain point.",
            "Confusing ‘problem exists’ with ‘my solution is the right one’."
        ],
        "refs": "'Identifying an Opportunity' (p. 2–3)"
    },
    {
        "id": 3,
        "section": "Process",
        "q": "The note says founders rarely have a single lightning-bolt epiphany. If that’s true, what does opportunity identification actually look like in the real world?",
        "hint": "Think: gradual convergence, many small tests, pattern recognition.",
        "model": [
            "A gradual process of exploring multiple directions, learning from conversations/observations, and converging on a sharper hypothesis.",
            "Often starts from observing unmet needs, then refining who has the problem, how they currently cope, and what ‘value’ would mean."
        ],
        "followups": [
            "Why might the epiphany story be appealing — and dangerous?",
            "How does ‘quantity of ideas’ help early on?"
        ],
        "misconceptions": [
            "Waiting for inspiration instead of running a learning process.",
            "Over-investing in polishing the first concept."
        ],
        "refs": "Opportunity identification examples (p. 2–3)"
    },
    {
        "id": 4,
        "section": "Two buckets",
        "q": "Define *opportunity identification* vs *opportunity evaluation*. What’s a concrete activity that belongs in each bucket?",
        "hint": "Identification = forming the hypothesis. Evaluation = testing/reshaping it.",
        "model": [
            "Identification: forming a hypothesis about a market need and a potential value-creating approach (e.g., observing a gap, noticing repeated frustrations).",
            "Evaluation: testing assumptions with external information — customer conversations, willingness-to-pay tests, competitive scans — and iterating.",
            "Concrete examples: Identification → journaling recurring pains you see; Evaluation → 15 customer interviews + a landing page test."
        ],
        "followups": [
            "Which bucket do students usually skip — and why?",
            "What happens if you evaluate ‘solution’ before ‘problem’?"
        ],
        "misconceptions": [
            "Building a prototype = evaluation (it’s not, unless it tests assumptions).",
            "Pitching = evaluation (it can be, but only if you listen and learn)."
        ],
        "refs": "'How Founders Identify and Evaluate Opportunities' (p. 2–3)"
    },
    {
        "id": 5,
        "section": "Avoid a common trap",
        "q": "Why is a *solution orientation* risky in the evaluation phase? What mindset does the note recommend instead?",
        "hint": "Jumping to a solution can shut down learning.",
        "model": [
            "A solution orientation makes founders fall in love with implementation before verifying the underlying need, customer, or willingness to pay.",
            "The recommended mindset is a problem orientation: treat your ‘opportunity’ as a hypothesis and test/iterate before committing."
        ],
        "followups": [
            "What’s an example of a ‘false positive’ you’d get if you asked only solution-friendly questions?",
            "How do you structure questions so they don’t ‘lead the witness’?"
        ],
        "misconceptions": [
            "‘If users like my demo, I’m done.’ (likes ≠ buys; and small samples mislead)."
        ],
        "refs": "'Evaluating an Opportunity' (p. 3)"
    },
    # ---- Behaviors: Network ----
    {
        "id": 6,
        "section": "Behavior: Network",
        "q": "Why would a *diverse* network matter for finding or evaluating opportunities?",
        "hint": "Different people see different problems and have different info.",
        "model": [
            "Diverse networks provide non-overlapping information, perspectives, and access (customers, experts, partners, cofounders).",
            "They help you test blind spots: technical feasibility, market dynamics, regulation, sales cycles, etc."
        ],
        "followups": [
            "If your network is mostly ‘people like you,’ what kinds of opportunities will you systematically miss?",
            "What’s one ‘weak tie’ you could activate this week?"
        ],
        "misconceptions": [
            "Networking = collecting business cards (vs. building learning relationships).",
            "Assuming only investors matter early (customers usually matter more)."
        ],
        "refs": "Table of effective behaviors (p. 5) + Network section (p. 6)"
    },
    {
        "id": 7,
        "section": "Behavior: Network",
        "q": "‘Become your customer’ sounds simple. What does it actually mean, and how can you do it if you’re *not* in the target audience?",
        "hint": "Access + immersion + empathy + repeated contact.",
        "model": [
            "It means integrating into the target audience enough to understand their world: language, routines, constraints, and tradeoffs.",
            "If you aren’t the customer: shadow them, join their communities, work where they work, run structured interviews, and build ongoing access.",
            "Bonus: early customers often come from these relationships."
        ],
        "followups": [
            "What’s the difference between ‘asking opinions’ and ‘studying behavior’?",
            "What would make you confident you’re not projecting your own preferences onto them?"
        ],
        "misconceptions": [
            "Assuming you understand customers because you ‘read about them.’",
            "Equating ‘target audience’ with ‘everyone.’"
        ],
        "refs": "Network section + examples (p. 6–7)"
    },
    # ---- Behaviors: Industry experience ----
    {
        "id": 8,
        "section": "Behavior: Industry Experience",
        "q": "Why might ‘start early’ (even with small experiments) improve someone’s long-run odds as a founder?",
        "hint": "Practice builds judgement, resilience, and pattern recognition.",
        "model": [
            "Repeated ventures build practical know-how: selling, recruiting, pricing, customer discovery, and coping with uncertainty.",
            "It also builds founder identity and expands networks, which can compound over time."
        ],
        "followups": [
            "Is failing early always good? What makes it ‘good failure’ vs just spinning wheels?",
            "What’s a tiny venture you could run in 7 days to learn one skill?"
        ],
        "misconceptions": [
            "Waiting for the ‘perfect’ moment to start.",
            "Believing confidence must come before action."
        ],
        "refs": "Industry Experience section (p. 7–8)"
    },
    {
        "id": 9,
        "section": "Behavior: Industry Experience",
        "q": "When does domain expertise help, and when can it hurt opportunity discovery?",
        "hint": "Expertise reduces assumptions — but can create blinders.",
        "model": [
            "It helps by improving the quality of your initial hypotheses: you know workflows, constraints, and who pays.",
            "It can hurt if it narrows imagination (‘this is how it’s always done’) or leads to overconfidence.",
            "The note flags an experience tradeoff: novices may see fresh opportunities but take longer to validate."
        ],
        "followups": [
            "How can an expert protect against ‘expert blind spots’?",
            "How can a novice compensate for missing domain knowledge?"
        ],
        "misconceptions": [
            "‘Only insiders can win.’ (outsiders sometimes disrupt).",
            "‘I worked in the industry, so I don’t need customer discovery.’"
        ],
        "refs": "Experience tradeoff + domain expertise (p. 4, 8)"
    },
    # ---- Behaviors: Curiosity ----
    {
        "id": 10,
        "section": "Behavior: Curiosity",
        "q": "Why is ‘notice frustrations’ such a powerful opportunity-finding habit? How do you separate a real market problem from a minor annoyance?",
        "hint": "Look for frequency, severity, and willingness to pay.",
        "model": [
            "Opportunities start with problems. Noticing frustrations keeps you close to real pain points.",
            "Separate signal from noise by checking: how often it happens, how costly it is, who else has it, and what they currently do to solve it (including paying)."
        ],
        "followups": [
            "What is a ‘workaround’ and why is it a strong clue?",
            "What’s a frustration you personally have — and what evidence would you need before building?"
        ],
        "misconceptions": [
            "Assuming ‘I’m annoyed’ means ‘a market exists.’",
            "Ignoring B2B pains because they’re less glamorous."
        ],
        "refs": "Curiosity section (p. 9–10)"
    },
    {
        "id": 11,
        "section": "Behavior: Curiosity",
        "q": "‘Question everything’—what are the *most important* things to question in the first 30 days, and how do you avoid analysis paralysis?",
        "hint": "Question the riskiest assumptions first.",
        "model": [
            "Question the core assumptions: problem severity, who the buyer is, willingness to pay, market size reachable, competitive alternatives, and key constraints (regulation/operations).",
            "Avoid paralysis by timeboxing: run small tests, set decision thresholds, and keep learning while moving toward a minimal launch."
        ],
        "followups": [
            "Which assumption, if wrong, kills your venture fastest?",
            "What’s a test that gives you ‘disconfirming evidence’ (not just validation)?"
        ],
        "misconceptions": [
            "Only collecting confirming evidence.",
            "Waiting for certainty before acting."
        ],
        "refs": "Questioning + launch caveat (p. 10–11)"
    },
    # ---- Evidence from the note’s analysis ----
    {
        "id": 12,
        "section": "Evidence & interpretation",
        "q": "In the note’s small sample, which behavior category showed up most consistently among the ‘successful’ founders? Why might that pattern make sense?",
        "hint": "Look at the note’s discussion + exhibit on behavioral characteristics.",
        "model": [
            "The note reports Curiosity-related behaviors were most exclusively common among the successful founders, with Network next.",
            "Interpretation: curiosity drives continuous learning and course-correction; network gives access to customers and complementary perspectives."
        ],
        "followups": [
            "What are the limitations of learning from a small founder sample?",
            "If you were designing a study, what would you want to measure next?"
        ],
        "misconceptions": [
            "Treating correlation as guaranteed causation.",
            "Overgeneralizing from success stories (survivorship bias)."
        ],
        "refs": "Associating behaviors with success + Exhibit 1 (p. 11, 13)"
    },
    # ---- Application ----
    {
        "id": 13,
        "section": "Application",
        "q": "Pick a venture concept (yours or a class example). Design a 7-day ‘opportunity sprint’ that uses *all six* behaviors.",
        "hint": "Make it concrete: who, what, how many, by when.",
        "model": [
            "Example structure:",
            "Day 1: List 15 frustrations + rank by severity/frequency (Notice frustrations).",
            "Day 2: Map who else experiences top 3 pains; find communities (Become your customer).",
            "Day 3–4: 12–15 customer conversations; capture quotes + current workarounds (Question everything).",
            "Day 4: Call 3 domain experts to stress-test feasibility (Diversify network).",
            "Day 5: Build a simple landing page or concierge test; measure signups/preorders (Evaluation).",
            "Day 6: Price test (3 price points) with a subset of respondents (Question everything).",
            "Day 7: Decide: iterate / pivot / kill; write what you learned; choose next experiment (Start early mindset)."
        ],
        "followups": [
            "Where in your plan do you risk ‘leading’ customers? Fix it.",
            "What would you consider strong enough evidence to pivot?"
        ],
        "misconceptions": [
            "Packing too much into a week without clear learning goals.",
            "Doing ‘research’ that doesn’t change decisions."
        ],
        "refs": "Behaviors table + evaluation discussion (p. 3, 5)"
    },
]

INSTRUCTOR_GUIDE_MD = f"""
# Instructor Guide (Socratic Lesson Plan)

**Topic:** Entrepreneurial Opportunity Identification & Evaluation  
**Source:** Paraphrased from *The Start of the Start* (industry note).  
**Class length:** 75–90 minutes (timings below assume 80).  

## Learning goals (what students should walk out able to do)
1. Distinguish **opportunity identification** from **opportunity evaluation**.
2. Explain why opportunities should be treated as **testable hypotheses**.
3. Apply six behaviors (Network / Industry Experience / Curiosity) to design a concrete discovery plan.
4. Spot common founder traps: **solution-first**, **confirmation bias**, and **waiting for certainty**.

## Materials
- Whiteboard or slides
- Sticky notes or an online board
- This Streamlit tool (Student mode + Instructor mode)

## Suggested flow (80 minutes)
**0–8 min — Warm-up**
- Ask Q1 and push students to split controllable vs uncontrollable factors.
- Quick show of hands: “Who has a venture idea right now?”

**8–20 min — Define the terrain**
- Q2–Q5. Don’t lecture definitions; pull them from students.
- Board: two columns — *Identification* vs *Evaluation*.

**20–55 min — Behaviors (walk the ladder)**
- Network: Q6–Q7 (students list 3 diverse contacts + 1 customer community).
- Industry experience: Q8–Q9 (tradeoff debate: insiders vs outsiders).
- Curiosity: Q10–Q11 (students identify “riskiest assumption” for their idea).

**55–70 min — Evidence + synthesis**
- Q12 to surface the note’s pattern (Curiosity & Network).
- Quick critique: limitations, survivorship bias, small sample.

**70–80 min — Application**
- Q13: 7-day opportunity sprint.
- Exit ticket: “What is your single riskiest assumption, and how will you test it in 48 hours?”

## Facilitation moves (Socratic tools)
- **Ask for evidence:** “What would you need to see to believe that?”
- **Ask for a counterexample:** “When would that not be true?”
- **Stress-test assumptions:** “Who pays? Who uses? Who vetoes?”
- **Timebox certainty:** “What can you learn by Friday that changes your next action?”

## Quick rubric for student responses (use in participation / short write-up)
- **Clarity:** identifies customer + problem, not just solution.
- **Testability:** proposes actions that could *disconfirm* the hypothesis.
- **Specificity:** who/what/how many/by when.
- **Behavior coverage:** touches all 6 behaviors at least once.
"""

ANSWER_KEY_MD = """
# Answer Key (high-level)

> These are *exemplar* answers. Reward thoughtful alternatives that are evidence-based.

## Q1 — Controllable vs uncontrollable
- Controllable: team composition, problem selection, learning speed, customer access, experiments, pivot/kill decisions.
- Uncontrollable: macro conditions, timing, some tech readiness, funding environment, shocks.

## Q2 — Idea vs opportunity
- Idea: concept.  
- Opportunity: plausible match between a meaningful need + ability to deliver superior value with feasible resources; still a hypothesis until tested.

## Q3 — Identification is gradual
- Convergence from multiple experiments/conversations/observations; many “near misses” before the final direction.

## Q4 — Identification vs evaluation
- Identification = create the hypothesis (need + who + why).  
- Evaluation = test assumptions externally and iterate (interviews, WTP, competitive scan).

## Q5 — Problem orientation
- Don’t “sell” a solution; test whether the problem is real, urgent, and costly, and whether people will pay to solve it.

## Q6 — Diversify network
- Access to non-overlapping information, customers, partners, cofounders; better assumption-checking.

## Q7 — Become your customer
- Immersion and access (shadowing, communities, repeated conversations). Not just surveys; observe behavior and constraints.

## Q8 — Start early
- Practice builds judgement, resilience, sales/recruiting chops, and compounding networks; small ventures create learning loops.

## Q9 — Domain expertise tradeoff
- Helps: better hypotheses, fewer unknowns, faster validation.  
- Hurts: blinders, overconfidence.  
- Novices can see fresh opportunities but must learn faster.

## Q10 — Notice frustrations
- Problems reveal opportunities. Separate signal by frequency, severity, cost, who else has it, and existing workarounds.

## Q11 — Question everything (without freezing)
- Attack riskiest assumptions first; timebox learning; run small tests; seek disconfirming evidence.

## Q12 — Which behaviors show up most in “successful” founders?
- Curiosity most exclusively common; network next.  
- Interpretation: curiosity → learning/pivoting; network → access to customers and complementary viewpoints.  
- Caveat: small sample; correlation not guaranteed causation.

## Q13 — 7-day opportunity sprint
- A good sprint includes: problem list, customer immersion, interviews, expert calls, a market test (landing page / preorder / concierge), a WTP probe, and a decision rule (iterate/pivot/kill).
"""

# -----------------------------
# Instructor script (talk track)
# -----------------------------
QUESTIONS_BY_ID: Dict[int, Dict] = {q["id"]: q for q in QUESTIONS}

# Base timing assumes an ~80-minute session. The UI scales these durations to your class length.
SCRIPT_STEPS: List[Dict] = [
    {
        "qid": 1,
        "base_min": 7,
        "title": "Set the stakes: control vs. chaos",
        "talk_track": [
            "Open with: “Today we’re not pitching. We’re practicing how founders reduce uncertainty early.”",
            "Quickwrite (60 sec): write 3 things founders can control early + 3 they can’t.",
            "Cold-call 2–3 students; sort answers on the board into two columns.",
            "Bridge: “If we can’t control everything, we need behaviors that increase our odds.”"
        ],
        "board": ["CONTROL (within 30 days)", "CAN'T CONTROL / external"],
        "activity": "1-minute quickwrite + board sorting",
    },
    {
        "qid": 2,
        "base_min": 5,
        "title": "Idea vs. opportunity",
        "talk_track": [
            "Say: “We often treat ‘idea’ and ‘opportunity’ like synonyms. They’re not.”",
            "Ask students to give examples of: a cool idea that is *not* an opportunity (yet), and what evidence is missing.",
            "Push for: customer + pain + value + feasibility, not ‘the app.’"
        ],
        "board": ["IDEA (concept)", "OPPORTUNITY (tested hypothesis)"],
        "activity": "Call-and-response examples",
    },
    {
        "qid": 3,
        "base_min": 5,
        "title": "The myth of the lightning-bolt epiphany",
        "talk_track": [
            "Say: “Most founders describe discovery as a slow convergence, not a single moment.”",
            "Ask for a student story: a decision they reached gradually (career, major, project).",
            "Bridge to entrepreneurship: “Opportunity discovery is pattern recognition + learning loops.”"
        ],
        "board": ["Many small signals → convergence"],
        "activity": "1 story + class debrief",
    },
    {
        "qid": 4,
        "base_min": 6,
        "title": "Two buckets: identification vs. evaluation",
        "talk_track": [
            "Say: “Let’s build two buckets so we stop confusing thinking with testing.”",
            "Have students propose one action for identification and one for evaluation; write them under each column.",
            "Correct gently: “A prototype isn’t evaluation unless it tests a specific assumption.”"
        ],
        "board": ["IDENTIFICATION (form hypothesis)", "EVALUATION (test/reshape)"],
        "activity": "Board sorting with student examples",
    },
    {
        "qid": 5,
        "base_min": 6,
        "title": "Avoid the trap: solution-first thinking",
        "talk_track": [
            "Say: “Founders often fall in love with a solution before they earn the right.”",
            "Mini-exercise (2–3 min): rewrite ‘We will build X…’ into a problem hypothesis: “For [customer], [problem] happens in [context] and costs [time/money/stress].”",
            "Debrief: ask 2 students to read their rewrite; ask the room what assumption is being tested."
        ],
        "board": ["SOLUTION → (rewrite) → PROBLEM HYPOTHESIS"],
        "activity": "2–3 minute rewrite exercise",
    },
    {
        "qid": 6,
        "base_min": 5,
        "title": "Behavior 1: diversify your network",
        "talk_track": [
            "Say: “Diverse networks give you non-overlapping information—especially early.”",
            "Ask: “What do you systematically miss if everyone you ask looks like you?”",
            "Quick task: students write down 3 ‘weak ties’ in different roles they could contact this week."
        ],
        "board": ["Who sees what you don't?"],
        "activity": "60-sec ‘3 weak ties’ list",
    },
    {
        "qid": 7,
        "base_min": 5,
        "title": "Behavior 2: become your customer",
        "talk_track": [
            "Say: “Customer discovery isn’t opinions. It’s understanding behavior, constraints, and tradeoffs.”",
            "Ask: “How do you do this if you aren’t the target user?”",
            "Push for immersion: shadowing, communities, repeated access—not one survey."
        ],
        "board": ["Opinions ≠ behavior", "Access + immersion + repetition"],
        "activity": "Name 1 community or place where your customer ‘hangs out’",
    },
    {
        "qid": 8,
        "base_min": 5,
        "title": "Behavior 3: start early (small experiments)",
        "talk_track": [
            "Say: “Starting early isn’t about being born an entrepreneur. It’s about practice.”",
            "Ask: “What skills compound when you run small ventures?”",
            "Prompt: “What is a tiny experiment you could run in 7 days to learn one key skill?”"
        ],
        "board": ["Practice → judgement + confidence + network"],
        "activity": "1 micro-experiment idea per student",
    },
    {
        "qid": 9,
        "base_min": 5,
        "title": "Behavior 4: gain domain expertise (tradeoffs)",
        "talk_track": [
            "Set up a quick debate: insiders vs. outsiders.",
            "Ask: “When does expertise help? When does it blind you?”",
            "Close with: “Experts should guard against blind spots; novices must learn fast.”"
        ],
        "board": ["Expertise helps… / Expertise hurts…"],
        "activity": "2-minute mini-debate",
    },
    {
        "qid": 10,
        "base_min": 5,
        "title": "Behavior 5: notice frustrations (signal vs noise)",
        "talk_track": [
            "Say: “Problems are the raw material of opportunities.”",
            "Ask: “How do you tell a real market pain from a mild annoyance?”",
            "Introduce a filter: frequency × severity × (evidence of) willingness to pay; look for workarounds."
        ],
        "board": ["Frequency × Severity × WTP", "Workarounds = strong clue"],
        "activity": "Students rank 3 frustrations using the filter",
    },
    {
        "qid": 11,
        "base_min": 5,
        "title": "Behavior 6: question everything (without freezing)",
        "talk_track": [
            "Say: “Questioning is how you find the weak beams—but you still have to move.”",
            "Ask: “Which assumption kills the venture fastest if wrong?”",
            "Timebox: “By Friday, what test could disconfirm your riskiest assumption?”"
        ],
        "board": ["Riskiest assumption → test → decision rule"],
        "activity": "Write 1 kill-shot assumption + 1 test",
    },
    {
        "qid": 12,
        "base_min": 8,
        "title": "Evidence: which behaviors correlate with success (and why)",
        "talk_track": [
            "Say: “The note compares a small set of founders and looks for patterns.”",
            "Ask: “Which behavior category shows up most consistently among the ‘successful’ group?”",
            "Then immediately ask: “What are the limits of learning from small samples and success stories?”"
        ],
        "board": ["Pattern ≠ proof", "Avoid survivorship bias"],
        "activity": "Pattern + critique in the same breath",
    },
    {
        "qid": 13,
        "base_min": 13,
        "title": "Synthesis: design a 7-day opportunity sprint",
        "talk_track": [
            "Say: “Now we convert insight into action. Concrete beats clever.”",
            "In pairs: design a 7-day sprint that uses all six behaviors. Require: who you’ll talk to, how many, and what you’ll test.",
            "Share out 2 plans. For each, ask: “What decision will you make at the end of the week?”",
            "Exit ticket: riskiest assumption + 48-hour test."
        ],
        "board": ["7-day sprint: who / how many / by when", "Decision: iterate / pivot / kill"],
        "activity": "Pairs plan + share-out + exit ticket",
    },
]

def fmt_mmss(minutes_float: float) -> str:
    """Format a float minute value as MM:SS."""
    total_seconds = int(round(minutes_float * 60))
    mm = total_seconds // 60
    ss = total_seconds % 60
    return f"{mm:02d}:{ss:02d}"

def build_timed_script(total_minutes: int) -> List[Dict]:
    """Scale the base 80-minute script to a new total length."""
    base_total = 80.0
    factor = float(total_minutes) / base_total
    out: List[Dict] = []
    start = 0.0
    for step in SCRIPT_STEPS:
        dur = float(step["base_min"]) * factor
        end = start + dur
        out.append({"start": start, "end": end, "step": step})
        start = end
    # Force the final endpoint to match exactly (helps display).
    if out:
        out[-1]["end"] = float(total_minutes)
    return out

def build_script_md(total_minutes: int) -> str:
    """Build a printable Markdown version of the instructor talk track."""
    lines: List[str] = []
    lines.append("# Instructor Script (Talk Track)")
    lines.append("")
    lines.append(f"**Class length:** {total_minutes} minutes (scaled from an 80-minute base plan)")
    lines.append("")
    lines.append("Use this as a flexible talk track. Adapt to your voice and your students.")
    lines.append("")
    timed = build_timed_script(total_minutes)
    for item in timed:
        step = item["step"]
        q = QUESTIONS_BY_ID[step["qid"]]
        header = f"## {fmt_mmss(item['start'])}–{fmt_mmss(item['end'])} — Q{q['id']}: {step['title']}"
        lines.append(header)
        lines.append("")
        lines.append("**Talk track (say/do):**")
        for t in step.get("talk_track", []):
            lines.append(f"- {t}")
        if step.get("board"):
            lines.append("")
            lines.append("**Board / visuals:**")
            for b in step["board"]:
                lines.append(f"- {b}")
        if step.get("activity"):
            lines.append("")
            lines.append(f"**Quick activity:** {step['activity']}")
        lines.append("")
        lines.append("**Ask:**")
        lines.append(f"- {q['q']}")
        if q.get("followups"):
            lines.append("")
            lines.append("**Follow-ups:**")
            for f in q["followups"]:
                lines.append(f"- {f}")
        if q.get("model"):
            lines.append("")
            lines.append("**Listen for (answer elements):**")
            for m in q["model"]:
                lines.append(f"- {m}")
        if q.get("misconceptions"):
            lines.append("")
            lines.append("**Watch out for:**")
            for m in q["misconceptions"]:
                lines.append(f"- {m}")
        lines.append("")
        lines.append(f"*Note pointer:* {q.get('refs','')}")
        lines.append("")
    return "\n".join(lines)


# -----------------------------
# Helpers
# -----------------------------
def md_download_button(label: str, md_text: str, filename: str):
    st.download_button(
        label=label,
        data=md_text.encode("utf-8"),
        file_name=filename,
        mime="text/markdown",
        use_container_width=True
    )

def get_question_by_idx(idx: int) -> Dict:
    return QUESTIONS[idx]

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("💡 Socratic Class Tool")
st.sidebar.caption(f"Logged in as: {st.session_state.user_email}")

with open('/Users/michaelwilliams/Library/Mobile Documents/com~apple~CloudDocs/SchoolFiles/Articles/Start_of_The_Start.pdf', 'rb') as f:
    pdf_data = f.read()
st.sidebar.download_button("📄 Download Article (PDF)", pdf_data, "Start_of_The_Start.pdf", "application/pdf", use_container_width=True)

is_instructor = st.session_state.get("is_instructor", False)

if is_instructor:
    mode = st.sidebar.radio("Mode", ["Student", "Instructor"], index=1)
    page = st.sidebar.radio("Go to", ["Socratic Flow", "Instructor Script", "Student Worksheet", "Instructor Guide", "Answer Key"], index=0)
else:
    mode = "Student"
    page = st.sidebar.radio("Go to", ["Socratic Flow", "Student Worksheet"], index=0)

st.sidebar.caption(f"Built: {datetime.date.today().isoformat()}")

# -----------------------------
# Pages
# -----------------------------
if page == "Socratic Flow":
    st.title("Socratic Flow")
    st.caption("Step through a discussion sequence. Students type answers; Instructor mode shows prompts + exemplar answers.")

    if "q_idx" not in st.session_state:
        st.session_state.q_idx = 0
    total = len(QUESTIONS)
    q = get_question_by_idx(st.session_state.q_idx)

    colA, colB, colC = st.columns([1, 2, 1])
    with colA:
        if st.button("⬅️ Prev", use_container_width=True, disabled=(st.session_state.q_idx == 0)):
            st.session_state.q_idx -= 1
            st.rerun()
    with colC:
        if st.button("Next ➡️", use_container_width=True, disabled=(st.session_state.q_idx == total - 1)):
            st.session_state.q_idx += 1
            st.rerun()

    st.progress((st.session_state.q_idx + 1) / total)
    st.markdown(f"### Q{q['id']}: {q['section']}")
    st.markdown(q["q"])

    with st.expander("💭 Hint (optional)"):
        st.write(q["hint"])

    is_instructor = st.session_state.get("is_instructor", False)
    
    if is_instructor:
        response = st.text_area("Student response (notes):", key=f"resp_{q['id']}", height=140, placeholder="Type what you'd say in class...")
    else:
        default_value = st.session_state.student_data.get("responses", {}).get(str(q['id']), "")
        response = st.text_area("Student response (notes):", value=default_value, height=140, placeholder="Type what you'd say in class...", key=f"student_resp_{q['id']}")
        
        if st.button("💾 Save Progress", type="primary"):
            if "responses" not in st.session_state.student_data:
                st.session_state.student_data["responses"] = {}
            st.session_state.student_data["responses"][str(q['id'])] = response
            db.collection("students").document(st.session_state.user_email).set(st.session_state.student_data)
            st.success("✅ Progress saved!")

    if mode == "Instructor":
        st.markdown("#### Instructor supports")
        with st.expander("✅ Exemplar answer elements"):
            for line in q["model"]:
                st.write(f"- {line}")

        with st.expander("🔁 Follow-up questions"):
            for f in q["followups"]:
                st.write(f"- {f}")

        with st.expander("⚠️ Common misconceptions to surface"):
            for m in q["misconceptions"]:
                st.write(f"- {m}")

        st.caption(f"Where this comes from in the note: {q['refs']}")

    if is_instructor:
        st.divider()
        st.subheader("Quick export")
        md_download_button("Download Instructor Guide (Markdown)", INSTRUCTOR_GUIDE_MD, "instructor_guide.md")
        if mode == "Instructor":
            md_download_button("Download Answer Key (Markdown)", ANSWER_KEY_MD, "answer_key.md")

elif page == "Instructor Script":
    st.title("Instructor Script (Talk Track)")
    st.caption("A facilitation script you can keep open while teaching. Timings scale to your class length.")

    if mode != "Instructor":
        st.warning("Switch to **Instructor** mode in the sidebar to view the talk track.")
    else:
        total_minutes = st.slider("Class length (minutes)", min_value=40, max_value=120, value=80, step=5)
        st.markdown("Use the expanders below as your live talk track. You can also download a printable version.")

        timed = build_timed_script(total_minutes)
        for idx, item in enumerate(timed):
            step = item["step"]
            q = QUESTIONS_BY_ID[step["qid"]]
            label = f"{fmt_mmss(item['start'])}–{fmt_mmss(item['end'])} | Q{q['id']}: {step['title']}"

            with st.expander(label, expanded=(idx == 0)):
                st.markdown("**Talk track (say/do):**")
                for t in step.get("talk_track", []):
                    st.write(f"- {t}")

                if step.get("board"):
                    st.markdown("**Board / visuals:**")
                    for b in step["board"]:
                        st.write(f"- {b}")

                if step.get("activity"):
                    st.markdown(f"**Quick activity:** {step['activity']}")

                st.markdown("**Ask:**")
                st.write(q["q"])

                st.markdown("**Follow-ups:**")
                for f in q.get("followups", []):
                    st.write(f"- {f}")

                st.markdown("**Listen for (answer elements):**")
                for m in q.get("model", []):
                    st.write(f"- {m}")

                st.markdown("**Watch out for:**")
                for m in q.get("misconceptions", []):
                    st.write(f"- {m}")

                st.caption(f"Note pointer: {q.get('refs','')}")

        st.divider()
        script_md = build_script_md(total_minutes)
        md_download_button("Download Script (Markdown)", script_md, "instructor_script.md")
        st.text_area("Full script (copy/paste)", script_md, height=360)

elif page == "Student Worksheet":
    st.title("Student Worksheet — Opportunity Discovery Sprint")
    st.caption("A lightweight worksheet aligned to the six behaviors. Use as an in-class activity or homework template.")

    with st.form("worksheet"):
        st.subheader("1) Opportunity hypothesis")
        customer = st.text_input("Target customer (be specific):", placeholder="e.g., 1st-year grad students in Madison who...")
        problem = st.text_area("Problem / frustration:", height=80, placeholder="What is painful? When does it happen? Why does it matter?")
        workaround = st.text_area("Current workarounds / alternatives:", height=80, placeholder="How do they solve it today (including 'do nothing')?")

        st.subheader("2) Your riskiest assumptions (ranked)")
        a1 = st.text_input("Assumption #1 (highest risk):", placeholder="e.g., People will pay $X/month to avoid Y")
        test1 = st.text_input("Test for #1:", placeholder="e.g., 10 interviews + price prompt; 3 preorders")
        a2 = st.text_input("Assumption #2:", placeholder="e.g., Buyer is the manager, not the user")
        test2 = st.text_input("Test for #2:", placeholder="e.g., Speak with 5 buyers; map decision process")
        a3 = st.text_input("Assumption #3:", placeholder="e.g., We can deliver in <48 hours")
        test3 = st.text_input("Test for #3:", placeholder="e.g., concierge pilot for 3 customers")

        st.subheader("3) Network plan (diversify)")
        st.write("List 5 people you will talk to this week — aim for different backgrounds/roles.")
        contacts = []
        for i in range(1, 6):
            contacts.append(st.text_input(f"Contact {i} (name + role):", placeholder="e.g., Alex — logistics ops manager"))

        st.subheader("4) Become your customer")
        immersion = st.text_area("Where will you ‘hang out’ with your customer (online/offline) this week?", height=80)

        st.subheader("5) Domain expertise")
        know = st.text_area("What do you already know about this domain?", height=80)
        learn = st.text_area("What must you learn fast (and who can teach you)?", height=80)

        st.subheader("6) 7-day plan (Start early)")
        plan = st.text_area("Write a day-by-day plan (7 bullets):", height=140, placeholder="Day 1: ...\nDay 2: ...")

        submitted = st.form_submit_button("Generate download")

    if submitted:
        md = f"""# Opportunity Discovery Worksheet

## Opportunity hypothesis
- **Customer:** {customer}
- **Problem:** {problem}
- **Workarounds / alternatives:** {workaround}

## Riskiest assumptions + tests
1. **Assumption:** {a1}  
   **Test:** {test1}
2. **Assumption:** {a2}  
   **Test:** {test2}
3. **Assumption:** {a3}  
   **Test:** {test3}

## Network plan (diversify)
{chr(10).join([f"- {c}" for c in contacts if c.strip()])}

## Become your customer
{immersion}

## Domain expertise
- **What I know:** {know}
- **What I must learn:** {learn}

## 7-day plan
{plan}
"""
        st.success("Worksheet generated.")
        md_download_button("Download worksheet (Markdown)", md, "opportunity_worksheet.md")
        st.text_area("Preview", md, height=260)

elif page == "Instructor Guide":
    st.title("Instructor Guide")
    st.caption("Ready-to-teach structure using Socratic method prompts.")
    st.markdown(INSTRUCTOR_GUIDE_MD)
    md_download_button("Download Instructor Guide (Markdown)", INSTRUCTOR_GUIDE_MD, "instructor_guide.md")

elif page == "Answer Key":
    st.title("Answer Key")
    if mode != "Instructor":
        st.warning("Switch to **Instructor** mode in the sidebar to view the answer key.")
    else:
        st.markdown(ANSWER_KEY_MD)
        md_download_button("Download Answer Key (Markdown)", ANSWER_KEY_MD, "answer_key.md")

st.sidebar.markdown("---")
st.sidebar.caption("Note: This tool summarizes concepts and prompts discussion. It does not reproduce the original note’s text.")
