# Circadia — Health Metrics Pipeline

**Purpose:** Fitbit → DuckDB → ML scoring for health insights

## Current State

Submodule under Gladiator. Technical pipeline exists but goals not defined.

---

## What Circadia Should Do

1. **Ingest** - Pull data from Fitbit daily
2. **Store** - Store in DuckDB for analysis
3. **Score** - Apply ML models to score health metrics
4. **Alert** - Notify when metrics are concerning

---

## Problems to Solve

| Problem | Current | Target |
|---------|---------|--------|
| Health data not analyzed | Raw Fitbit data exists | Actionable insights |
| Don't know what metrics mean | Data but no signal | Clear scores |
| No early warning system | React to problems | Proactive alerts |

---

## The Evolution Loop

1. **Measure** - Get health data (sleep, HR, activity)
2. **Identify** - What's the pattern? What's concerning?
3. **Build** - Create scoring models
4. **Observe** - Are the scores accurate?
5. **Iterate** - Improve models

**Goal:** Move from data → insights → predictions → autonomous

---

## Next Actions

- [ ] Ensure Fitbit data is syncing
- [ ] Define key metrics to score
- [ ] Build scoring model
- [ ] Set up alerts for concerning metrics