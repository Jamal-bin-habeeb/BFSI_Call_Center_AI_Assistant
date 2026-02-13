"""
Lightweight BFSI Response Engine with Guardrails.

Uses keyword-matching + template system that runs instantly on any machine.
Includes safety checks, out-of-domain rejection, and compliance disclaimers
as required by PRD Section 5.
"""


# ── Guardrails: Out-of-domain / unsafe query detection (PRD §5) ────────────
UNSAFE_KEYWORDS = [
    "hack", "steal", "fraud", "launder", "illegal", "exploit",
    "bypass", "cheat", "fake id", "forge", "counterfeit",
]

OUT_OF_DOMAIN_KEYWORDS = [
    "recipe", "weather", "movie", "sports", "cricket", "football",
    "game", "song", "joke", "travel", "vacation", "dating",
    "politics", "election", "religion",
]

SAFETY_DISCLAIMER = (
    "\n\n⚠️ *Disclaimer: This information is for general guidance only. "
    "Please verify with official bank documents or contact your branch "
    "for the most accurate and up-to-date information. Rates and terms "
    "are subject to change.*"
)

UNSAFE_RESPONSE = (
    "🚫 I'm sorry, but I cannot assist with that request. "
    "This assistant is designed to help with legitimate banking, financial services, "
    "and insurance queries only. If you have a genuine banking concern, "
    "please rephrase your question."
)

OUT_OF_DOMAIN_RESPONSE = (
    "I appreciate your query, but I'm specifically designed to assist with "
    "Banking, Financial Services, and Insurance (BFSI) topics only. "
    "I can help you with:\n"
    "• Loan eligibility & applications\n"
    "• EMI calculations & schedules\n"
    "• Interest rates & charges\n"
    "• Credit card & debit card services\n"
    "• Transactions (UPI, NEFT, RTGS, IMPS)\n"
    "• Insurance policies & claims\n"
    "• Account services & KYC\n"
    "• Grievance redressal\n\n"
    "Please ask a BFSI-related question and I'll be happy to help!"
)


# ── Response templates organized by BFSI category ──────────────────────────
RESPONSE_TEMPLATES = {
    "loan_eligibility": {
        "keywords": ["eligibility", "eligible", "qualify", "criteria", "apply",
                      "application", "loan status", "approval"],
        "response": (
            "Loan eligibility depends on several factors including age (21–60 years), "
            "income stability, credit score (typically 700+), existing obligations, and "
            "employment type. Salaried applicants need a minimum of 2 years' work experience, "
            "while self-employed individuals require 3 years of business continuity. "
            "For a detailed assessment, please provide your income and loan type."
        ),
    },
    "emi": {
        "keywords": ["emi", "installment", "monthly payment", "repayment", "schedule"],
        "response": (
            "EMI (Equated Monthly Installment) is calculated using the formula: "
            "EMI = [P × R × (1+R)^N] / [(1+R)^N – 1], where P = principal, "
            "R = monthly interest rate, and N = tenure in months. "
            "Each installment includes both principal and interest components. "
            "You can use our official EMI calculator for exact figures."
        ),
    },
    "interest_rate": {
        "keywords": ["interest rate", "rate of interest", "roi", "charges",
                      "processing fee", "fee"],
        "response": (
            "Interest rates vary based on your credit profile, loan type, and tenure. "
            "Home loans are typically linked to the repo rate (8.50%–9.25% p.a.). "
            "Processing fees range between 1%–2% of the loan amount plus applicable taxes. "
            "All charges are disclosed in the sanction letter and loan agreement."
        ),
    },
    "credit_score": {
        "keywords": ["credit score", "cibil", "credit rating", "credit history",
                      "credit report"],
        "response": (
            "Credit score is a key indicator of repayment behavior and financial discipline. "
            "A score above 750 is considered excellent and may qualify you for better terms. "
            "Scores below 650 may impact eligibility or attract higher interest rates. "
            "Final approval depends on overall risk evaluation."
        ),
    },
    "documents": {
        "keywords": ["document", "documents", "kyc", "proof", "papers", "paperwork",
                      "required documents"],
        "response": (
            "Standard documents required include: 1) Identity Proof (Aadhaar/PAN), "
            "2) Address Proof (Utility Bill/Passport), 3) Income Proof (Salary Slips/ITR), "
            "4) Bank Statements for the last 6 months. Home loans also require property papers. "
            "Processing typically takes 24 hours to 5 working days."
        ),
    },
    "card": {
        "keywords": ["card", "debit card", "credit card", "block", "lost", "atm",
                      "pin", "cvv"],
        "response": (
            "For debit/credit card services: You can block a lost card immediately via "
            "Mobile Banking → Card Management, by SMS ('BLOCK <last 4 digits>'), or by "
            "calling our 24x7 toll-free helpline. For international transactions, "
            "enable them via Net Banking → Manage Cards → Usage Settings."
        ),
    },
    "transaction": {
        "keywords": ["neft", "rtgs", "imps", "upi", "transfer", "transaction", "payment",
                      "fund transfer", "send money"],
        "response": (
            "Transaction limits vary by mode: UPI — ₹1 Lakh/day (10 txns), "
            "IMPS — ₹5 Lakhs/day, NEFT/RTGS — no limit online (subject to cooling period "
            "for new beneficiaries). UPI and IMPS are 24x7 instant payment systems. "
            "NEFT operates in half-hourly batches; RTGS is real-time for amounts ≥ ₹2 Lakhs."
        ),
    },
    "complaint": {
        "keywords": ["complaint", "grievance", "issue", "problem", "escalat", "ombudsman",
                      "redressal", "not resolved", "unhappy"],
        "response": (
            "Our grievance redressal mechanism: Level 1 — Branch Manager or Customer Care "
            "(response in 7 days). Level 2 — Nodal Officer (response in 10 days). "
            "Level 3 — Principal Nodal Officer. If unresolved for 30 days, "
            "you may approach the RBI Banking Ombudsman."
        ),
    },
    "account": {
        "keywords": ["account", "savings", "current", "balance", "open account",
                      "close account", "statement", "passbook", "mini statement"],
        "response": (
            "We offer Savings, Current, and Fixed Deposit accounts. "
            "Savings account interest rates range from 3.0%–4.0% p.a. "
            "You can open an account online or at any branch with your KYC documents. "
            "For balance inquiries, use Mobile Banking, Net Banking, or SMS Banking."
        ),
    },
    "branch": {
        "keywords": ["branch", "working hours", "timing", "office", "visit", "nearest"],
        "response": (
            "Our branches are open from 10:00 AM to 4:00 PM, Monday to Saturday "
            "(except 2nd and 4th Saturdays and public holidays). "
            "Many services are also available 24x7 through our Mobile Banking app "
            "and Net Banking portal."
        ),
    },
    "prepayment": {
        "keywords": ["prepay", "pre-pay", "foreclose", "close loan", "penalty", "early",
                      "part payment"],
        "response": (
            "Prepayment and foreclosure options are available for most loan types. "
            "Floating rate loans: No prepayment penalty. "
            "Fixed rate loans: Up to 2% penalty if paid within the lock-in period. "
            "Partial prepayments can help reduce your tenure or EMI. "
            "Please check your loan agreement for specific terms."
        ),
    },
    # ── Insurance (PRD §1 scope requirement) ────────────────────────────
    "insurance_policy": {
        "keywords": ["insurance", "policy", "life insurance", "health insurance",
                      "term plan", "premium", "sum assured", "coverage"],
        "response": (
            "We offer a range of insurance products including Term Life Insurance, "
            "Health Insurance, Motor Insurance, and Unit-Linked Plans (ULIPs). "
            "Term plans start from ₹500/month for ₹1 Crore coverage. "
            "Health insurance covers hospitalization, day-care procedures, and pre/post "
            "hospitalization expenses. Please specify which product you'd like details on."
        ),
    },
    "insurance_claim": {
        "keywords": ["claim", "claim status", "file claim", "claim process",
                      "claim settlement", "nominee", "maturity"],
        "response": (
            "To file an insurance claim: 1) Intimate the claim via our toll-free number "
            "or Mobile Banking app within 24 hours. 2) Submit required documents — "
            "Policy document, ID proof, medical reports (for health), FIR (for motor). "
            "3) Claims are typically processed within 30 days of document submission. "
            "Track your claim status online via the 'My Claims' section."
        ),
    },
    "fd_rd": {
        "keywords": ["fixed deposit", "fd", "recurring deposit", "rd", "deposit",
                      "maturity", "premature withdrawal"],
        "response": (
            "Fixed Deposit (FD) interest rates range from 5.5%–7.5% p.a. based on tenure. "
            "Senior citizens get an additional 0.5%. Minimum FD amount is ₹10,000. "
            "Recurring Deposits (RD) start from ₹500/month. "
            "Premature withdrawal may attract a penalty of 0.5%–1% on the applicable rate."
        ),
    },
    "mobile_net_banking": {
        "keywords": ["mobile banking", "net banking", "online banking", "internet banking",
                      "login", "password", "register", "otp"],
        "response": (
            "To register for Mobile/Net Banking: 1) Download our Mobile Banking app "
            "from App Store or Play Store. 2) Register using your account number and "
            "registered mobile number. 3) Set your login PIN/password. "
            "For password reset, use the 'Forgot Password' option or visit your branch. "
            "OTP will be sent to your registered mobile number for verification."
        ),
    },
}

DEFAULT_RESPONSE = (
    "Thank you for your query. I can help with loan eligibility, EMI calculations, "
    "interest rates, credit scores, documentation, card services, transactions, "
    "insurance, account services, and grievance redressal. Could you please provide "
    "more details about what you'd like to know?"
)


class SLMEngine:
    """Lightweight BFSI response engine with safety guardrails."""

    def __init__(self, model_name=None, model_path=None):
        self.model_name = model_name or "template-engine-v2"
        self.model = True  # Flag so callers know engine is "ready"
        self.tokenizer = None

    def load_model(self):
        """No-op — kept for API compatibility with app.py."""
        print("SLM Engine ready (lightweight template mode with guardrails).")

    # ── Guardrails (PRD §5) ─────────────────────────────────────────────
    @staticmethod
    def _is_unsafe(query):
        """Detect potentially unsafe or malicious queries."""
        q = query.lower()
        return any(kw in q for kw in UNSAFE_KEYWORDS)

    @staticmethod
    def _is_out_of_domain(query):
        """Detect queries outside BFSI domain."""
        q = query.lower()
        # Check if it matches ANY BFSI keyword first
        for data in RESPONSE_TEMPLATES.values():
            if any(kw in q for kw in data["keywords"]):
                return False  # It's BFSI-related
        # Then check if it matches out-of-domain keywords
        return any(kw in q for kw in OUT_OF_DOMAIN_KEYWORDS)

    def generate_response(self, prompt, max_new_tokens=200):
        """Match the query against BFSI templates with safety checks."""
        # ── Step 1: Safety Check (PRD §5) ───────────────────────────────
        if self._is_unsafe(prompt):
            return UNSAFE_RESPONSE

        # ── Step 2: Out-of-domain Check (PRD §5) ────────────────────────
        if self._is_out_of_domain(prompt):
            return OUT_OF_DOMAIN_RESPONSE

        query_lower = prompt.lower()

        # ── Step 3: Score each category by keyword matches ──────────────
        best_category = None
        best_score = 0

        for category, data in RESPONSE_TEMPLATES.items():
            score = sum(1 for kw in data["keywords"] if kw in query_lower)
            if score > best_score:
                best_score = score
                best_category = category

        if best_category and best_score > 0:
            response = RESPONSE_TEMPLATES[best_category]["response"]
            return response + SAFETY_DISCLAIMER

        return DEFAULT_RESPONSE


if __name__ == "__main__":
    slm = SLMEngine()
    slm.load_model()

    print("=" * 60)
    print("TEST 1: Normal BFSI query")
    print(slm.generate_response("What are the documents required for a home loan?"))

    print("\n" + "=" * 60)
    print("TEST 2: EMI query")
    print(slm.generate_response("What is the EMI for 10 lakhs?"))

    print("\n" + "=" * 60)
    print("TEST 3: Insurance query")
    print(slm.generate_response("Tell me about health insurance plans"))

    print("\n" + "=" * 60)
    print("TEST 4: Out-of-domain query (should reject)")
    print(slm.generate_response("What's the weather like today?"))

    print("\n" + "=" * 60)
    print("TEST 5: Unsafe query (should reject)")
    print(slm.generate_response("How to hack a bank account?"))

    print("\n" + "=" * 60)
    print("TEST 6: Card query")
    print(slm.generate_response("How do I block my lost debit card?"))
