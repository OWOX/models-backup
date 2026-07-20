---
type: "OWOX Data Mart"
title: "Support Tickets"
description: "One row per support ticket — CSAT and churn-risk signal."
resource: "https://app.owox.com/api/external/http-data/data-marts/2d17b79d-e958-4853-aa45-195d29804041.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-20T16:43:07.000Z
---

# Support Tickets

One row per support ticket — CSAT and churn-risk signal.

## Overview

- **ID:** `2d17b79d-e958-4853-aa45-195d29804041`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [SaaS] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/2d17b79d-e958-4853-aa45-195d29804041.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `ticket_id` | STRING | PK. Unique support-ticket identifier. |
| `account_id` | STRING | Account that opened the ticket. FK to [Account](./account.md) |
| `opened_at` | TIMESTAMP | When the ticket was opened. |
| `closed_at` | TIMESTAMP | When the ticket was closed. |
| `priority` | STRING | Ticket priority level. |
| `category` | STRING | Ticket topic/category. |
| `csat_score` | INTEGER | Customer satisfaction rating for the ticket. |
| `first_response_mins` | INTEGER | Minutes to first agent response. |

## Joins

- [Account](./account.md) — `account_id = account_id`
