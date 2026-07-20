---
type: "OWOX Data Mart"
title: "Account"
description: "One row per customer account (company). Firmographics, plan tier and health."
resource: "https://app.owox.com/api/external/http-data/data-marts/d9c55dd4-84b1-474a-9262-038ec0fa1f30.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-20T16:43:05.000Z
---

# Account

One row per customer account (company). Firmographics, plan tier and health.

## Overview

- **ID:** `d9c55dd4-84b1-474a-9262-038ec0fa1f30`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [SaaS] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/d9c55dd4-84b1-474a-9262-038ec0fa1f30.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `account_id` | STRING | PK. Unique account identifier. |
| `name` | STRING | Company/account name. |
| `industry` | STRING | Industry vertical of the account. |
| `employee_band` | STRING | Company-size bucket by headcount. |
| `plan_tier` | STRING | Subscription plan tier. |
| `mrr_band` | STRING | Monthly-recurring-revenue size bucket. |
| `region` | STRING | Sales/geographic region. |
| `acquisition_channel` | STRING | Marketing channel that sourced the account — blended-CAC join key. |
| `signup_date` | DATE | Date the account first signed up. |
| `csm_owner` | STRING | Customer success manager who owns the account. |
| `health_score` | INTEGER | 0–100 product-health composite. |
| `lifecycle_stage` | STRING | trial / active / at-risk / churned. |
