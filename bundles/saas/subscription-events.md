---
type: "OWOX Data Mart"
title: "Subscription Events"
description: "One row per subscription change. Reconstructs the MRR waterfall and NRR/GRR."
resource: "https://app.owox.com/api/external/http-data/data-marts/7f6b2c12-d6e3-4813-b72b-d379645601e5.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-20T16:43:07.000Z
---

# Subscription Events

One row per subscription change. Reconstructs the MRR waterfall and NRR/GRR.

## Overview

- **ID:** `7f6b2c12-d6e3-4813-b72b-d379645601e5`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [SaaS] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/7f6b2c12-d6e3-4813-b72b-d379645601e5.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `event_id` | STRING | PK. Unique subscription-event identifier. |
| `account_id` | STRING | Account the event belongs to. FK to [Account](./account.md) |
| `event_ts` | TIMESTAMP | When the subscription change occurred. |
| `event_type` | STRING | new / upgrade / downgrade / reactivation / churn. |
| `plan_from` | STRING | Plan before the change. |
| `plan_to` | STRING | Plan after the change. |
| `mrr_delta` | NUMERIC | Signed MRR change — the MRR-movement waterfall. |
| `seats_delta` | INTEGER | Signed change in seat count. |
| `mrr_after` | NUMERIC | Total MRR after the change. |

## Joins

- [Account](./account.md) — `account_id = account_id`
