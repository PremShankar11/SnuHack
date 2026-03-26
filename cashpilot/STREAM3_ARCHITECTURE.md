# Stream 3 Architecture: AI Orchestrator

## 🏗️ System Design Overview

Stream 3 sits between the mathematical engine (Stream 2) and the user interface (Stream 4), translating deterministic decisions into contextual human communications.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CASHPILOT ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   STREAM 1   │      │   STREAM 2   │      │   STREAM 3   │
│              │      │              │      │              │
│ Data         │─────▶│ Mathematical │─────▶│ AI           │
│ Ingestion    │      │ Engine       │      │ Orchestrator │
│              │      │              │      │              │
│ • Plaid API  │      │ • Runway     │      │ • Action     │
│ • OCR        │      │ • LP Solver  │      │   Generator  │
│ • Reconcile  │      │ • Monte Carlo│      │ • Negotiation│
│              │      │              │      │ • Zombies    │
└──────────────┘      └──────────────┘      └──────────────┘
                                                    │
                                                    ▼
                                            ┌──────────────┐
                                            │   STREAM 4   │
                                            │              │
                                            │ Frontend UI  │
                                            │              │
                                            │ • Dashboard  │
                                            │ • Action     │
                                            │   Inbox      │
                                            └──────────────┘
```

---

## 🎯 Core Principles

### 1. Separation of Concerns

**Stream 2 (Math)**: Makes ALL financial decisions
- Who to pay
- How much to pay
- When to pay
- What to delay

**Stream 3 (AI)**: Executes decisions through communication
- How to phrase the request
- What tone to use
- What context to include
- How to maintain relationships

### 2. Zero Financial Authority

Stream 3 has ZERO authority to:
- ❌ Decide which vendor to delay
- ❌ Calculate payment amounts
- ❌ Determine payment schedules
- ❌ Prioritize obligations

Stream 3 can ONLY:
- ✅ Draft communications
- ✅ Adapt tone to context
- ✅ Explain decisions
- ✅ Log actions for approval

### 3. Human-in-the-Loop

All AI-generated actions require user approval:
```
AI Generates Action → Logs to Database → User Reviews → User Approves/Rejects
```

---

## 📊 Data Flow Architecture

### Input: Stream 2 Optimization Output

```json
{
  "status": "SUCCESS",
  "optimized_obligations": [
    {
      "obligation_id": "uuid-123",
      "entity_name": "Acme Corp",
      "original_amount": -2000.00,
      "pay_now": 1500.00,
      "delay_amount": 500.00,
      "new_due_date": "2026-04-15",
      "ontology_tier": 2,
      "goodwill_score": 85
    }
  ],
  "total_delayed": 500.00,
  "projected_savings": 150.00
}
```

### Processing: Context Enrichment

Stream 3 enriches the mathematical output with relationship context:

```python
# Query database for additional context
context = {
    "vendor_name": "Acme Corp",
    "relationship_history": "3-year partnership, always paid on time",
    "goodwill_score": 85,
    "tier": 2,  # Relational (flexible)
    "previous_delays": 0,
    "last_payment_date": "2026-03-15"
}
```

### Output: AI-Generated Action

```json
{
  "action_type": "PAYMENT_DELAY",
  "obligation_id": "uuid-123",
  "communication_draft": "Hi Acme Corp,\n\nI hope this message finds you well...",
  "tone": "FRIENDLY_CONFIDENT",
  "reasoning": "1. Vendor Tier: 2 (Flexible)\n2. Goodwill Score: 85/100...",
  "entity_context": {...},
  "requires_approval": true
}
```

### Storage: Action Logs Table

```sql
INSERT INTO action_logs (
    company_id,
    action_type,
    message,
    status,
    chain_of_thought,
    execution_type,
    execution_payload,
    created_at
) VALUES (
    'company-uuid',
    'PAYMENT_DELAY',
    'AI-Generated: Hi Acme Corp...',
    'PENDING_USER_APPROVAL',
    '{"reasoning": "1. Vendor Tier: 2..."}',
    'AI_GENERATED',
    '{"communication_draft": "...", "tone": "..."}',
    NOW()
);
```

---

## 🧩 Module Architecture

### 1. Action Generator (`ai/action_generator.py`)

**Responsibilities**:
- Generate payment delay communications
- Generate receivable acceleration offers
- Adapt tone based on context
- Provide Chain-of-Thought reasoning

**Key Functions**:
```python
generate_payment_delay_action(obligation_id, delay_days, fractional_payment)
generate_receivable_acceleration_action(obligation_id, discount_pct, urgency_days)
```

**Tone Selection Logic**:
```
Tier 0 (Critical) → FORMAL_URGENT
Goodwill ≥ 80 → FRIENDLY_CONFIDENT
Goodwill ≥ 50 → PROFESSIONAL_RESPECTFUL
Goodwill < 50 → FORMAL_APOLOGETIC
```

### 2. Zombie Detector (`ai/zombie_detector.py`)

**Responsibilities**:
- Identify recurring subscriptions
- Flag unused services
- Calculate potential savings
- Generate cancellation actions

**Detection Heuristics**:
```python
is_zombie = (
    transaction_count >= 2 and
    days_active >= 25 and
    ontology_tier >= 2 and  # Non-critical only
    matches_subscription_pattern
)
```

### 3. AI Router (`api/ai_router.py`)

**Responsibilities**:
- Expose AI capabilities via REST API
- Log all actions to database
- Provide action approval interface
- Integrate with Stream 2 outputs

**Endpoints**:
```
POST /api/ai/generate-payment-delay
POST /api/ai/generate-receivable-acceleration
GET  /api/ai/detect-zombie-spend
POST /api/ai/generate-cancellation/{entity_id}
GET  /api/ai/actions
```

---

## 🔄 Integration Points

### With Stream 2 (Mathematical Engine)

```python
# Stream 2 generates optimization
from quant.optimizer import optimize_payment_strategy
optimization = optimize_payment_strategy(company_id)

# Stream 3 generates actions for each optimized obligation
from ai.action_generator import generate_payment_delay_action

for obligation in optimization['optimized_obligations']:
    if obligation['delay_amount'] > 0:
        action = generate_payment_delay_action(
            obligation['obligation_id'],
            delay_days=7,
            fractional_payment=obligation['pay_now']
        )
        # Action automatically logged to database
```

### With Stream 1 (Data Ingestion)

```python
# Stream 1 ingests transactions
# Stream 3 analyzes patterns for zombie spend

from ai.zombie_detector import detect_zombie_subscriptions
zombies = detect_zombie_subscriptions(company_id)

# Zombies are flagged for user review
```

### With Stream 4 (Frontend)

```python
# Frontend fetches pending actions
GET /api/ai/actions

# User reviews and approves/rejects
POST /api/ai/actions/{action_id}/approve
POST /api/ai/actions/{action_id}/reject
```

---

## 🎨 Prompt Engineering Strategy

### Context Injection

All Gemini prompts include:
1. **Role Definition**: "You are a financial communication specialist"
2. **Specific Context**: Vendor name, amount, dates, relationship history
3. **Tone Guidance**: Based on tier and goodwill score
4. **Constraints**: Word limits, required elements
5. **Output Format**: Email body only, no subject

### Example Prompt Template

```python
prompt = f"""You are a financial communication specialist. Draft a professional email requesting a payment extension.

Context:
- Vendor: {vendor_name}
- Original Amount: ${amount:,.2f}
- Original Due Date: {due_date}
- Requested Extension: {delay_days} days
- Relationship Quality: {goodwill_score}/100
- Relationship History: {relationship_notes}
- Tone: {tone}

Requirements:
1. Be concise (under 150 words)
2. Acknowledge the relationship history
3. Provide a clear reason (cash flow timing, not financial distress)
4. Offer specific new payment date
5. Express commitment to the relationship
6. Use appropriate tone: {tone}

Draft the email body only (no subject line):"""
```

---

## 🔒 Safety & Compliance

### Guardrails

1. **No Financial Decisions**: AI cannot change amounts, dates, or priorities
2. **User Approval Required**: All actions logged, none executed automatically
3. **Audit Trail**: Full Chain-of-Thought reasoning stored
4. **Tier 0 Protection**: Critical obligations (taxes, payroll) never delayed
5. **Goodwill Preservation**: Tone adapts to protect relationships

### Error Handling

```python
try:
    action = generate_payment_delay_action(...)
except Exception as e:
    # Log error
    # Return graceful fallback
    # Never expose internal errors to user
    return {
        "status": "ERROR",
        "message": "Unable to generate action",
        "fallback": "Please contact vendor directly"
    }
```

---

## 📈 Performance Considerations

### Gemini API Optimization

1. **Batch Requests**: Generate multiple actions in parallel
2. **Caching**: Cache common prompt templates
3. **Rate Limiting**: Implement exponential backoff
4. **Fallbacks**: Provide template-based fallbacks if API fails

### Database Optimization

1. **Indexed Queries**: Index `action_logs` by `status` and `created_at`
2. **Pagination**: Limit action list queries
3. **Archiving**: Move resolved actions to archive table

---

## 🧪 Testing Strategy

### Unit Tests

```python
def test_tone_selection():
    # High goodwill → Friendly tone
    assert select_tone(tier=2, goodwill=85) == "FRIENDLY_CONFIDENT"
    
    # Low goodwill → Apologetic tone
    assert select_tone(tier=2, goodwill=30) == "FORMAL_APOLOGETIC"
    
    # Tier 0 → Always urgent
    assert select_tone(tier=0, goodwill=100) == "FORMAL_URGENT"
```

### Integration Tests

```python
def test_end_to_end_action_generation():
    # 1. Create test obligation
    obligation_id = create_test_obligation()
    
    # 2. Generate action
    action = generate_payment_delay_action(obligation_id, 7)
    
    # 3. Verify action logged to database
    assert action_exists_in_database(action['action_type'])
    
    # 4. Verify communication draft is not empty
    assert len(action['communication_draft']) > 0
```

---

## 🎯 Success Metrics

### Functional Metrics
- ✅ 100% of actions include Chain-of-Thought reasoning
- ✅ 100% of actions logged to database
- ✅ 0% of actions executed without user approval
- ✅ Tone adapts correctly based on context

### Quality Metrics
- ✅ Communication drafts are under 150 words
- ✅ All required context elements included
- ✅ Tone matches vendor relationship
- ✅ No financial hallucinations (amounts, dates)

### Performance Metrics
- ✅ Action generation < 2 seconds
- ✅ Zombie detection < 1 second
- ✅ API response time < 500ms

---

## 🚀 Future Enhancements

### Phase 2 Features (Post-Hackathon)

1. **Multi-Agent Negotiation**
   - Autonomous back-and-forth with vendors
   - Parse vendor responses
   - Adjust strategy based on counter-offers

2. **Sentiment Analysis**
   - Analyze vendor email responses
   - Adjust future tone based on sentiment
   - Flag hostile relationships

3. **A/B Testing**
   - Test different communication styles
   - Track approval rates
   - Optimize prompts based on results

4. **Email Integration**
   - Actually send emails via Gmail API
   - Track open rates
   - Parse responses automatically

5. **Inventory Liquidation**
   - Connect to Shopify/Square
   - Generate flash sale campaigns
   - Calculate optimal discount rates

---

## 📚 Key Takeaways

1. **AI is a Translator, Not a Decider**: Stream 3 never makes financial decisions
2. **Context is King**: Relationship history drives tone and approach
3. **Human Approval Required**: All actions logged, none executed automatically
4. **Explainability Matters**: Chain-of-Thought builds user trust
5. **Safety First**: Multiple guardrails prevent financial errors

---

**Stream 3 Architecture: Where Math Meets Empathy 🤖💬**
