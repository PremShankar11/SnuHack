# Stream 3 Quick Start Guide

## 🚀 Quick Setup (5 minutes)

```bash
# 1. Install dependencies
cd SnuHack/cashpilot/backend
pip install google-generativeai langchain langchain-google-genai

# 2. Set up Gemini API key
# Add to .env file:
GEMINI_API_KEY=your_api_key_here

# 3. Create module structure
mkdir -p backend/ai
touch backend/ai/__init__.py
touch backend/ai/action_generator.py
touch backend/ai/zombie_detector.py
touch backend/api/ai_router.py

# 4. Start backend
uvicorn main:app --reload
```

---

## 📋 Implementation Checklist

### Phase 1: Core AI Features (2 hours)
- [ ] Create `ai/action_generator.py`
  - [ ] `generate_payment_delay_action()` function
  - [ ] `generate_receivable_acceleration_action()` function
  - [ ] Gemini API integration
  - [ ] Context-aware tone selection

- [ ] Create `ai/zombie_detector.py`
  - [ ] `detect_zombie_subscriptions()` function
  - [ ] Pattern matching for recurring charges
  - [ ] `generate_cancellation_action()` function

### Phase 2: API & Integration (1 hour)
- [ ] Create `api/ai_router.py`
  - [ ] POST `/api/ai/generate-payment-delay`
  - [ ] POST `/api/ai/generate-receivable-acceleration`
  - [ ] GET `/api/ai/detect-zombie-spend`
  - [ ] GET `/api/ai/actions`
  - [ ] `_log_action_to_database()` helper

- [ ] Update `main.py`
  - [ ] Import AI router
  - [ ] Register AI router

### Phase 3: Testing (30 minutes)
- [ ] Test payment delay generation
- [ ] Test receivable acceleration
- [ ] Test zombie spend detection
- [ ] Verify action logging to database
- [ ] Test integration with Stream 2 optimizer

---

## 🧪 Quick Test Commands

```bash
# Test Payment Delay
curl -X POST http://localhost:8000/api/ai/generate-payment-delay \
  -H "Content-Type: application/json" \
  -d '{"obligation_id": "UUID", "delay_days": 7, "fractional_payment": 500}'

# Test Receivable Acceleration
curl -X POST http://localhost:8000/api/ai/generate-receivable-acceleration \
  -H "Content-Type: application/json" \
  -d '{"obligation_id": "UUID", "discount_percentage": 3.0, "urgency_days": 5}'

# Test Zombie Detection
curl http://localhost:8000/api/ai/detect-zombie-spend

# Get Pending Actions
curl http://localhost:8000/api/ai/actions
```

---

## 🎯 Key Concepts

### 1. AI Never Decides
- Stream 2 (math) makes all financial decisions
- Stream 3 (AI) only translates decisions into language
- No LLM is used for calculations or strategy

### 2. Context-Aware Communication
- Tone adapts based on:
  - Vendor tier (0-3)
  - Goodwill score (0-100)
  - Relationship history
  - Payment amount

### 3. Action Logging
- All AI actions logged to `action_logs` table
- Status: `PENDING_USER_APPROVAL`
- Includes Chain-of-Thought reasoning
- Full audit trail for compliance

---

## 📊 Data Flow

```
Stream 2 Output (LP Optimizer)
    ↓
    {
      "optimized_obligations": [
        {
          "obligation_id": "123",
          "delay_amount": 500,
          "pay_now": 1500,
          "new_due_date": "2026-04-15"
        }
      ]
    }
    ↓
Stream 3 Input (Action Generator)
    ↓
    generate_payment_delay_action(
      obligation_id="123",
      delay_days=7,
      fractional_payment=1500
    )
    ↓
Stream 3 Output (AI-Generated Action)
    ↓
    {
      "action_type": "PAYMENT_DELAY",
      "communication_draft": "Dear Vendor...",
      "tone": "PROFESSIONAL_RESPECTFUL",
      "reasoning": "1. Vendor Tier: 2...",
      "requires_approval": true
    }
    ↓
Logged to Database (action_logs table)
    ↓
Frontend Action Inbox (User Reviews & Approves)
```

---

## 🔑 Key Functions

### Action Generator

```python
# Generate payment delay communication
action = generate_payment_delay_action(
    obligation_id="uuid",
    delay_days=7,
    fractional_payment=500.00  # Optional
)

# Generate receivable acceleration
action = generate_receivable_acceleration_action(
    obligation_id="uuid",
    discount_percentage=3.0,
    urgency_days=5
)
```

### Zombie Detector

```python
# Detect unused subscriptions
zombies = detect_zombie_subscriptions(company_id)

# Generate cancellation action
action = generate_cancellation_action(entity_id)
```

---

## 🎨 Tone Selection Logic

```python
if tier == 0:
    tone = "FORMAL_URGENT"  # Critical obligations
elif goodwill_score >= 80:
    tone = "FRIENDLY_CONFIDENT"  # Strong relationships
elif goodwill_score >= 50:
    tone = "PROFESSIONAL_RESPECTFUL"  # Moderate relationships
else:
    tone = "FORMAL_APOLOGETIC"  # Weak relationships
```

---

## 📝 Example Outputs

### Payment Delay (High Goodwill)
```
Hi [Vendor],

I hope this message finds you well. Due to a temporary cash flow timing 
issue with a major client payment, I'm writing to request a brief 7-day 
extension on our upcoming invoice.

As a gesture of good faith, I'm processing a partial payment of $1,500 
today, with the remaining balance scheduled for April 15th.

We truly value our 3-year partnership and appreciate your understanding.

Best regards,
[Your Name]
```

### Receivable Acceleration
```
Hi [Client],

I wanted to reach out with a time-sensitive opportunity. If you're able 
to settle Invoice #4421 by Friday (5 days early), we're offering a 3% 
early payment discount—saving you $150.

New amount: $4,850 (originally $5,000)

This offer is valid through Friday, April 12th. Let me know if you'd 
like to take advantage of this!

Best,
[Your Name]
```

---

## 🐛 Common Issues

### Issue: Gemini API Key Not Found
```bash
# Solution: Add to .env
echo "GEMINI_API_KEY=your_key_here" >> .env
```

### Issue: Action Not Logged to Database
```python
# Check database connection
from core.db import get_db_connection
conn = get_db_connection()
print(conn)  # Should not be None
```

### Issue: Tone Not Adapting
```python
# Verify goodwill scores in database
SELECT name, goodwill_score, ontology_tier FROM entities;
```

---

## 🎯 Success Metrics

✅ AI generates contextually appropriate emails
✅ Tone adapts based on vendor relationship
✅ All actions logged to database
✅ Zombie spend detector finds subscriptions
✅ Receivable acceleration creates urgency
✅ Chain-of-Thought reasoning is clear
✅ No financial decisions made by AI

---

## 🚀 Next Steps

1. **Complete Stream 3 Implementation** (3-4 hours)
2. **Build Frontend Action Inbox** (Stream 4)
3. **Integrate with Stream 2 Optimizer**
4. **End-to-End Testing**
5. **Polish & Demo Prep**

---

## 📚 Additional Resources

- **Full Plan**: `stream3_plan.md`
- **Stream 2 Integration**: `stream2_plan.md`
- **Database Schema**: `schema.sql`
- **Gemini API Docs**: https://ai.google.dev/docs

---

**Stream 3 transforms cold math into warm human relationships! 🤖💬**
