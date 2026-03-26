# Stream 3: AI Orchestrator - Complete Overview

## 🎯 What is Stream 3?

Stream 3 is the **AI-powered execution layer** that translates mathematical optimization decisions into contextual human communications. It's the bridge between cold calculations and warm relationships.

**Key Principle**: The AI never makes financial decisions—it only executes strategies determined by the mathematical engine (Stream 2).

---

## 🌟 Core Features

### 1. Context-Aware Action Generator
Drafts vendor-specific communications based on:
- Relationship history (goodwill score)
- Vendor tier (critical vs flexible)
- Payment amount and timing
- Previous interaction patterns

**Example Output**:
```
Hi Acme Corp,

I hope this message finds you well. Due to a temporary cash flow timing 
issue with a major client payment, I'm writing to request a brief 7-day 
extension on our upcoming invoice.

As a gesture of good faith, I'm processing a partial payment of $1,500 
today, with the remaining balance scheduled for April 15th.

We truly value our 3-year partnership and appreciate your understanding.
```

### 2. Bi-Directional Liquidity Solver
Not just delaying payments—also accelerating receivables:
- Identifies clients with pending invoices
- Calculates optimal early payment discounts
- Drafts incentive communications
- Creates urgency with time-limited offers

**Example Output**:
```
Hi [Client],

I wanted to reach out with a time-sensitive opportunity. If you're able 
to settle Invoice #4421 by Friday (5 days early), we're offering a 3% 
early payment discount—saving you $150.

New amount: $4,850 (originally $5,000)

This offer is valid through Friday, April 12th.
```

### 3. Zombie Spend Eradication
Identifies unused recurring subscriptions for immediate cash flow improvement:
- Pattern matching on transaction history
- Flags recurring charges with no usage indicators
- Calculates monthly/annual savings
- Generates cancellation communications

**Example Detection**:
```json
{
  "vendor_name": "SaaS Tool Pro",
  "monthly_cost": 149.00,
  "annual_cost": 1788.00,
  "confidence": "HIGH",
  "recommendation": "REVIEW_FOR_CANCELLATION"
}
```

### 4. Chain-of-Thought Reasoning
Every AI action includes transparent reasoning:
```
Decision Rationale:
1. Vendor Tier: 2 (Flexible - can be delayed)
2. Goodwill Score: 85/100 (Strong relationship)
3. Extension: 7 days maintains positive cash flow
4. Partial payment of $1,500 demonstrates good faith
5. Tone: FRIENDLY_CONFIDENT based on relationship strength
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  STREAM 3 COMPONENTS                     │
└─────────────────────────────────────────────────────────┘

Input: Stream 2 Optimization Output
    ↓
┌─────────────────────────────────────────────────────────┐
│  Action Generator                                        │
│  • Payment delay communications                          │
│  • Receivable acceleration offers                        │
│  • Tone adaptation (4 levels)                           │
│  • Context enrichment                                    │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  Zombie Detector                                         │
│  • Recurring transaction analysis                        │
│  • Subscription pattern matching                         │
│  • Savings calculation                                   │
│  • Cancellation drafting                                 │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  Action Logger                                           │
│  • Database persistence                                  │
│  • Chain-of-Thought storage                             │
│  • Approval workflow                                     │
│  • Audit trail                                           │
└─────────────────────────────────────────────────────────┘
    ↓
Output: Action Logs (awaiting user approval)
```

---

## 📊 Data Flow

### 1. Input from Stream 2
```json
{
  "optimized_obligations": [
    {
      "obligation_id": "uuid-123",
      "entity_name": "Acme Corp",
      "pay_now": 1500.00,
      "delay_amount": 500.00,
      "new_due_date": "2026-04-15",
      "ontology_tier": 2,
      "goodwill_score": 85
    }
  ]
}
```

### 2. Context Enrichment
```python
# Stream 3 queries database for additional context
context = {
    "relationship_history": "3-year partnership",
    "previous_delays": 0,
    "last_payment_date": "2026-03-15",
    "relationship_notes": "Always paid on time"
}
```

### 3. AI Generation
```python
# Gemini generates contextual communication
communication = generate_with_gemini(
    vendor_context=context,
    optimization_output=stream2_output,
    tone=select_tone(tier, goodwill)
)
```

### 4. Action Logging
```sql
INSERT INTO action_logs (
    action_type,
    message,
    status,
    chain_of_thought,
    execution_payload
) VALUES (
    'PAYMENT_DELAY',
    'AI-Generated: Hi Acme Corp...',
    'PENDING_USER_APPROVAL',
    '{"reasoning": "..."}',
    '{"communication_draft": "..."}'
);
```

---

## 🎨 Tone Adaptation

Stream 3 adapts communication tone based on vendor relationship:

| Tier | Goodwill | Tone | Example Phrase |
|------|----------|------|----------------|
| 0 | Any | FORMAL_URGENT | "We must discuss immediate payment arrangements" |
| 1-3 | ≥80 | FRIENDLY_CONFIDENT | "I hope this message finds you well" |
| 1-3 | 50-79 | PROFESSIONAL_RESPECTFUL | "I'm writing to request your consideration" |
| 1-3 | <50 | FORMAL_APOLOGETIC | "I sincerely apologize for this request" |

---

## 🔒 Safety Guardrails

### 1. Zero Financial Authority
Stream 3 CANNOT:
- ❌ Decide which vendor to delay
- ❌ Calculate payment amounts
- ❌ Determine payment schedules
- ❌ Prioritize obligations

Stream 3 CAN ONLY:
- ✅ Draft communications
- ✅ Adapt tone to context
- ✅ Explain decisions
- ✅ Log actions for approval

### 2. Human-in-the-Loop
```
AI Generates → Logs to DB → User Reviews → User Approves/Rejects
```

### 3. Tier 0 Protection
Critical obligations (taxes, payroll) are never delayed:
```python
if tier == 0:
    return {
        "status": "BLOCKED",
        "reason": "Tier 0 obligations cannot be delayed"
    }
```

### 4. Audit Trail
Every action includes:
- Full Chain-of-Thought reasoning
- Context used for decision
- Timestamp and user ID
- Approval/rejection status

---

## 🚀 Quick Start

### Installation
```bash
cd SnuHack/cashpilot/backend
pip install google-generativeai langchain langchain-google-genai
```

### Configuration
```bash
# Add to .env
GEMINI_API_KEY=your_api_key_here
```

### Basic Usage
```python
from ai.action_generator import generate_payment_delay_action

# Generate payment delay communication
action = generate_payment_delay_action(
    obligation_id="uuid-123",
    delay_days=7,
    fractional_payment=1500.00
)

# Action is automatically logged to database
# User can review in Action Inbox
```

---

## 📋 API Endpoints

### Generate Payment Delay
```bash
POST /api/ai/generate-payment-delay
{
  "obligation_id": "uuid",
  "delay_days": 7,
  "fractional_payment": 1500.00
}
```

### Generate Receivable Acceleration
```bash
POST /api/ai/generate-receivable-acceleration
{
  "obligation_id": "uuid",
  "discount_percentage": 3.0,
  "urgency_days": 5
}
```

### Detect Zombie Spend
```bash
GET /api/ai/detect-zombie-spend
```

### Get Pending Actions
```bash
GET /api/ai/actions
```

---

## 🧪 Testing

### Unit Tests
```python
def test_tone_selection():
    assert select_tone(tier=2, goodwill=85) == "FRIENDLY_CONFIDENT"
    assert select_tone(tier=0, goodwill=100) == "FORMAL_URGENT"
```

### Integration Tests
```python
def test_action_generation():
    action = generate_payment_delay_action("uuid", 7)
    assert action['communication_draft'] is not None
    assert action['requires_approval'] == True
```

### Manual Testing
```bash
# Test payment delay
curl -X POST http://localhost:8000/api/ai/generate-payment-delay \
  -H "Content-Type: application/json" \
  -d '{"obligation_id": "uuid", "delay_days": 7}'

# Test zombie detection
curl http://localhost:8000/api/ai/detect-zombie-spend
```

---

## 📈 Success Metrics

### Functional
- ✅ 100% of actions include Chain-of-Thought reasoning
- ✅ 100% of actions logged to database
- ✅ 0% of actions executed without user approval
- ✅ Tone adapts correctly based on context

### Quality
- ✅ Communication drafts under 150 words
- ✅ All required context elements included
- ✅ Tone matches vendor relationship
- ✅ No financial hallucinations

### Performance
- ✅ Action generation < 2 seconds
- ✅ Zombie detection < 1 second
- ✅ API response time < 500ms

---

## 🎯 Integration with Other Streams

### With Stream 1 (Data Ingestion)
```python
# Stream 1 ingests transactions
# Stream 3 analyzes for zombie spend
zombies = detect_zombie_subscriptions(company_id)
```

### With Stream 2 (Mathematical Engine)
```python
# Stream 2 generates optimization
optimization = optimize_payment_strategy(company_id)

# Stream 3 generates actions
for obligation in optimization['optimized_obligations']:
    action = generate_payment_delay_action(obligation['obligation_id'], 7)
```

### With Stream 4 (Frontend)
```python
# Frontend fetches pending actions
GET /api/ai/actions

# User reviews and approves
POST /api/ai/actions/{id}/approve
```

---

## 📚 Documentation

- **Full Implementation Plan**: `stream3_plan.md`
- **Quick Start Guide**: `STREAM3_QUICKSTART.md`
- **Architecture Details**: `STREAM3_ARCHITECTURE.md`
- **This Overview**: `README_STREAM3.md`

---

## 🔮 Future Enhancements

### Phase 2 (Post-Hackathon)
1. **Multi-Agent Negotiation**: Autonomous back-and-forth with vendors
2. **Sentiment Analysis**: Analyze vendor responses, adjust strategy
3. **A/B Testing**: Test different communication styles
4. **Email Integration**: Actually send emails via Gmail API
5. **Inventory Liquidation**: Connect to Shopify for flash sales

---

## 💡 Key Takeaways

1. **AI is a Translator, Not a Decider**: Stream 3 never makes financial decisions
2. **Context is King**: Relationship history drives tone and approach
3. **Human Approval Required**: All actions logged, none executed automatically
4. **Explainability Matters**: Chain-of-Thought builds user trust
5. **Safety First**: Multiple guardrails prevent financial errors

---

## 🎓 Learning Resources

### Gemini API
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Function Calling Guide](https://ai.google.dev/docs/function_calling)
- [Prompt Engineering Best Practices](https://ai.google.dev/docs/prompt_best_practices)

### LangChain
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Agent Framework](https://python.langchain.com/docs/modules/agents/)

---

## 🏆 Hackathon Evaluation Alignment

### How Stream 3 Addresses Criteria

| Criterion | How Stream 3 Helps |
|-----------|-------------------|
| **Decision Integrity** | AI never makes decisions, only executes |
| **Strategic Reasoning** | Chain-of-Thought explains every action |
| **System Architecture** | Clear separation: math (S2) vs AI (S3) |
| **Actionable Usability** | Ready-to-use communications, not raw data |
| **Explainability** | Full reasoning trail for every action |
| **Reliability** | Deterministic tone selection, no hallucinations |

---

## 🚀 Getting Started

1. **Read**: `STREAM3_QUICKSTART.md` for 5-minute setup
2. **Understand**: `STREAM3_ARCHITECTURE.md` for system design
3. **Implement**: `stream3_plan.md` for step-by-step guide
4. **Test**: Use provided curl commands to verify
5. **Integrate**: Connect with Stream 2 optimizer output

---

**Stream 3: Where Math Meets Empathy 🤖💬**

**Estimated Implementation Time**: 3-4 hours
**Priority**: HIGH (Core differentiator)
**Dependencies**: Stream 2 (Mathematical Engine)
**Status**: Ready to implement

---

**Let's build the heart of CashPilot—the AI that turns cold calculations into warm relationships! 🚀**
