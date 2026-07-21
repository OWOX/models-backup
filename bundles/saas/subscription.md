---
type: "OWOX Data Mart"
title: "Subscription"
description: "One row per subscription, current state. Links an account to its plan; carries MRR, seats and billing dates."
resource: "https://app.owox.com/api/external/http-data/data-marts/f24a8aba-2075-4039-a300-6dc31d713b85.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-21T13:36:31.000Z
---

# Subscription

One row per subscription, current state. Links an account to its plan; carries MRR, seats and billing dates.

## Overview

- **ID:** `f24a8aba-2075-4039-a300-6dc31d713b85`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [SaaS] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/f24a8aba-2075-4039-a300-6dc31d713b85.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `subscription_id` | STRING | PK. Unique subscription identifier. |
| `account_id` | STRING | Account that owns the subscription. FK to [Account](./account.md) |
| `plan_id` | STRING | Plan the subscription is billed on. May differ from the account's current tier under grandfathered pricing or a negotiated discount. FK to [Plan](./plan.md) |
| `status` | STRING | Subscription status: trialing / active / past_due / canceled. |
| `seats_licensed` | INTEGER | Number of seats licensed on the subscription. |
| `mrr` | NUMERIC | Monthly recurring revenue for the subscription. |
| `currency` | STRING | Billing currency, aligned to the account's region. |
| `billing_interval` | STRING | Billing cadence: monthly / annual. |
| `started_at` | DATE | Date the subscription started. |
| `current_period_start` | DATE | Start of the current billing period. |
| `current_period_end` | DATE | End of the current billing period. |
| `canceled_at` | DATE | Date the subscription was canceled, if it was. |
| `discount_pct` | NUMERIC | Negotiated discount fraction applied to list price, if any. |

## Joins

- [Account](./account.md) — `account_id = account_id`
- [Plan](./plan.md) — `plan_id = plan_id`
