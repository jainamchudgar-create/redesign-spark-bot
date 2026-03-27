ALL_SPARKS = [
    "Aryan Srivastava",
    "Rahul Kumar",
    "Daniel Nurieli",
    "Samuel Margolis",
    "Adedoyin & Chris",
    "Anmol Narula",
    "Onkar Singh Gujral",
    "Isabelle Gan",
]

# Fill in SLACK_USER_ID for each person before running.
# To find a user's ID: in Slack, click their profile → ... → Copy member ID
EVALUATORS = {
    # ── New Ventures team → Concept Vision ──────────────────────────────────
    "kienan": {
        "name": "Kienan",
        "slack_user_id": "U03HFG3GA5V",
        "email": "kienan.obrien@redesignhealth.com",
        "section": "concept_vision",
        "assigned_sparks": ["Aryan Srivastava", "Isabelle Gan"],
    },
    "neil": {
        "name": "Neil",
        "slack_user_id": "U03U1BQCT27",
        "email": "neil.patel@redesignhealth.com",
        "section": "concept_vision",
        "assigned_sparks": ["Rahul Kumar", "Anmol Narula"],
    },
    "neharika": {
        "name": "Neharika",
        "slack_user_id": "U08LS8QAQGH",
        "email": "neharika.garg@redesignhealth.com",
        "section": "concept_vision",
        "assigned_sparks": [
            "Aryan Srivastava",
            "Daniel Nurieli",
            "Samuel Margolis",
            "Adedoyin & Chris",
            "Onkar Singh Gujral",
            "Isabelle Gan",
        ],
    },
    "aron_dan": {
        "name": "Aron/Dan",
        "slack_user_id": "U0811F0LL8L",
        "email": "aron.szanto@redesignhealth.com",
        "section": "concept_vision",
        "assigned_sparks": ["Daniel Nurieli"],
    },
    "patrick": {
        "name": "Patrick",
        "slack_user_id": "U03BGD55Z6Y",
        "email": "patrick.mcdonagh@redesignhealth.com",
        "section": "concept_vision",
        "assigned_sparks": ["Samuel Margolis", "Adedoyin & Chris"],
    },
    "jorge": {
        "name": "Jorge",
        "slack_user_id": "U08UAHXRRPF",
        "email": "jorge.campos@redesignhealth.com",
        "section": "concept_vision",
        "assigned_sparks": ["Rahul Kumar", "Samuel Margolis"],
    },
    "moz": {
        "name": "Moz",
        "slack_user_id": "U0ALPPVN517",
        "email": "moz.rana@redesignhealth.com",
        "section": "concept_vision",
        "assigned_sparks": ["Samuel Margolis"],
    },
    "akash": {
        "name": "Akash",
        "slack_user_id": "U0823GYJ7K5",
        "email": "akash.lodha@redesignhealth.com",
        "section": "concept_vision",
        "assigned_sparks": ["Anmol Narula", "Isabelle Gan"],
    },
    "preston": {
        "name": "Preston",
        "slack_user_id": "U09UGAXG6GH",
        "email": "preston.tollinger@redesignhealth.com",
        "section": "concept_vision",
        "assigned_sparks": ["Onkar Singh Gujral"],
    },
    # ── Founder Strategy team → Founder DNA ─────────────────────────────────
    "tom": {
        "name": "Tom",
        "slack_user_id": "U0604RVV4R5",
        "email": "tom.skiba@redesignhealth.com",
        "section": "founder_dna",
        "assigned_sparks": ALL_SPARKS,
    },
    "sarah": {
        "name": "Sarah",
        "slack_user_id": "U026G26GK38",
        "email": "sarah.cranston@redesignhealth.com",
        "section": "founder_dna",
        "assigned_sparks": ALL_SPARKS,
    },
    # ── Tech team → Tech / AI-Innateness ────────────────────────────────────
    "dan_tech": {
        "name": "Dan",
        "slack_user_id": "U09MWB7KQSX",
        "email": "dan.costanza@redesignhealth.com",
        "section": "tech",
        "assigned_sparks": ALL_SPARKS,
    },
    "prithvi": {
        "name": "Prithvi",
        "slack_user_id": "U09HN4MAWLD",
        "email": "prithvi.sriram@redesignhealth.com",
        "section": "tech",
        "assigned_sparks": ALL_SPARKS,
    },
    # ── Venture Traction team → Commercial Acumen ────────────────────────────
    "leland": {
        "name": "Leland",
        "slack_user_id": "U05NSUAJFM1",
        "email": "leland.brewster@redesignhealth.com",
        "section": "commercial",
        "assigned_sparks": ALL_SPARKS,
    },
    "matt_ripkey": {
        "name": "Matt Ripkey",
        "slack_user_id": "U0AFBA5810A",
        "email": "matt.ripkey@redesignhealth.com",
        "section": "commercial",
        "assigned_sparks": ALL_SPARKS,
    },
}

SECTION_LABELS = {
    "concept_vision": "Concept Vision",
    "founder_dna": "Founder DNA",
    "tech": "Tech / AI-Innateness",
    "commercial": "Commercial Acumen",
}

RUBRIC = {
    1: {
        "concept_vision": [
            "Can the participant clearly articulate their thesis or area of interest, and what draws them to it?",
            "Have they defined a specific set of research questions and a credible plan to answer them by Week 2?",
            "Does their initial framing suggest an understanding of what makes a problem worth solving in healthcare?",
        ],
        "founder_dna": [
            "Did they come prepared and engage meaningfully with sessions, mentors, and peers?",
            "Do they demonstrate intellectual curiosity — are they asking the right questions, not just the expected ones?",
            "How open are they to feedback and challenge on their initial assumptions (coachability)?",
        ],
        "tech": [
            "Can they articulate what 'AI-native' means in practice — and do they have hands-on familiarity with the tools and stack required to build it?",
        ],
        "commercial": [
            "Do they have an initial working understanding of how to think about go-to-market in healthcare — channels, buyers, and what 'early traction' looks like?",
        ],
    },
    2: {
        "concept_vision": [
            "Have they identified a clearly defined, acute problem — and can they articulate exactly who experiences it and how severely?",
            "Is the problem validated through primary research (customer/user interviews), and how many meaningful conversations have they had?",
            "Are their early market size assumptions (TAM) grounded in evidence, or speculative?",
            "Is the problem space differentiated — why hasn't it been solved already, or why now?",
            "Are there any significant legal, regulatory, or structural barriers to entering this space that they've flagged?",
        ],
        "founder_dna": [
            "Are they going deep on customer discovery or staying at a surface level?",
            "How quickly are they updating their views based on what they're hearing (pivot speed / learning velocity)?",
            "Are they showing genuine curiosity and avoiding confirmation bias in their research?",
            "Any signs of resilience — did they hit dead ends this week, and how did they respond?",
        ],
        "tech": [
            "Are they identifying solutions that are genuinely AI-native (only possible because of AI) vs. simply AI-augmented versions of existing approaches?",
        ],
        "commercial": [],  # No structured touchpoint this week
    },
    3: {
        "concept_vision": [
            "Is the proposed solution clearly differentiated from existing alternatives — have they done a thorough competitive landscape review?",
            "Is the value proposition and ROI specific and compelling? Who captures the value and how?",
            "Is the technical approach feasible and genuinely AI-native, or AI-added?",
            "Have they defined a clear ICP (Ideal Customer Profile) and why that customer buys first?",
            "Is the solution focused and scoped — or are they trying to solve everything at once?",
        ],
        "founder_dna": [
            "Can they communicate the solution clearly and concisely to a non-expert?",
            "Are they incorporating feedback from Week 2 and making smart prioritisation trade-offs?",
            "How are they approaching co-founder or early team considerations for this type of company?",
            "Are they showing founder-market fit — why are they the right person to build this?",
        ],
        "tech": [
            "Have they scoped a credible PoC — can they define what they would build, with what tools, in what timeframe?",
            "Is their proposed solution technically feasible given their own skill set, or are they relying heavily on future hires or partners?",
        ],
        "commercial": [
            "Are they making smart use of ecosystem contacts and warm introductions — are they converting access into real commercial signal?",
        ],
    },
    4: {
        "concept_vision": [
            "Is the go-to-market strategy coherent and realistic for a capital-efficient early stage?",
            "Is the business model clearly defined — revenue logic, pricing, and who pays?",
            "Is the capital plan feasible — how much do they need, for what milestones, and by when?",
            "Have they validated commercial assumptions with real market feedback?",
            "Does the mission and impact framing resonate and differentiate within the broader healthcare landscape?",
        ],
        "founder_dna": [
            "Can they credibly answer 'why am I the founder for this?' — is the narrative compelling?",
            "Have they thought clearly about founding team composition and what gaps need to be filled?",
            "Are they showing maturity in how they handle investor-style questioning and pressure?",
            "Is there evidence of continued resilience and momentum — are they building, not just planning?",
        ],
        "tech": [
            "Are they actively building a PoC or demo — and does the work-in-progress reflect strong independent execution capability?",
            "Do they have a clear, credible view of their infrastructure, cloud, and AI stack choices — and can they defend those decisions technically?",
        ],
        "commercial": [
            "Have their market size and commercial assumptions been stress-tested through real customer-facing conversations — or are they still desk-research estimates?",
            "Is the ICP well-defined and grounded in evidence — do they know exactly who buys first, why, and at what price point?",
        ],
    },
}

# Program week end dates (used for auto-detecting current week)
PROGRAM_WEEKS = {
    1: "2026-03-21",
    2: "2026-03-27",
    3: "2026-04-03",
    4: "2026-04-10",
}
