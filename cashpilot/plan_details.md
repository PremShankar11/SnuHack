Track 3: Fintech
Context:
Small businesses often make financial decisions based only on their current bank
balance, without a clear view of upcoming obligations, payment timelines, and
trade-offs. As a result, they face avoidable cash shortfalls, delayed payments, and
reactive decision-making. Most existing tools focus on recording and reporting financial
data. They do not assist users in determining what action to take when available cash is
insufficient to meet all upcoming commitments.
Challenge:
Build an semi-autonomous system that models a user’s short-term financial state,
identifies situations where obligations exceed available liquidity, and determines the
most appropriate next action with clear and actionable reasoning.
Scope:
Participants are expected to design and implement a system with the following
capabilities:
● Multi-Source Financial State Modeling: Ingest fragmented financial inputs such
as bank statements , digital invoices, expenses and images(physical/handwritten)
receipts into a normalized structure that includes cash balance, payables, and
receivables.
● Constraint & Runway Detection: Quantify systemic risk identifying scenarios
where upcoming obligations cannot be fully satisfied with available cash.
Compute a time-based liquidity indicator such as days to zero, to provide a
real-time solvency countdown.
● Predictive Decision Engine:  Model each obligation using attributes such as
urgency, risk/penalty, and flexibility. When conflicts arise, the engine must
perform deterministic scenario projections to prioritize obligations and justify
the chosen trade-offs.
● Context-Aware Action Preparation: Translate decisions into ready-to-use outputs
such as payment rescheduling plans or drafted negotiation emails. The strategic
approach and linguistic tone of these drafts must dynamically adapt based on the
specific counterparty relationship profile.
● Explainability & Chain-of-Thought: Provide clear, human-readable COT reasoning
at the decision level. Explanations should justify prioritization and trade-offs
without exposing unnecessary internal complexity.
Evaluation Criteria:
Criteria
Decision Integrity
Strategic Reasoning
Data Robustness
What we look for
logical prioritization of obligations.
Clarity of justifications for chosen trade-offs
and paths.
Extracting handwritten inputs, correlating
various data-sources, identifying duplicates,
etc. sky is your limit.
System Architecture
Actionable Usability
Reliability of techniques used
Constraints and Expectations:
Soundness of system design and separation
between decision logic and AI-assisted output
generation
Ease of reviewing and triggering suggested
actions for non-technical users.
Proven techniques, verifiable outputs, etc.
● Participants are encouraged to use more deterministic systems for projections
and calculations, rather than  relying solely  on LLM-based reasoning.
● Enabling correct and actionable decisions is also appreciated, on top of providing
data visualizations and projections.
● The engine must ideally demonstrate high-fidelity processing of diverse data
formats, including digital transaction records and physical document images.
Innovate beyond these constraints to build a system that transforms financial anxiety into
clarity, turning fragmented obligations into decisive, confident action.

This is a phenomenal hackathon prompt. It correctly identifies a massive flaw in current FinTech tools for small and medium-sized businesses (SMBs): they are **historical** (looking at what happened) rather than **prescriptive** (telling you what to do about what is *going* to happen).

To win this track, you need to prove you understand the difference between **Generative AI** (writing emails, extracting text) and **Deterministic Logic** (math, cash flow routing, hard constraints). The judges explicitly stated they want a hybrid approach.

Here is a comprehensive, revised feature plan. I have taken the core requirements and layered on **"Next Level" Innovations** to turn this from a good hackathon project into a venture-backable product.

---

### **Phase 1: The Core Foundation (Fulfilling the Prompt)**

These are the table-stakes features required to solve the challenge, structured for maximum evaluation points.

**1. Omni-Channel Ingestion Pipeline**

- **What it is:** A pipeline that takes structured data (Plaid/Stripe APIs for bank balances) and unstructured data (photos of receipts, PDF invoices) and standardizes them.
- **Implementation:** * **Tech:** Google Gemini 1.5 Pro (Vision) for extracting line items, dates, and amounts from physical receipts.
    - **Logic:** Output everything into a strict JSON schema: `{entity, amount, due_date, type: "payable" | "receivable", flexibility_rating}`.

**2. The Deterministic "Runway" Engine**

- **What it is:** A pure mathematical model (No LLM hallucinations here) that calculates the exact "Days to Zero" (D2Z) solvency metric.
- **Implementation:** * **Tech:** Python (Pandas/NumPy) or Node.js.
    - **Logic:** A daily compounding ledger. $Balance_{today} = Balance_{yesterday} + \sum Receivables_{today} - \sum Payables_{today}$. If $Balance < 0$, flag a "Liquidity Breach Scenario."

**3. Constraint & Context-Aware Action Generator**

- **What it is:** When a Liquidity Breach is detected, the AI drafts contextually appropriate solutions (e.g., an email asking for an extension).
- **Implementation:** * **Tech:** Gemini API for text generation + Prompt Engineering with strict context variables.
    - **Logic:** If the vendor is a massive corporation (e.g., AWS), the action is "Use credit card." If the vendor is a local supplier, the action is "Draft negotiation email requesting a 15-day extension based on a 3-year loyal relationship."

---

### **Phase 2: "Next Level" Innovations (How to Win)**

To stand out, your system cannot just delay payments (defensive). It must actively manipulate the entire financial chessboard (offensive and defensive).

**4. Bi-Directional Liquidity Solving (The Inflow Accelerator)**

- **The Innovation:** Instead of only figuring out who *not* to pay, the system proactively figures out how to get paid *faster*.
- **How it ties in:** If the engine detects a shortfall on Day 12, it looks at pending *receivables*.
- **Actionable Output:** It automatically drafts an email to a client owing you money: *"Hi [Client], we are offering a dynamic 3% discount if this invoice is settled by Friday instead of next week."*

**5. The Vendor "Goodwill" Scoring Algorithm**

- **The Innovation:** How does the AI know who is "flexible"? You build a Goodwill Score based on historical data.
- **How it ties in:** The system analyzes past ledgers. If you have paid Supplier A exactly on time for 24 months, your "Goodwill Score" with them is 99/100. If you are constantly late with Supplier B, the score is 20/100.
- **Actionable Output:** In a cash crunch, the Deterministic Engine routes the delayed payment to Supplier A, knowing the relationship can absorb the hit, protecting your fragile relationship with Supplier B.

**6. Micro-Financing / Factoring Fallback**

- **The Innovation:** What if "Days to Zero" hits, you have no Goodwill left, and no receivables to accelerate?
- **How it ties in:** Integrate a mock API for short-term invoice factoring (selling your unpaid invoices for immediate cash) or a short-term line of credit.
- **Actionable Output:** "Option 3: Draw $5,000 from Stripe Capital at a 1.5% fee to cover the shortfall. Click here to execute."

**7. Chain-of-Thought (CoT) Audit Trail UI**

- **The Innovation:** Non-technical users won't trust an AI that just says "Don't pay your rent." You need to show the exact math and logic.
- **How it ties in:** A visual timeline showing the exact decision tree.
- **Actionable Output:** A UI card that reads: *"Why this choice? 1. If you pay Rent today, balance drops to -$400 on Tuesday. 2. Your Goodwill Score with Vendor X is High (95). 3. Delaying Vendor X by 4 days prevents overdraft and incurs zero late fees."*

---

### **Phase 3: High-Level Architecture & Tech Stack**

To maintain the "separation between decision logic and AI" required by the prompt, use a **Microservices-lite Architecture**.

- **Frontend (The Action Hub):**
    - *Tech:* Next.js (React), Tailwind CSS, Framer Motion (for smooth UI), and **D3.js / Recharts** for the visual cashflow graphs.
    - *Role:* Displays the "Days to Zero" dashboard, the Action Inbox (approve/reject AI drafted emails), and the visual Chain-of-Thought.
- **The Brain (Backend API):**
    - *Tech:* Python (FastAPI). Python is perfect here because it handles deterministic math (Pandas) and AI/LLM integrations beautifully.
    - *Role:* Houses the routing logic.
- **The Ledger (Database):**
    - *Tech:* PostgreSQL (Supabase or Render).
    - *Role:* Strict relational database for Users, Invoices, Transactions, and Goodwill Scores.
- **The AI Layer:**
    - *Tech:* Gemini 1.5 Pro API.
    - *Role:* 1. **Vision Task:** OCR and classification of handwritten receipts.
        
        2. **NLP Task:** Drafting highly contextual negotiation emails.
        
        3. **Reasoning Task:** Translating the deterministic math outputs into human-readable Chain-of-Thought explanations.
        

---

### **Phase 4: High-Level Implementation Map (Hackathon Timeline)**

**Step 1: The Dummy Data Layer (Crucial for testing)**

- Create a realistic 60-day ledger of transactions for a fake business (e.g., a small design agency). Include predictable expenses (rent, software), variable expenses (freelancers), and incoming client payments. Seed this into your database.

**Step 2: The Math Engine (Deterministic)**

- Write a Python script that ingests the dummy ledger and calculates the daily balance for the next 30 days. Write unit tests to ensure it correctly identifies the exact day the balance drops below zero.

**Step 3: The Optimization Algorithm**

- Write the logic that kicks in when a shortfall is found. It should sort upcoming payables by `(Goodwill Score + Flexibility Rating)` and shift the most flexible ones past the shortfall date until the balance stays positive.

**Step 4: The AI Wrapper (Generative)**

- Connect the output of Step 3 to the LLM. Prompt it: *"The system has mathematically decided to delay Invoice #442 to Acme Corp by 5 days. Draft a polite email to Acme Corp requesting this, noting our 5-year relationship."*

**Step 5: The Frontend & Visuals**

- Build a clean dashboard. The primary view shouldn't be a boring spreadsheet; it should be an "Action Center" that feels like an Inbox. "You have 1 Liquidity Warning. Review AI Action Plan."

---

### **Interactive Concept: The "Runway Sandbox"**

To truly impress the judges, you should let the user *play* with the deterministic engine. Instead of just telling them what to do, let them see the math adapt in real-time.

Here is a conceptual interactive widget demonstrating how your deterministic logic engine would react to user inputs.

Show me the visualization

### **The Winning Pitch Angle**

When you present this, use this framing:

*"Legacy systems tell you that you ran out of money yesterday. Current dashboards tell you that you will run out of money tomorrow. Our system negotiates with your vendors and incentivizes your clients today, so you never run out of money at all."*

---

### **The Revised "Financial Autopilot" Feature Map**

### **Category 1: Advanced Execution (Retained & Refined)**

**1. The Multi-Agent Negotiation Swarm**

- **The Concept:** Instead of just generating an email draft for the user to copy-paste, the system acts as an authorized agent to secure runway.
- **How it Enhances:** If the deterministic engine says, "We need 5 more days to survive this week," the AI agent automatically emails the vendor. It can parse their reply (e.g., "I can only give you 3 days") and check back with the deterministic engine to see if a 3-day extension mathematically prevents the shortfall. If yes, it locks it in.
- **Implementation:** LangChain/AutoGen hooked into the Gmail API, strictly constrained by rules (e.g., "Never negotiate with the IRS, only negotiate with local suppliers").

**2. Automated "Inventory-to-Cash" Liquidation Engine**

- **The Concept:** Solving a cash crunch by creating *new* inflows, not just delaying outflows.
- **How it Enhances:** If "Days to Zero" drops below a critical threshold, the system connects to the user's POS/E-commerce platform, identifies the slowest-moving inventory, and automatically drafts a promotional flash sale to bridge the specific cash gap.
- **Implementation:** Connect to the Shopify or Square API. The deterministic engine calculates exactly how much cash is needed; the AI drafts the Mailchimp email and creates the discount code.

**3. Probabilistic Monte Carlo Modeling (The Reality Check)**

- **The Concept:** Upgrading the deterministic "Days to Zero" countdown with probability.
- **How it Enhances:** In reality, a client who owes you money on the 15th might pay on the 14th, or the 18th. By running thousands of simulations based on historical payment variance, you don't just get a single line graph.
- **Implementation:** Use standard Python libraries (`numpy`).
    - *Actionable Output:* Instead of "You will run out of money on Thursday," the UI displays: *"You have an 82% chance of surviving this week, but an 18% chance of a shortfall due to Client X's historical late payments."*

---

### **Category 2: New High-Impact Core Features**

These new features deeply address the "trade-offs" and "systemic risk" mentioned in the hackathon prompt.

**4. Dynamic Payment Fractionalization (Micro-Installments)**

- **The Concept:** When cash is tight, paying $0 to a vendor damages the relationship, but paying 100% bankrupts you. This feature calculates the perfect middle ground.
- **How it Enhances:** The deterministic engine calculates the exact minimum amount you can pay a vendor to keep them happy without dipping your total balance below zero.
- **Implementation:** * *Logic:* The engine identifies a $5,000 shortfall. It proposes paying Vendor A 30% today and 70% next week.
    - *AI Action:* The AI drafts the communication: *"Hi Vendor A, we are processing a good-faith payment of $1,500 today, with the remaining balance scheduled for next Tuesday."*

**5. Virtual Liability Ring-Fencing (The "Phantom Balance")**

- **The Concept:** A massive reason SMBs fail is they look at their bank balance and think it's all "theirs," forgetting about upcoming payroll or quarterly taxes.
- **How it Enhances:** As soon as an invoice is paid *to* the SMB, the deterministic engine automatically subtracts the estimated tax burden and upcoming payroll from the visible ledger.
- **Implementation:** * *Math:* $C_{usable} = C_{total} - (L_{tax} + L_{payroll})$
    - *Actionable Output:* The dashboard prominently displays "Usable Cash" alongside "Total Balance," preventing the user from making spending decisions based on money that already belongs to the government or employees.

**6. Autonomous "Zombie Spend" Eradication**

- **The Concept:** Immediate liquidity generation by killing unused recurring expenses.
- **How it Enhances:** During the ingestion phase (reading bank statements), the system flags recurring SaaS or subscription payments. If a liquidity crisis is detected, this is the first line of defense.
- **Implementation:**
    - *Actionable Output:* The UI flags a $150/month software subscription. With one click, the generative AI drafts the cancellation email to the vendor or provides the direct cancellation link, instantly adding $150 back to the monthly runway

---

# REVISED FINAL FEATURE GUIDE

Here is the ultimate, master blueprint. I have synthesized every single feature, add-on, and architectural improvement we discussed into a unified, venture-grade product plan. Nothing has been left out.

This plan transitions your project from a basic dashboard into a **"Financial Autopilot,"** strictly adhering to the hackathon’s demands for deterministic logic, explainability, and multi-format data ingestion.

---

### **The "Financial Autopilot" Master Plan**

### **Category 1: Data Ingestion & Integrity (The Foundation)**

To build a reliable system, the data going in must be flawless and standardized.

**1. Omni-Channel Ingestion Pipeline**

- **The Concept:** A unified pipeline that ingests both structured API data and unstructured document images.
- **How it Enhances:** Fulfills the "Multi-Source Financial State Modeling" requirement by converting Plaid/Stripe data, PDF invoices, and handwritten receipts into a strict JSON schema `{entity, amount, due_date, type, flexibility_rating}`.
- **Implementation:** Google Gemini 1.5 Pro (Vision) for OCR + Plaid/Stripe APIs.

**2. N-Way Reconciliation & Fuzzy Matching**

- **The Concept:** Prevents the system from double-counting liabilities.
- **How it Enhances:** Drastically improves "Data Robustness." It matches scanned receipts with pending bank API transactions to merge them rather than creating duplicates.
- **Implementation:** Python logic using Levenshtein distance (fuzzy string matching) to recognize that a receipt from "Home Depot" matches a bank outflow for "HOMEDEPT*44" on the same date.

**3. Strict Function Calling (Tool Use)**

- **The Concept:** Hard separation between generative AI and mathematical calculations.
- **How it Enhances:** Guarantees zero math hallucinations and fulfills the "separation between decision logic and AI" constraint. The LLM never calculates; it only calls Python functions.
- **Implementation:** Gemini API Function Calling. The LLM is provided tools like `calculate_runway()` or `simulate_delay()` and acts purely as an orchestrator.

---

### **Category 2: The Mathematical Brain (Deterministic & Predictive)**

This is where the core logic lives. No LLMs are allowed in these calculations.

**4. The Deterministic "Runway" Engine**

- **The Concept:** A pure mathematical daily compounding ledger calculating the exact "Days to Zero" (D2Z).
- **How it Enhances:** Provides the baseline "Constraint & Runway Detection" required by the prompt.
- **Implementation:** Python (Pandas/NumPy). Logic: $Balance_{today} = Balance_{yesterday} + \sum Receivables_{today} - \sum Payables_{today}$.

**5. Linear Programming (Optimization Engine)**

- **The Concept:** An advanced mathematical solver that replaces basic "sorting" logic.
- **How it Enhances:** Fulfills "Decision Integrity." Instead of guessing what to delay, it calculates the absolute mathematical minimum of "Damage" (fees + goodwill loss) while keeping the cash balance $\ge 0$.
- **Implementation:** Python (`SciPy.optimize`). Defines an objective function to minimize penalties across thousands of payment permutations.

**6. Probabilistic Monte Carlo Modeling (The Reality Check)**

- **The Concept:** Upgrading the deterministic D2Z countdown with real-world probability.
- **How it Enhances:** Accounts for the reality that clients pay late. It runs thousands of simulations based on historical payment variance to predict the actual likelihood of survival.
- **Implementation:** Python (`numpy`). Outputs a probability score (e.g., "82% chance of surviving this week, 18% chance of a shortfall").

**7. Ontological Constraint Matrix**

- **The Concept:** A hardcoded, hierarchical taxonomy of debt (e.g., Tier 0: Taxes, Tier 1: Credit Cards, Tier 2: Suppliers).
- **How it Enhances:** Deepens the "Strategic Reasoning." The Optimization Engine knows it is mathematically forbidden to delay Tier 0 obligations, while Tier 2 obligations are flexible.
- **Implementation:** PostgreSQL relational database mapping every liability to strict constraint rules.

**8. Virtual Liability Ring-Fencing (The "Phantom Balance")**

- **The Concept:** Automatically subtracting upcoming critical obligations (taxes, payroll) from the visible bank balance.
- **How it Enhances:** Prevents reactive decision-making based on inflated balances.
- **Implementation:** Python math logic: $C_{usable} = C_{total} - (L_{tax} + L_{payroll})$. Displays "Usable Cash" alongside "Total Balance" on the frontend.

---

### **Category 3: Tactical Execution (Solving the Shortfall)**

When a shortfall is detected, these are the tools the system uses to save the business.

**9. The Vendor "Goodwill" Scoring Algorithm**

- **The Concept:** Quantifies counterparty relationships based on payment history.
- **How it Enhances:** Guides the Optimization Engine on who is safe to delay without burning critical bridges.
- **Implementation:** Database algorithm. 24 months of on-time payments = 99/100 score. Late payments reduce the score.

**10. Dynamic Payment Fractionalization (Micro-Installments)**

- **The Concept:** Calculating the perfect middle ground between paying $0 and paying 100%.
- **How it Enhances:** Protects Vendor Goodwill while conserving cash. The engine calculates the exact minimum payment needed to keep a vendor happy without bankrupting the user.
- **Implementation:** Python logic determining fractional splits (e.g., "Pay 30% today, 70% next week"), fed into the LLM to draft the communication.

**11. Bi-Directional Liquidity Solving (The Inflow Accelerator)**

- **The Concept:** Proactively generating cash by getting clients to pay faster.
- **How it Enhances:** Shifts the system from defensive to offensive.
- **Implementation:** Scans pending receivables and triggers Gemini to draft targeted emails: *"Hi [Client], we are offering a 3% discount if this invoice is settled by Friday."*

**12. Autonomous "Zombie Spend" Eradication**

- **The Concept:** Immediate liquidity generation by identifying and killing unused recurring expenses (SaaS, subscriptions).
- **How it Enhances:** Low-hanging fruit for runway extension during a crisis.
- **Implementation:** Regular expression matching on bank feeds to flag recurring outflows, paired with Gemini to draft cancellation emails or surface cancellation links.

**13. Micro-Financing / Factoring Fallback**

- **The Concept:** The last resort option if Goodwill is depleted and no receivables can be accelerated.
- **How it Enhances:** Provides a complete safety net, ensuring the user always has a viable action to take.
- **Implementation:** Mock API integration simulating an invoice factoring service (e.g., Stripe Capital) to draw an instant bridge loan for a percentage fee.

---

### **Category 4: Autonomous Operations & Contextual Output**

How the decisions are translated into real-world actions.

**14. Constraint & Context-Aware Action Generator**

- **The Concept:** Translates the system's math into ready-to-use human outputs.
- **How it Enhances:** Ensures tone matches the entity (formal for banks, friendly for local suppliers).
- **Implementation:** Gemini API Prompt Engineering injected with variables (Vendor Tier, Goodwill Score, Shortfall Amount).

**15. The Multi-Agent Negotiation Swarm**

- **The Concept:** Authorized AI agents that actually handle the back-and-forth negotiation with vendors.
- **How it Enhances:** Pushes the project into autonomous execution. The agent can email a vendor, parse a counter-offer, check it against the math engine, and lock in the deal.
- **Implementation:** LangChain or AutoGen hooked to the Gmail API, strictly constrained by a "guardrail wallet."

**16. Automated "Inventory-to-Cash" Liquidation Engine**

- **The Concept:** Connecting the financial ledger to physical assets to generate emergency revenue.
- **How it Enhances:** A highly innovative cross-domain solution. If cash is low, it spins up a flash sale to bridge the gap.
- **Implementation:** Shopify Admin API / Square API. Identifies slow-moving inventory, calculates required discount to raise cash, and triggers Mailchimp campaigns.

---

### **Category 5: User Trust & Transparency**

**17. Chain-of-Thought (CoT) Audit Trail UI**

- **The Concept:** A visual explanation of *why* the system chose a specific path.
- **How it Enhances:** Fulfills the "Explainability" criteria. Non-technical users can review the logic before trusting the AI with their money.
- **Implementation:** Next.js frontend component displaying a step-by-step logic tree: *"Why this choice? 1. Paying rent today causes a -$400 overdraft tomorrow. 2. Vendor X Goodwill is High (95). 3. Fractionalizing Vendor X prevents overdraft with 0 late fees."*

---

### **High-Level Implementation Map (Hackathon Plan)**

- **Step 1: The Dummy Data Layer:** Seed a PostgreSQL database with a realistic 60-day ledger (predictable expenses, variable expenses, incoming payments).
- **Step 2: The Core Python Backend:** Build the FastAPI layer housing the Deterministic Engine, Linear Programming solver, and Ontological Matrix. Write unit tests for the exact day cash drops below zero.
- **Step 3: The Tool/Agent Layer:** Connect Gemini to the FastAPI endpoints using Strict Function Calling. Build the Action Generator prompts.
- **Step 4: The Execution Features:** Wire up the specific tactics (Fractionalization math, Bi-Directional email generation, Phantom Balance calculation).
- **Step 5: The Frontend Dashboard:** Build the Next.js/React UI. Focus on the CoT Audit Trail, the "Usable Cash" visualizer, and an Inbox-style interface for reviewing AI actions.
    
    This is a massive, winning architecture. Would you like me to map out the specific database schema needed to support the Ontological Constraints and Goodwill Scoring, or would you prefer a sample of the exact Gemini prompt used for the Context-Aware Action Generator?
    

# Implementation Guide

Here is the perfectly balanced, feature-complete implementation plan. I have completely removed all time-based markers so your team can work at their own pace without artificial pressure.

I have strictly divided the **17 Master Plan Features** into four distinct domains. Every member has an equal technical load, and because of the JSON contracts we established, nobody has to wait for anyone else to finish before they start coding.

---

### **Phase 1: The Initialization Handshake (All Hands)**

Before coding begins, the team aligns the infrastructure.

- **The Database:** One member spins up the Supabase project, runs the 5-table SQL script, and shares the `DATABASE_URL`.
- **The Environment:** Everyone adds the `DATABASE_URL` and `GEMINI_API_KEY` to their local `.env` files.
- **The Mocks:** Everyone creates a local `mock_data.json` file containing the 6 JSON Contracts we defined.
- **The Split:** The team breaks off into their four parallel streams.

---

### **Stream 1: The Data Engineer (Ingestion & Integrity)**

**Core Responsibility:** Getting messy data into the database cleanly and maintaining the rules engine.

**Tech Stack:** Supabase (PostgreSQL), Python, `rapidfuzz`, Gemini Vision API.

- **Feature 7: Ontological Constraint Matrix:** Populate the `entities` table in Supabase. Hardcode the baseline rules (e.g., Taxes = Tier 0, Credit Cards = Tier 1, Suppliers = Tier 2).
- **Feature 9: Vendor Goodwill Scoring Algorithm:** Write a Python script that queries the `transactions` table. For every on-time payment found, increase the vendor's Goodwill Score; for every late payment, decay it. Update the `entities` table.
- **Feature 1: Omni-Channel Ingestion Pipeline:** Build the `plaid_simulator.py` script to pump fake bank transactions into the database. Then, write the Python function that sends a JPG receipt to Gemini 1.5 Pro Vision and parses the response into **JSON Contract 1**.
- **Feature 2: N-Way Reconciliation:** Implement the `rapidfuzz` library (Levenshtein distance). Write the logic that intercepts the OCR receipt data, checks the `obligations` table for matching amounts within a 48-hour window, and merges them to prevent duplicate debts.

---

### **Stream 2: The Quant (Math Engine & API Gateway)**

**Core Responsibility:** The deterministic brain of the operation. No AI, just pure, irrefutable math.

**Tech Stack:** Python, FastAPI, Pandas, NumPy, SciPy.

- **Feature 4: The Deterministic "Runway" Engine:** Spin up the FastAPI server. Write the Pandas logic to calculate the exact "Days to Zero" (D2Z) by iterating over the `obligations` table.
- **Feature 8 (Backend): Virtual Liability Ring-Fencing:** Write the formula to subtract Tier 0 obligations from the current Plaid balance, outputting the `usable_cash` variable for the frontend.
- **Feature 6: Probabilistic Monte Carlo Modeling:** Use NumPy to run 10,000 simulations on upcoming receivables. Apply a normal distribution to payment dates based on the client's `avg_latency_days`. Output the final "Probability of Survival" score.
- **Features 5 & 10: Linear Programming & Fractionalization:** The hardest task. Use `scipy.optimize.linprog`. Write the objective function to minimize (Late Fees + Goodwill Decay). Set constraints so Tier 0 items must be paid 100%. The solver must calculate the exact micro-installment required (e.g., pay 30% today) to keep the cash balance $\ge 0$. Output this as **JSON Contract 3**.

---

### **Stream 3: The AI Orchestrator (Agents & Execution)**

**Core Responsibility:** Translating the math into human action and negotiating in the real world.

**Tech Stack:** Python, LangChain, Gemini API, External API Mocks.

- **Feature 3: Strict Function Calling:** Define LangChain Tools. The LLM must be physically constrained to using tools like `check_solvency()` and `get_vendor_goodwill()`.
- **Feature 14: Context-Aware Action Generator:** Build the prompt templates. The agent takes **JSON Contract 3** (the math output) and drafts empathetic negotiation emails, adapting its tone based on the vendor's Ontology Tier and Goodwill score.
- **Feature 15: The Multi-Agent Negotiation Swarm:** Build the LangChain graph.
    - *Agent 1 (Communicator):* Drafts emails and reads inbound counter-offers (**JSON Contract 6**).
    - *Agent 2 (Quant Reviewer):* Takes the counter-offer and runs it through Member 2's math engine to verify the new deal doesn't bankrupt the user.
- **Features 11, 12 & 16: Autonomous Execution Triggers:** Write the logic for the alternative actions. Draft the emails for **Bi-Directional Liquidity** (asking clients to pay early for a 3% discount), Regex matching for **Zombie Spend** eradication, and mocking the payload for the **Shopify/Stripe** liquidation fallbacks.

---

### **Stream 4: The Frontend Architect (UI/UX & Trust Layer)**

**Core Responsibility:** Building the command center. Translating complex math and AI logic into a beautiful, explainable interface.

**Tech Stack:** Next.js (React), Tailwind CSS, Recharts, Framer Motion.

- **Global Dashboard & State:** Scaffold the Next.js app. Create the split-pane layout (Passive charts on the left, Active Inbox on the right). Initially, wire the UI to read directly from the local `mock_data.json` so you aren't blocked by the backend.
- **Feature 8 (Frontend): Phantom Balance UI:** Integrate Recharts. Build a dual-line chart. One line is gray (Total Bank Balance), and one line is bold (Phantom Usable Cash). Visually demonstrate the runway dipping below zero.
- **Feature 17: Chain-of-Thought (CoT) Audit Trail:** Build the interactive Stepper component. When a user clicks a pending action in their inbox, use Framer Motion to smoothly expand a card displaying the AI's step-by-step logic tree.
- **Feature 13: The Fallback UI:** Build the specific UI panels that render when standard negotiations fail, allowing the user to click to authorize a Stripe Capital bridge loan or a Shopify Flash Sale.
- **The Wiring:** Replace the mock JSON files with live `fetch()` calls to Member 2's FastAPI endpoints. Wire the "Approve" button to POST **JSON Contract 5** back to the server, triggering Member 3's agents.

---

### **Phase 3: The Final Merge**

Because you established the exact names of your database columns and JSON payloads on day one, the integration phase is vastly simplified:

1. **Data Plumber** ensures the database is populated.
2. **Quant** points their FastAPI server at the live database instead of mock data.
3. **AI Orchestrator** mounts their LangChain functions as endpoints on the Quant's FastAPI server.
4. **Frontend Architect** points their Next.js app to `localhost:8000`.

This distribution is perfectly balanced. Data handles the input, Math handles the rules, AI handles the output, and Frontend handles the human experience.

---

---

---

---

---

# UNIFORM SCHEMA AND JSON

---

---

This is exactly what winning teams do at Hour 0. You are establishing the "Single Source of Truth." If your teammates follow this document, you will eliminate 90% of the integration bugs that kill other hackathon teams on Sunday morning.

Here is the complete, copy-paste ready **Master Architecture Document**. Send this directly to your team's Slack or Discord.

---

# 🏗️ SYSTEM ARCHITECTURE MASTER DOC: FINANCIAL AUTOPILOT

**Team Rule:** If a data field is not in this document, it does not exist. Do not change schemas without telling the group.

## PART 1: SUPABASE / POSTGRESQL SCHEMA (5 TABLES)

**Assignee:** Data Plumber (Run these in the Supabase SQL Editor immediately).

**1. `companies` (The User's Snapshot)**

*Purpose:* Stores the business owner's profile and the live Plaid bank balance.

SQL

# 

`CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    plaid_current_balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    last_synced_at TIMESTAMP DEFAULT now()
);`

**2. `entities` (Vendors & Clients Ontology)**

*Purpose:* The rules engine. Defines who we owe, their priority level (Tier 0-3), and behavioral data (Goodwill, late fees).

SQL

# 

`CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(10) NOT NULL, -- 'VENDOR' or 'CLIENT'
    ontology_tier INT NOT NULL, -- 0 (Locked), 1 (Penalty), 2 (Relational), 3 (Flexible)
    goodwill_score INT DEFAULT 100, -- 0 to 100 scale
    late_fee_rate DECIMAL(5,4) DEFAULT 0.0000, -- e.g., 0.015 for 1.5%
    avg_latency_days INT DEFAULT 0 -- Used by Monte Carlo
);`

**3. `transactions` (The Past Ledger)**

*Purpose:* Historical Plaid data used strictly to calculate Goodwill Scores based on past on-time payments.

SQL

# 

`CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID REFERENCES entities(id),
    amount DECIMAL(12,2) NOT NULL,
    cleared_date DATE NOT NULL,
    source VARCHAR(50) DEFAULT 'PLAID_API'
);`

**4. `obligations` (The Future Ledger)**

*Purpose:* Pending bills and expected receivables. This is the exact table the Math Engine queries to run the LP Solver.

SQL

# 

`CREATE TABLE obligations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID REFERENCES entities(id),
    amount DECIMAL(12,2) NOT NULL, -- Negative = Payable, Positive = Receivable
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'SHUFFLED', 'PAID'
    is_locked BOOLEAN DEFAULT FALSE -- True if Tier 0 (Taxes/Payroll)
);`

**5. `action_logs` (AI Memory & Inbox)**

*Purpose:* Stores the AI's logic to show the user, holds the email/Shopify payloads, and tracks LangChain conversation threads.

SQL

# 

`CREATE TABLE action_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    obligation_id UUID REFERENCES obligations(id) NULL, 
    status VARCHAR(50) DEFAULT 'PENDING_USER', -- 'PENDING_USER', 'NEGOTIATING', 'RESOLVED'
    chain_of_thought JSONB NOT NULL,
    execution_type VARCHAR(50) NOT NULL, -- 'GMAIL', 'SHOPIFY', 'STRIPE'
    execution_payload JSONB NOT NULL,
    agent_thread_id VARCHAR(255) NULL -- For tracking vendor email replies
);`

---

## PART 2: THE IMMUTABLE JSON CONTRACTS (6 PAYLOADS)

**Assignees:** All Devs. Ensure your API routes accept and return these exact structures.

### Contract 1: Standard Ingestion Payload

- **Flow:** Gemini Vision OCR / Plaid Simulator -> Python Backend -> Database
- **Purpose:** Normalizing messy real-world data into a clean object.

JSON

# 

`{
  "ingestion_event": {
    "source": "GEMINI_VISION_OCR",
    "raw_text_reference": "Home Depot Store #4492...",
    "parsed_data": {
      "entity_name": "Home Depot",
      "entity_type": "VENDOR",
      "amount": -345.50,
      "due_date": "2026-03-30"
    },
    "reconciliation_confidence": 0.98
  }
}`

### Contract 2: The Dashboard Global State

- **Flow:** Python Backend (`/api/dashboard`) -> Next.js Frontend
- **Purpose:** Gives the UI everything it needs to render the charts and Phantom Balance.

JSON

# 

`{
  "global_state": {
    "plaid_balance": 12450.00,
    "phantom_usable_cash": 4100.00,
    "locked_tier_0_funds": 8350.00,
    "runway_metrics": {
      "days_to_zero": 8,
      "liquidity_breach_date": "2026-04-02",
      "monte_carlo_survival_prob": 0.12
    },
    "cashflow_projection_array": [
      {"date": "2026-03-25", "balance": 4100.00},
      {"date": "2026-03-26", "balance": 4100.00},
      {"date": "2026-03-27", "balance": -200.00} 
    ]
  }
}`

### Contract 3: The Math Directive (No Hallucinations)

- **Flow:** Python LP Solver -> Gemini LangChain Agent
- **Purpose:** The pure math instructions passed to the LLM so it knows exactly what deal to negotiate.

JSON

# 

`{
  "solver_directive": {
    "breach_amount": -200.00,
    "optimization_result": [
      {
        "obligation_id": "ob_992",
        "entity_name": "Acme Supplies",
        "original_due": "2026-03-27",
        "math_decision": "FRACTIONAL_PAYMENT",
        "pay_now_amount": 100.00,
        "delay_amount": 300.00,
        "requested_extension_days": 7
      }
    ]
  }
}`

### Contract 4: The Action Inbox Item

- **Flow:** Python/AI Backend -> Next.js Frontend
- **Purpose:** Populates the UI queue for the user to review the AI's Chain of Thought and approve the action.

JSON

# 

`{
  "action_item": {
    "id": "act_001",
    "status": "PENDING_APPROVAL",
    "title": "Fractionalize Acme Supplies Payment",
    "chain_of_thought": [
      "Projected shortfall of $200 on March 27th.",
      "Acme Supplies is Tier 2 (Flexible) with 95/100 Goodwill.",
      "Paying $100 today prevents overdraft while maintaining vendor trust."
    ],
    "execution_type": "GMAIL_NEGOTIATION", 
    "payload": {
      "to": "billing@acme.com",
      "subject": "Invoice #442 - Partial Payment",
      "body": "Hi Acme team, we are remitting $100.00 today..."
    }
  }
}`

### Contract 5: The Execution Trigger

- **Flow:** Next.js Frontend ("Approve" Button) -> Python Backend
- **Purpose:** Tells the backend the user has signed off, authorizing the AI to actually hit the Gmail or Shopify APIs.

JSON

# 

`{
  "trigger_execution": {
    "action_id": "act_001",
    "execution_type": "GMAIL_NEGOTIATION",
    "approved_by_user": true,
    "timestamp": "2026-03-25T14:30:00Z"
  }
}`

### Contract 6: The Inbound Webhook (The Negotiation Loop)

- **Flow:** Gmail / External World -> Python Backend -> LangChain Swarm
- **Purpose:** Wakes up the AI when a vendor replies with a counter-offer, allowing the math engine to re-verify the new terms.

JSON

# 

`{
  "inbound_communication": {
    "source": "GMAIL_WEBHOOK",
    "agent_thread_id": "thread_8829_acme",
    "sender": "billing@acme.com",
    "received_at": "2026-03-25T16:00:00Z",
    "raw_text": "We cannot accept $100. We need at least $200 remitted today.",
    "extracted_intent": {
      "is_agreement": false,
      "counter_offer_detected": true,
      "requested_amount": 200.00
    }
  }
}`

---

To make your team's life even easier right out of the gate, would you like me to generate the **Pydantic Models** (for your Python/FastAPI developers) or the **TypeScript Interfaces** (for your Next.js developer) based exactly on these JSON contracts? They can just copy-paste them in to get instant autocomplete and type-safety.

# SUPABASE SETUP

Excellent choice. Using Supabase instantly elevates your team from "college project" to "venture-backed startup" speed.

To ensure nobody is blocked, you need to execute the **"Hour 1 Database Handshake."** Here is the exact step-by-step setup guide for your team. Copy and paste this directly into your team's Discord or Slack channel so everyone knows their exact mission the minute the clock starts.

---

### **Phase 1: The Admin Setup (Assign to Member 1 - The Data Plumber)**

*Only one person does this to prevent duplicate databases.*

1. **Create the Project:** Go to **Supabase.com**, log in with GitHub, and click **"New Project."**
2. **Configure:** Name it `financial-autopilot`. Generate a secure database password and **save it to a notepad immediately** (Supabase will not show it to you again). Choose a server region closest to the hackathon venue to minimize latency.
3. **Run the Schema:** Click on the **"SQL Editor"** tab on the left sidebar. Paste the exact `CREATE TABLE` SQL scripts we finalized in the previous step and hit **Run**. Your tables now exist in the cloud.
4. **Retrieve the Keys:** Go to **Project Settings -> Database**. Scroll down to **Connection String -> URI**.
5. **Broadcast:** Copy that URI string and drop it in your team chat. It will look like this:
6. URI:
    
    postgresql://postgres:Supabase*123@db.jcmtqmrkmrobglcsbrws.supabase.co:5432/postgres
    

---

### **Phase 2: The Universal Environment Setup (All 4 Members)**

Every single person on the team must now create a file named `.env` in the root folder of their local code repository.

**Everyone pastes this exact block into their `.env` file:**

Code snippet

# 

`# Database Connection
DATABASE_URL="postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# AI Integration
GEMINI_API_KEY="your_google_ai_studio_key_here"`

*(Note: Member 1 must replace `[YOUR-PASSWORD]` with the actual password before sending it to the team).*

---

### **Phase 3: The Architecture Rules (Crucial for the Hackathon)**

To prevent messy, spaghetti code that will break during your demo, your team must agree to these strict connection rules right now.

### **Rule 1: The Frontend (Member 4) is BANNED from talking to Supabase.**

- **The Trap:** Supabase offers a slick Javascript client (`supabase-js`) that lets Next.js fetch data directly from the database. **Do not use it.**
- **The Reason:** If your Next.js frontend pulls data directly from the database, it bypasses your Python Deterministic Engine. You lose the Phantom Balance math and the Optimization engine.
- **The Solution:** The Next.js frontend only ever makes standard `fetch()` calls to Member 2's FastAPI endpoints (e.g., `http://localhost:8000/api/dashboard`).

### **Rule 2: Python (Members 1, 2, & 3) owns the Database.**

Your Python backend will be the only thing connecting to Supabase. To keep things lightning-fast and avoid the learning curve of massive ORMs like SQLAlchemy, use the `psycopg2` library. It allows you to write raw, clean SQL.

**Have your Python devs run this terminal command:**

`pip install psycopg2-binary python-dotenv fastapi uvicorn`

**The Universal Database Connection Boilerplate (Python):**

Have Members 1, 2, and 3 create a file called `db.py` and paste this in. They will use this exact function anytime they need to read or write data.

Python

# 

`import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load the .env file you all created
load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL"), 
            cursor_factory=RealDictCursor # This forces SQL to return JSON-like dictionaries!
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

# --- Example of how the Math Engine will use this ---
# conn = get_db_connection()
# cursor = conn.cursor()
# cursor.execute("SELECT * FROM obligations WHERE status = 'PENDING'")
# pending_bills = cursor.fetchall() 
# conn.close()`

### **The "Hour 1" Finish Line**

Once Phase 1, 2, and 3 are done, your team is completely networked.

- Member 1 can start writing Python scripts to push mock Plaid data into Supabase.
- Member 2 can start pulling that live data into the FastAPI math engine.
- Member 4 can start building the Next.js UI, pointing it at Member 2's FastAPI server.

You are now developing in perfect parallel.

Would you like me to write the exact `mock_plaid_ingestion.py` script for Member 1? They can run it once to instantly flood your new Supabase database with 50 realistic, hackathon-ready transactions and vendor profiles.

# API sims

This is the ultimate hackathon survival question.

If you try to set up real OAuth flows, live webhooks, and production API keys for Plaid, Stripe, and Shopify in 48 hours, you will spend 30 hours reading documentation and 0 hours building your AI.

To win a hackathon, you don't need real APIs; you need **Deterministic API Simulators**. You need to build your own mini-endpoints that *pretend* to be Plaid and Stripe, returning the exact JSON your app expects in milliseconds.

Here is the "Hackathon Cheat Code" for simulating all three systems perfectly so your demo looks flawless.

---

### **1. Plaid (The Sensory System)**

**The Goal:** Simulate a constant stream of new bank transactions hitting your database.

**The Trap:** Real Plaid requires a frontend widget, token exchange, and webhook listeners.

**The Hackathon Solution: "The Ghost Transaction Generator"**

Instead of connecting to Plaid, Member 1 (The Data Plumber) writes a Python script called `plaid_simulator.py`.

- **How it works:** This script runs in the background. Every 30 seconds, it randomly selects a vendor from your `entities` table, generates a random dollar amount, and uses `psycopg2` to directly `INSERT` a new row into your Supabase `obligations` table.
- **The Demo Effect:** During your pitch, you leave this script running. The judges will watch your frontend Next.js dashboard autonomously update with "live" transactions, and your "Days to Zero" runway will dynamically change in real-time. It looks like magic.

### **2. Stripe & Stripe Capital (The Payments & Loan Fallback)**

**The Goal:** Simulate receiving money from a client or drawing a bridge loan.

**The Trap:** Setting up Stripe webhooks requires exposing your `localhost` to the internet using tools like Ngrok, which often crash during live demos.

**The Hackathon Solution: "The Mock Payment Gateway"**

Member 2 (The FastAPI Quant) builds two fake endpoints directly into your own Python backend:

- **Endpoint A: `/api/mock-stripe/payment-link`**
    - *Action:* When your AI agent negotiates a deal, it hits this endpoint.
    - *Response:* It instantly returns a fake URL: `https://pay.stripe.com/test_8xjd92`. You put this URL in the drafted email.
- **Endpoint B: `/api/mock-stripe/capital-draw`**
    - *Action:* If the Runway Engine detects a fatal crash, it hits this endpoint requesting $5,000.
    - *Response:* The endpoint instantly returns `{"status": "APPROVED", "funds_deposited": 5000, "fee": 150}` and automatically updates the Supabase bank balance.

### **3. Shopify (The Asset Liquidation Engine)**

**The Goal:** Prove your system can cross domains and spin up an inventory flash sale to raise cash.

**The Hackathon Solution: "The E-Commerce Sandbox Endpoint"**

You don't need a real Shopify store. You just need to prove your AI knows *how* and *when* to trigger one.

- **The Setup:** Member 2 creates a mock endpoint: `/api/mock-shopify/flash-sale`.
- **The Action:** When the math engine realizes it needs $2,000 fast, it POSTs a payload to this endpoint: `{"target_revenue": 2000, "discount_pct": 20}`.
- **The Response:** The endpoint returns: `{"status": "success", "campaign_live": true, "shareable_link": "myshopify.com/flash-sale-20"}`.
- **The Demo Effect:** You show the judges the Chain-of-Thought UI logging this exact interaction. It proves the architecture works, even if the store is fake.

---

### **The "Why This Wins" Pitch to the Judges**

If a technical judge asks, *"Are you actually connected to Plaid and Shopify right now?"* you give them this incredibly professional answer:

> *"For this 48-hour sprint, we built **Deterministic API Simulators** inside our FastAPI backend. Because our architecture is strictly decoupled using JSON contracts, our Python engine doesn't know the difference between our simulator and the real Plaid or Shopify production endpoints. Tomorrow, if we swap our mock URLs for production URLs and drop in live API keys, the entire Financial Autopilot functions exactly the same. We optimized for architectural integrity over third-party OAuth wrangling."*
> 

Judges respect teams that know how to scope a project and fake the external dependencies to prove the internal core logic.

Would you like me to write the exact Python code for the `plaid_simulator.py` script? Member 1 can run it in the background to inject realistic, randomized financial chaos into your database for the AI to solve.