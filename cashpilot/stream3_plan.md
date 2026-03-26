# Stream 3 Implementation Plan: AI Orchestrator (Autonomous Agents & Execution)

## 🎯 Overview

Stream 3 is the **AI-powered execution layer** of CashPilot. While Stream 2 provides the mathematical brain (deterministic calculations), Stream 3 translates those decisions into real-world actions using AI agents.

**Core Principle**: The AI never makes financial decisions—it only executes strategies determined by the mathematical engine.

---

## 📊 Current Status

✅ **Phase 1 Complete**: Data ingestion, database, simulation engine
✅ **Phase 2 Complete**: Mathematical optimization engine (LP solver, Monte Carlo, Runway)
🎯 **Phase 3 Target**: Build autonomous AI agents that execute payment strategies

---

## 🎭 Core Responsibilities

Stream 3 transforms mathematical outputs into human-readable actions:

1. **Context-Aware Communication**: Draft emails/messages tailored to vendor relationships
2. **Multi-Agent Negotiation**: Autonomous back-and-forth with vendors
3. **Bi-Directional Liquidity**: Accelerate receivables, not just delay payables
4. **Zombie Spend Detection**: Identify and eliminate unused subscriptions
5. **Inventory Liquidation**: Generate emergency cash through flash sales

---

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **Framework**: FastAPI (already set up)
- **AI/LLM**: Google Gemini 1.5 Pro API
- **Agent Framework**: LangChain or custom implementation
- **Email Integration**: Gmail API (mocked for hackathon)
- **E-commerce**: Shopify/Square API (mocked for hackathon)

---

## 📦 Installation

```bash
cd SnuHack/cashpilot/backend
pip install google-generativeai langchain langchain-google-genai
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAM 3 ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────┘

Stream 2 (Math Engine)
    ↓
    ├─→ LP Optimizer Output (who to delay, by how much)
    ├─→ Monte Carlo Output (survival probability)
    └─→ Runway Output (days to zero)
    
Stream 3 (AI Orchestrator)
    ↓
    ├─→ Action Generator (draft emails/messages)
    ├─→ Negotiation Agent (autonomous back-and-forth)
    ├─→ Receivables Accelerator (incentivize early payment)
    ├─→ Zombie Spend Detector (find unused subscriptions)
    └─→ Inventory Liquidator (emergency flash sales)
    
Output: Action Logs (stored in database for user approval)
```

---

## 📋 Implementation Tasks

### Task 1: Create AI Module Structure

**Directory Structure**:
```
backend/
├── ai/
│   ├── __init__.py
│   ├── action_generator.py      # Draft contextual communications
│   ├── negotiation_agent.py     # Multi-turn vendor negotiations
│   ├── receivables_accelerator.py  # Speed up incoming payments
│   ├── zombie_detector.py       # Find unused subscriptions
│   └── inventory_liquidator.py  # Emergency cash generation
├── api/
│   └── ai_router.py             # AI endpoints
└── main.py (update to include AI router)
```

---

### Task 2: Implement Action Generator

**Purpose**: Convert mathematical optimization decisions into human-readable, contextually appropriate communications.

**File**: `backend/ai/action_generator.py`

```python
"""
Action Generator - Context-aware communication drafting.

Takes LP optimizer output and generates vendor-specific communications
based on relationship history, tier classification, and goodwill scores.

ZERO FINANCIAL DECISIONS - Only translates math into language.
"""

import google.generativeai as genai
from typing import Dict, List
from core.db import get_db_connection
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_payment_delay_action(
    obligation_id: str,
    delay_days: int,
    fractional_payment: float = None
) -> Dict:
    """
    Generates a contextual communication for delaying a payment.
    
    Args:
        obligation_id: UUID of the obligation
        delay_days: Number of days to delay
        fractional_payment: Optional partial payment amount
    
    Returns:
        {
            "action_type": "PAYMENT_DELAY",
            "communication_draft": str,
            "tone": str,
            "reasoning": str,
            "entity_context": Dict
        }
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get obligation and entity details
        cur.execute(
            """
            SELECT o.amount, o.due_date, o.description,
                   e.name, e.entity_type, e.goodwill_score, 
                   e.ontology_tier, e.relationship_notes
            FROM obligations o
            JOIN entities e ON o.entity_id = e.id
            WHERE o.id = %s;
            """,
            (obligation_id,)
        )
        data = cur.fetchone()
        
        if not data:
            raise ValueError("Obligation not found")
        
        # Build context for LLM
        context = {
            "vendor_name": data['name'],
            "amount": abs(float(data['amount'])),
            "original_due": data['due_date'].strftime("%B %d, %Y"),
            "delay_days": delay_days,
            "goodwill_score": data['goodwill_score'],
            "tier": data['ontology_tier'],
            "relationship_notes": data['relationship_notes'] or "No prior notes",
            "fractional_payment": fractional_payment
        }
        
        # Determine tone based on tier and goodwill
        if context['tier'] == 0:
            tone = "FORMAL_URGENT"  # Should never delay Tier 0, but handle edge case
        elif context['goodwill_score'] >= 80:
            tone = "FRIENDLY_CONFIDENT"
        elif context['goodwill_score'] >= 50:
            tone = "PROFESSIONAL_RESPECTFUL"
        else:
            tone = "FORMAL_APOLOGETIC"
        
        # Generate communication using Gemini
        prompt = f"""You are a financial communication specialist. Draft a professional email requesting a payment extension.

Context:
- Vendor: {context['vendor_name']}
- Original Amount: ${context['amount']:,.2f}
- Original Due Date: {context['original_due']}
- Requested Extension: {delay_days} days
- Relationship Quality: {context['goodwill_score']}/100
- Relationship History: {context['relationship_notes']}
- Tone: {tone}

{"- Partial Payment Offered: $" + f"{fractional_payment:,.2f}" if fractional_payment else ""}

Requirements:
1. Be concise (under 150 words)
2. Acknowledge the relationship history
3. Provide a clear reason (cash flow timing, not financial distress)
4. Offer specific new payment date
5. {"Emphasize the good-faith partial payment" if fractional_payment else "Express commitment to the relationship"}
6. Use appropriate tone: {tone}

Draft the email body only (no subject line):"""

        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        
        communication_draft = response.text.strip()
        
        # Generate reasoning for Chain-of-Thought
        reasoning = f"""
        Decision Rationale:
        1. Vendor Tier: {context['tier']} ({"Critical - Cannot delay" if context['tier'] == 0 else "Flexible"})
        2. Goodwill Score: {context['goodwill_score']}/100 ({"Strong relationship" if context['goodwill_score'] >= 70 else "Moderate relationship"})
        3. Extension: {delay_days} days maintains positive cash flow
        4. {"Partial payment of ${fractional_payment:,.2f} demonstrates good faith" if fractional_payment else "Full payment deferred to maintain liquidity"}
        5. Tone: {tone} based on relationship strength
        """
        
        return {
            "action_type": "PAYMENT_DELAY",
            "obligation_id": obligation_id,
            "communication_draft": communication_draft,
            "tone": tone,
            "reasoning": reasoning.strip(),
            "entity_context": context,
            "requires_approval": True
        }
    
    finally:
        cur.close()
        conn.close()


def generate_receivable_acceleration_action(
    obligation_id: str,
    discount_percentage: float,
    urgency_days: int
) -> Dict:
    """
    Generates communication to incentivize early payment from clients.
    
    Args:
        obligation_id: UUID of the receivable
        discount_percentage: Discount offered for early payment (e.g., 3.0 for 3%)
        urgency_days: Days until discount expires
    
    Returns:
        {
            "action_type": "RECEIVABLE_ACCELERATION",
            "communication_draft": str,
            "discount_amount": float,
            "reasoning": str
        }
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get receivable details
        cur.execute(
            """
            SELECT o.amount, o.due_date, o.description,
                   e.name, e.entity_type, e.goodwill_score
            FROM obligations o
            JOIN entities e ON o.entity_id = e.id
            WHERE o.id = %s AND o.amount > 0;
            """,
            (obligation_id,)
        )
        data = cur.fetchone()
        
        if not data:
            raise ValueError("Receivable not found")
        
        amount = float(data['amount'])
        discount_amount = amount * (discount_percentage / 100)
        new_amount = amount - discount_amount
        
        context = {
            "client_name": data['name'],
            "original_amount": amount,
            "discount_percentage": discount_percentage,
            "discount_amount": discount_amount,
            "new_amount": new_amount,
            "urgency_days": urgency_days,
            "original_due": data['due_date'].strftime("%B %d, %Y")
        }
        
        prompt = f"""You are a financial communication specialist. Draft a professional email offering an early payment discount to a client.

Context:
- Client: {context['client_name']}
- Invoice Amount: ${context['original_amount']:,.2f}
- Original Due Date: {context['original_due']}
- Early Payment Discount: {discount_percentage}% (${discount_amount:,.2f} savings)
- New Amount if Paid Early: ${new_amount:,.2f}
- Offer Valid For: {urgency_days} days

Requirements:
1. Be concise and professional (under 120 words)
2. Frame as a win-win opportunity
3. Emphasize the savings amount, not just percentage
4. Create urgency with the deadline
5. Make payment instructions clear
6. Maintain positive tone

Draft the email body only (no subject line):"""

        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        
        communication_draft = response.text.strip()
        
        reasoning = f"""
        Receivable Acceleration Strategy:
        1. Original Amount: ${amount:,.2f}
        2. Discount Offered: {discount_percentage}% (${discount_amount:,.2f})
        3. Net Benefit: Receive ${new_amount:,.2f} immediately vs ${amount:,.2f} on {context['original_due']}
        4. Cash Flow Impact: Accelerates {urgency_days} days of runway
        5. Cost: ${discount_amount:,.2f} (acceptable for liquidity preservation)
        """
        
        return {
            "action_type": "RECEIVABLE_ACCELERATION",
            "obligation_id": obligation_id,
            "communication_draft": communication_draft,
            "discount_percentage": discount_percentage,
            "discount_amount": round(discount_amount, 2),
            "new_amount": round(new_amount, 2),
            "reasoning": reasoning.strip(),
            "requires_approval": True
        }
    
    finally:
        cur.close()
        conn.close()
```

---

### Task 3: Implement Zombie Spend Detector

**Purpose**: Identify unused recurring subscriptions that can be cancelled for immediate cash flow improvement.

**File**: `backend/ai/zombie_detector.py`

```python
"""
Zombie Spend Detector - Identifies unused recurring expenses.

Analyzes transaction patterns to find subscriptions that haven't been
actively used, providing immediate liquidity through cancellation.

ZERO AI/LLM - Pure pattern matching and heuristics.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from core.db import get_db_connection
import re

def detect_zombie_subscriptions(company_id: str, lookback_days: int = 90) -> List[Dict]:
    """
    Identifies recurring expenses that may be unused "zombie spend".
    
    Heuristics:
    - Recurring monthly charges (same amount, same vendor)
    - No corresponding activity/usage indicators
    - Low-priority vendors (Tier 2-3)
    
    Args:
        company_id: UUID of the company
        lookback_days: Days to analyze (default 90)
    
    Returns:
        List of potential zombie subscriptions with cancellation recommendations
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get current date
        cur.execute("SELECT current_simulated_date FROM companies WHERE id = %s;", (company_id,))
        simulated_now = cur.fetchone()['current_simulated_date']
        lookback_start = simulated_now - timedelta(days=lookback_days)
        
        # Find recurring transactions (same vendor, similar amounts, monthly pattern)
        cur.execute(
            """
            SELECT 
                e.id as entity_id,
                e.name as vendor_name,
                e.ontology_tier,
                COUNT(t.id) as transaction_count,
                AVG(t.amount) as avg_amount,
                MIN(t.cleared_date) as first_seen,
                MAX(t.cleared_date) as last_seen
            FROM transactions t
            JOIN entities e ON t.entity_id = e.id
            WHERE t.cleared_date >= %s 
            AND t.amount < 0
            AND e.entity_type = 'VENDOR'
            GROUP BY e.id, e.name, e.ontology_tier
            HAVING COUNT(t.id) >= 2
            ORDER BY AVG(t.amount) DESC;
            """,
            (lookback_start,)
        )
        recurring_vendors = cur.fetchall()
        
        zombie_candidates = []
        
        for vendor in recurring_vendors:
            # Check if it's a subscription pattern (monthly recurring)
            transaction_count = vendor['transaction_count']
            days_active = (vendor['last_seen'] - vendor['first_seen']).days
            
            # Heuristic: If we see 2-3 transactions over 60-90 days, likely monthly subscription
            is_likely_subscription = (
                transaction_count >= 2 and
                days_active >= 25 and
                vendor['ontology_tier'] >= 2  # Only flag non-critical vendors
            )
            
            if is_likely_subscription:
                avg_amount = abs(float(vendor['avg_amount']))
                annual_cost = avg_amount * 12
                
                # Check for common subscription keywords
                vendor_name_lower = vendor['vendor_name'].lower()
                subscription_keywords = ['software', 'saas', 'subscription', 'monthly', 'pro', 'premium', 'cloud']
                is_subscription_vendor = any(keyword in vendor_name_lower for keyword in subscription_keywords)
                
                zombie_candidates.append({
                    "entity_id": str(vendor['entity_id']),
                    "vendor_name": vendor['vendor_name'],
                    "monthly_cost": round(avg_amount, 2),
                    "annual_cost": round(annual_cost, 2),
                    "transaction_count": transaction_count,
                    "first_seen": vendor['first_seen'].isoformat(),
                    "last_seen": vendor['last_seen'].isoformat(),
                    "confidence": "HIGH" if is_subscription_vendor else "MEDIUM",
                    "recommendation": "REVIEW_FOR_CANCELLATION",
                    "impact": f"Cancelling saves ${avg_amount:,.2f}/month (${annual_cost:,.2f}/year)"
                })
        
        return zombie_candidates
    
    finally:
        cur.close()
        conn.close()


def generate_cancellation_action(entity_id: str) -> Dict:
    """
    Generates a cancellation action for a zombie subscription.
    
    Args:
        entity_id: UUID of the vendor entity
    
    Returns:
        Action dict with cancellation instructions
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "SELECT name, contact_email FROM entities WHERE id = %s;",
            (entity_id,)
        )
        vendor = cur.fetchone()
        
        if not vendor:
            raise ValueError("Vendor not found")
        
        # Generate cancellation email draft
        prompt = f"""Draft a professional subscription cancellation email.

Vendor: {vendor['name']}
Tone: Professional but firm

Requirements:
1. Request immediate cancellation
2. Request confirmation of cancellation
3. Ask for final invoice/prorated refund if applicable
4. Thank them for past service
5. Keep under 100 words

Draft the email body:"""

        import google.generativeai as genai
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        
        return {
            "action_type": "SUBSCRIPTION_CANCELLATION",
            "entity_id": entity_id,
            "vendor_name": vendor['name'],
            "communication_draft": response.text.strip(),
            "contact_email": vendor['contact_email'],
            "requires_approval": True
        }
    
    finally:
        cur.close()
        conn.close()
```

---

### Task 4: Create AI Router & Action Logs

**Purpose**: Expose AI capabilities via API endpoints and store all generated actions for user approval.

**File**: `backend/api/ai_router.py`

```python
"""
AI Router - API endpoints for AI-powered actions.

All AI-generated actions are logged to the database for user review/approval.
No actions are executed automatically without user consent.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ai.action_generator import (
    generate_payment_delay_action,
    generate_receivable_acceleration_action
)
from ai.zombie_detector import detect_zombie_subscriptions, generate_cancellation_action
from core.db import get_db_connection
import json
from datetime import datetime

router = APIRouter()


class PaymentDelayRequest(BaseModel):
    obligation_id: str
    delay_days: int
    fractional_payment: Optional[float] = None


class ReceivableAccelerationRequest(BaseModel):
    obligation_id: str
    discount_percentage: float
    urgency_days: int


@router.post("/api/ai/generate-payment-delay")
def generate_payment_delay(request: PaymentDelayRequest):
    """Generate a payment delay communication."""
    try:
        action = generate_payment_delay_action(
            request.obligation_id,
            request.delay_days,
            request.fractional_payment
        )
        
        # Log action to database
        _log_action_to_database(action)
        
        return action
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/ai/generate-receivable-acceleration")
def generate_receivable_acceleration(request: ReceivableAccelerationRequest):
    """Generate a receivable acceleration communication."""
    try:
        action = generate_receivable_acceleration_action(
            request.obligation_id,
            request.discount_percentage,
            request.urgency_days
        )
        
        # Log action to database
        _log_action_to_database(action)
        
        return action
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ai/detect-zombie-spend")
def detect_zombie_spend():
    """Detect unused recurring subscriptions."""
    try:
        # Get first company
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM companies LIMIT 1;")
        company = cur.fetchone()
        cur.close()
        conn.close()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        zombies = detect_zombie_subscriptions(str(company['id']))
        
        return {
            "zombie_subscriptions": zombies,
            "total_monthly_savings": sum(z['monthly_cost'] for z in zombies),
            "total_annual_savings": sum(z['annual_cost'] for z in zombies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/ai/generate-cancellation/{entity_id}")
def generate_cancellation(entity_id: str):
    """Generate a subscription cancellation action."""
    try:
        action = generate_cancellation_action(entity_id)
        
        # Log action to database
        _log_action_to_database(action)
        
        return action
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ai/actions")
def get_pending_actions():
    """Get all pending AI-generated actions awaiting user approval."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT * FROM action_logs 
            WHERE is_resolved = FALSE 
            AND execution_type = 'AI_GENERATED'
            ORDER BY created_at DESC;
            """
        )
        actions = cur.fetchall()
        
        formatted_actions = []
        for action in actions:
            formatted_actions.append({
                "id": str(action['id']),
                "action_type": action['action_type'],
                "message": action['message'],
                "status": action['status'],
                "chain_of_thought": action['chain_of_thought'],
                "execution_payload": action['execution_payload'],
                "created_at": action['created_at'].isoformat()
            })
        
        cur.close()
        conn.close()
        
        return {"actions": formatted_actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _log_action_to_database(action: dict):
    """Helper function to log AI-generated actions to the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get company ID
        cur.execute("SELECT id FROM companies LIMIT 1;")
        company = cur.fetchone()
        
        if not company:
            return
        
        company_id = company['id']
        
        # Insert action log
        cur.execute(
            """
            INSERT INTO action_logs (
                company_id, action_type, message, status,
                chain_of_thought, execution_type, execution_payload, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                company_id,
                action['action_type'],
                f"AI-Generated: {action.get('communication_draft', '')[:100]}...",
                'PENDING_USER_APPROVAL',
                json.dumps({"reasoning": action.get('reasoning', '')}),
                'AI_GENERATED',
                json.dumps(action),
                datetime.now()
            )
        )
        
        conn.commit()
    finally:
        cur.close()
        conn.close()
```

---

### Task 5: Register AI Router in Main App

**File**: `backend/main.py` (add these lines)

```python
# Add after existing router imports
from api.ai_router import router as ai_router

# Add after existing router includes
app.include_router(ai_router, tags=["AI Orchestrator"])
```

---

## 🧪 Testing the Implementation

### Step 1: Start the Backend
```bash
cd SnuHack/cashpilot/backend
uvicorn main:app --reload
```

### Step 2: Test Each AI Endpoint

**Test Payment Delay Generation**:
```bash
curl -X POST http://localhost:8000/api/ai/generate-payment-delay \
  -H "Content-Type: application/json" \
  -d '{
    "obligation_id": "<UUID>",
    "delay_days": 7,
    "fractional_payment": 500.00
  }'
```

**Test Receivable Acceleration**:
```bash
curl -X POST http://localhost:8000/api/ai/generate-receivable-acceleration \
  -H "Content-Type: application/json" \
  -d '{
    "obligation_id": "<UUID>",
    "discount_percentage": 3.0,
    "urgency_days": 5
  }'
```

**Test Zombie Spend Detection**:
```bash
curl http://localhost:8000/api/ai/detect-zombie-spend
```

**Test Get Pending Actions**:
```bash
curl http://localhost:8000/api/ai/actions
```

---

## 🔗 Integration with Stream 2

Stream 3 consumes Stream 2 outputs:

```python
# Example: Automatically generate actions from LP optimizer results
from quant.optimizer import optimize_payment_strategy
from ai.action_generator import generate_payment_delay_action

# Get optimization results
optimization = optimize_payment_strategy(company_id)

# For each optimized obligation, generate AI action
if optimization['status'] == 'SUCCESS':
    for obligation in optimization['optimized_obligations']:
        action = generate_payment_delay_action(
            obligation['obligation_id'],
            delay_days=7,
            fractional_payment=obligation['pay_now']
        )
        # Action is automatically logged to database
```

---

## ✅ Success Criteria

You'll know Stream 3 is complete when:

✅ AI generates contextually appropriate communications
✅ Tone adapts based on vendor tier and goodwill score
✅ All actions are logged to database for user approval
✅ Zombie spend detector identifies recurring subscriptions
✅ Receivable acceleration drafts incentive emails
✅ No financial decisions made by AI (only execution)
✅ Chain-of-Thought reasoning is clear and traceable
✅ API endpoints return valid JSON
✅ Integration with Stream 2 works seamlessly

---

## 📊 Feature Completion Matrix

| Feature | Status | Priority | Estimated Time |
|---------|--------|----------|----------------|
| Action Generator | ⏳ Pending | HIGH | 60 minutes |
| Zombie Spend Detector | ⏳ Pending | MEDIUM | 45 minutes |
| Receivable Accelerator | ⏳ Pending | MEDIUM | 30 minutes |
| AI Router & Logging | ⏳ Pending | HIGH | 30 minutes |
| Integration with Stream 2 | ⏳ Pending | HIGH | 30 minutes |
| Frontend Action Inbox | ⏳ Pending | MEDIUM | 45 minutes |

**Total Estimated Time**: 3-4 hours

---

## 🎯 Key Principles

1. **AI Never Decides**: The mathematical engine (Stream 2) makes all financial decisions
2. **AI Only Executes**: Stream 3 translates math into human language
3. **User Approval Required**: All actions logged to database, awaiting approval
4. **Context-Aware**: Communications adapt to vendor relationships
5. **Explainable**: Every action includes Chain-of-Thought reasoning
6. **Traceable**: Full audit trail in action_logs table

---

## 🚀 Next Steps After Stream 3

Once Stream 3 is complete, you can:
- **Stream 4**: Build the frontend Action Inbox UI
- **Integration**: Connect all streams into a cohesive system
- **Testing**: End-to-end testing with simulation slider
- **Polish**: Add loading states, error handling, animations

---

## 📁 File Structure After Completion

```
backend/
├── ai/
│   ├── __init__.py
│   ├── action_generator.py
│   ├── negotiation_agent.py (optional advanced feature)
│   ├── receivables_accelerator.py (integrated in action_generator)
│   ├── zombie_detector.py
│   └── inventory_liquidator.py (optional advanced feature)
├── api/
│   ├── ai_router.py
│   ├── quant_router.py (from Stream 2)
│   ├── dashboard_router.py
│   └── ...
├── quant/ (from Stream 2)
│   ├── optimizer.py
│   ├── runway_engine.py
│   └── ...
└── main.py (updated)
```

---

## 🔧 Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'google.generativeai'`
**Solution**: `pip install google-generativeai`

**Issue**: Gemini API returns 429 (rate limit)
**Solution**: Add retry logic with exponential backoff

**Issue**: Actions not appearing in database
**Solution**: Check `_log_action_to_database()` function and database connection

---

## 💡 Optional Advanced Features

If you have extra time, consider adding:

1. **Multi-Agent Negotiation**: Autonomous back-and-forth with vendors
2. **Inventory Liquidation**: Connect to Shopify/Square for flash sales
3. **Email Integration**: Actually send emails via Gmail API
4. **Sentiment Analysis**: Analyze vendor responses to adjust strategy
5. **A/B Testing**: Test different communication styles

---

## 📝 Notes

- All AI features use Gemini 1.5 Pro for consistency
- Action logs provide full audit trail for compliance
- System never executes actions without user approval
- Chain-of-Thought reasoning builds user trust
- Context-aware communications improve vendor relationships

---

**Ready to start? Begin with Task 1 and work sequentially. Each task builds on the previous one.**

**Stream 3 is where the magic happens—turning cold math into warm human relationships! 🤖💬**
