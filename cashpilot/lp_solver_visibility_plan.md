# LP Solver & Monte Carlo Data Visibility Plan

## Problem Statement
The LP solver optimization data and Monte Carlo analytics are not clearly visible on the dashboard. We need to:
1. Make LP solver data more prominent on the home page (Dashboard)
2. Display LP solver data on the Analytics page
3. Display Monte Carlo data on the Dashboard home page
4. Ensure all data is working correctly and visible without errors

## Current State Analysis

### Backend (Working)
- **LP Solver**: `/api/quant/optimize` endpoint exists and returns optimization data
- **Monte Carlo**: `/api/quant/monte-carlo` endpoint exists and returns simulation data
- **Dashboard API**: `/api/dashboard` already fetches LP optimization data
- **Analytics API**: `/api/analytics` has placeholder Monte Carlo data (not using real endpoint)

### Frontend (Partially Working)
- **Dashboard Page** (`app/page.tsx`):
  - ✅ LP solver data IS displayed (optimization section at bottom)
  - ❌ Monte Carlo data NOT displayed
  - Issue: LP section only shows when `optimization.status !== "UNAVAILABLE"`
  
- **Analytics Page** (`app/analytics/page.tsx`):
  - ❌ LP solver data NOT displayed
  - ⚠️ Monte Carlo data uses placeholder calculations (not real API)

## Implementation Plan

### Phase 1: Backend Integration (Ensure Real Data Flow)

#### Task 1.1: Update Analytics API to Use Real Monte Carlo Data
**File**: `backend/api/dashboard_router.py`
**Changes**:
- Import `run_monte_carlo_simulation` from `quant.monte_carlo`
- Replace placeholder Monte Carlo calculations in `/api/analytics` with real API call
- Add error handling with graceful fallback

**Expected Output**: Analytics endpoint returns real Monte Carlo simulation data

---

### Phase 2: Frontend - Dashboard Home Page Enhancements

#### Task 2.1: Add Monte Carlo Widget to Dashboard
**File**: `app/page.tsx`
**Changes**:
- Fetch Monte Carlo data from `/api/quant/monte-carlo` endpoint
- Create new "Monte Carlo Survival Analysis" card
- Display:
  - Survival probability (with visual indicator)
  - P10/Median/P90 balance projections
  - Number of simulations run
- Position: Below LP Optimization section or in a new grid row

**Design**:
```
┌─────────────────────────────────────────┐
│ Monte Carlo Survival Analysis          │
│ ─────────────────────────────────────── │
│ Survival Probability: 73%              │
│ [Progress bar visualization]            │
│                                         │
│ P10 (Bear):  $2,450                    │
│ Median:      $4,890                    │
│ P90 (Bull):  $7,320                    │
│                                         │
│ Based on 10,000 simulations            │
└─────────────────────────────────────────┘
```

#### Task 2.2: Enhance LP Solver Visibility
**File**: `app/page.tsx`
**Changes**:
- Always show LP Optimization section (even when no optimization needed)
- Add visual indicators for optimization status
- Improve error state messaging
- Add loading states

---

### Phase 3: Frontend - Analytics Page Enhancements

#### Task 3.1: Add LP Solver Optimization Section
**File**: `app/analytics/page.tsx`
**Changes**:
- Fetch LP optimization data from `/api/quant/optimize` endpoint
- Create new section showing:
  - Optimization status
  - List of optimized obligations (if any)
  - Total delayed amounts
  - Projected savings
  - Breach prevention status
- Position: Below Monte Carlo and Goodwill Radar sections

**Design**:
```
┌─────────────────────────────────────────┐
│ LP Optimization Strategy                │
│ ─────────────────────────────────────── │
│ Status: SUCCESS                         │
│ Breach Prevented: Yes                   │
│                                         │
│ Optimized Obligations:                  │
│ • Vendor A: Pay $500, Delay $200       │
│ • Vendor B: Pay $300, Delay $400       │
│                                         │
│ Total Deferred: $600                   │
│ Projected Savings: $150                │
└─────────────────────────────────────────┘
```

#### Task 3.2: Update Monte Carlo to Use Real Data
**File**: `app/analytics/page.tsx`
**Changes**:
- Verify Monte Carlo section uses data from updated `/api/analytics` endpoint
- Ensure it displays real simulation results (not placeholder)

---

### Phase 4: Testing & Validation

#### Task 4.1: Backend API Testing
**Tests**:
1. Test `/api/quant/optimize` endpoint directly
2. Test `/api/quant/monte-carlo` endpoint directly
3. Test `/api/dashboard` returns LP data
4. Test `/api/analytics` returns real Monte Carlo data
5. Verify error handling and fallbacks

**Commands**:
```bash
# Test LP Optimizer
curl http://localhost:8000/api/quant/optimize

# Test Monte Carlo
curl http://localhost:8000/api/quant/monte-carlo

# Test Dashboard
curl http://localhost:8000/api/dashboard

# Test Analytics
curl http://localhost:8000/api/analytics
```

#### Task 4.2: Frontend Integration Testing
**Tests**:
1. Load Dashboard page - verify LP section visible
2. Load Dashboard page - verify Monte Carlo section visible
3. Load Analytics page - verify LP section visible
4. Load Analytics page - verify Monte Carlo uses real data
5. Test with simulation slider - verify data updates
6. Test error states (backend down)
7. Test loading states

#### Task 4.3: Visual Verification
**Checklist**:
- [ ] Dashboard shows LP optimization data clearly
- [ ] Dashboard shows Monte Carlo survival probability
- [ ] Analytics shows LP optimization strategy
- [ ] Analytics shows real Monte Carlo data (not placeholder)
- [ ] All sections have proper loading states
- [ ] All sections have proper error handling
- [ ] Data updates when simulation slider moves
- [ ] No console errors
- [ ] Responsive design works on different screen sizes

---

## File Changes Summary

### Backend Files to Modify:
1. `backend/api/dashboard_router.py` - Update `/api/analytics` endpoint

### Frontend Files to Modify:
1. `app/page.tsx` - Add Monte Carlo widget, enhance LP visibility
2. `app/analytics/page.tsx` - Add LP section, verify Monte Carlo data

### New Components (Optional):
- `app/components/MonteCarloCard.tsx` - Reusable Monte Carlo display
- `app/components/LPOptimizationCard.tsx` - Reusable LP optimization display

---

## Success Criteria

### Must Have:
✅ LP solver data visible on Dashboard home page
✅ LP solver data visible on Analytics page
✅ Monte Carlo data visible on Dashboard home page
✅ Monte Carlo data on Analytics uses real API (not placeholder)
✅ No console errors
✅ Data updates correctly with simulation slider

### Nice to Have:
- Loading skeletons for all data sections
- Smooth transitions when data updates
- Tooltips explaining metrics
- Export/download functionality for optimization results

---

## Risk Mitigation

### Potential Issues:
1. **Backend API failures**: Add try-catch with graceful fallbacks
2. **Data format mismatches**: Validate API response structure
3. **Performance**: Monte Carlo runs 10k simulations - ensure it doesn't block
4. **UI clutter**: Keep design clean and organized

### Fallback Strategy:
- If LP solver fails: Show "Optimization unavailable" message
- If Monte Carlo fails: Show "Simulation unavailable" message
- Always show last successful data with timestamp

---

## Implementation Order

1. **Backend First**: Update analytics API to use real Monte Carlo (Task 1.1)
2. **Test Backend**: Verify all endpoints return correct data (Task 4.1)
3. **Dashboard Updates**: Add Monte Carlo to home page (Task 2.1, 2.2)
4. **Analytics Updates**: Add LP section (Task 3.1, 3.2)
5. **Integration Testing**: Full end-to-end testing (Task 4.2, 4.3)

---

## Estimated Timeline

- Phase 1 (Backend): 15 minutes
- Phase 2 (Dashboard): 30 minutes
- Phase 3 (Analytics): 30 minutes
- Phase 4 (Testing): 20 minutes

**Total**: ~1.5 hours

---

## Notes

- All changes maintain existing functionality
- No breaking changes to current UI
- Backward compatible with existing data structures
- Focus on clarity and usability
