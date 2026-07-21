---
type: "OWOX Data Mart"
title: "Plan"
description: "One row per sellable plan/price point. Fixed catalog of 4 tiers × 2 billing intervals."
resource: "https://app.owox.com/api/external/http-data/data-marts/f7dfcbdd-b9a5-4dd1-ba7d-c2ae5c1837c2.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-21T13:36:33.000Z
---

# Plan

One row per sellable plan/price point. Fixed catalog of 4 tiers × 2 billing intervals.

## Overview

- **ID:** `f7dfcbdd-b9a5-4dd1-ba7d-c2ae5c1837c2`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [SaaS] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/f7dfcbdd-b9a5-4dd1-ba7d-c2ae5c1837c2.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `plan_id` | STRING | PK. Unique plan/price-point identifier. |
| `plan_name` | STRING | Human-readable plan name (tier + billing interval). |
| `tier` | STRING | Product tier: Starter / Pro / Business / Enterprise. |
| `billing_interval` | STRING | Billing cadence: monthly / annual. |
| `list_price` | NUMERIC | Published list price for this plan at this interval. |
| `currency` | STRING | Currency of the list price. |
| `is_active` | BOOLEAN | Whether the plan is currently sellable. |
