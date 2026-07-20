---
type: "OWOX Data Mart"
title: "Trials"
description: "One row per trial. Trial-to-paid conversion without discounting."
resource: "https://app.owox.com/api/external/http-data/data-marts/fd4b3c2b-1c54-4fb4-9f8e-22d89122dc34.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-20T16:43:08.000Z
---

# Trials

One row per trial. Trial-to-paid conversion without discounting.

## Overview

- **ID:** `fd4b3c2b-1c54-4fb4-9f8e-22d89122dc34`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [SaaS] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/fd4b3c2b-1c54-4fb4-9f8e-22d89122dc34.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `trial_id` | STRING | PK. Unique trial identifier. |
| `account_id` | STRING | Account running the trial. FK to [Account](./account.md) |
| `started_at` | TIMESTAMP | When the trial began. |
| `ends_at` | TIMESTAMP | Scheduled trial expiry. |
| `converted_at` | TIMESTAMP | When the trial converted to a paid plan, if it did. |
| `is_converted` | BOOLEAN | Trial-to-paid outcome flag. |
| `trial_source` | STRING | Where the trial came from (self-serve, sales-assisted, PLG upsell). |
| `requested_plan` | STRING | Plan tier the trial is evaluating. |

## Joins

- [Account](./account.md) — `account_id = account_id`
