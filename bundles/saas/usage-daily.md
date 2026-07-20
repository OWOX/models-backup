---
type: "OWOX Data Mart"
title: "Usage (daily)"
description: "One row per account × user × day of product usage. Engagement and activation."
resource: "https://app.owox.com/api/external/http-data/data-marts/3f271fcb-c1f6-4cb2-8914-86b73fb55675.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-20T16:43:09.000Z
---

# Usage (daily)

One row per account × user × day of product usage. Engagement and activation.

## Overview

- **ID:** `3f271fcb-c1f6-4cb2-8914-86b73fb55675`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [SaaS] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/3f271fcb-c1f6-4cb2-8914-86b73fb55675.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `usage_id` | STRING | PK. Unique daily-usage record identifier. |
| `account_id` | STRING | Account that generated the usage. FK to [Account](./account.md) |
| `user_id` | STRING | User that generated the usage. FK to [User](./user.md) |
| `usage_date` | DATE | Calendar day of the usage. |
| `active_minutes` | INTEGER | Minutes the user was active in-product. |
| `key_actions` | INTEGER | Count of high-value actions taken. |
| `feature_adoption_score` | FLOAT | Breadth of features touched — activation signal. |

## Joins

- [Account](./account.md) — `account_id = account_id`
- [User](./user.md) — `user_id = user_id`
