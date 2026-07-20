---
type: "OWOX Data Mart"
title: "User"
description: "One row per user seat within an account."
resource: "https://app.owox.com/api/external/http-data/data-marts/6c047c34-a01d-44b8-b294-1340685392e3.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-20T16:43:08.000Z
---

# User

One row per user seat within an account.

## Overview

- **ID:** `6c047c34-a01d-44b8-b294-1340685392e3`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [SaaS] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/6c047c34-a01d-44b8-b294-1340685392e3.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | STRING | PK. Unique user identifier. |
| `account_id` | STRING | Owning account. FK to [Account](./account.md) |
| `email` | STRING | User's email address. |
| `role` | STRING | User's role within the account. |
| `seat_type` | STRING | Type of seat assigned (e.g. full / viewer). |
| `invited_at` | TIMESTAMP | When the user was invited. |
| `last_active_at` | TIMESTAMP | Most recent activity timestamp. |
| `is_active` | BOOLEAN | Whether the seat is currently active. |

## Joins

- [Account](./account.md) — `account_id = account_id`
