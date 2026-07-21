---
type: "OWOX Data Mart"
title: "Invoices"
description: "One row per invoice. Billing, collections and dunning."
resource: "https://app.owox.com/api/external/http-data/data-marts/393ca959-5c23-433f-8b07-b5490c5c2fb9.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-21T13:31:06.000Z
---

# Invoices

One row per invoice. Billing, collections and dunning.

## Overview

- **ID:** `393ca959-5c23-433f-8b07-b5490c5c2fb9`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [SaaS] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/393ca959-5c23-433f-8b07-b5490c5c2fb9.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `invoice_id` | STRING | PK. Unique invoice identifier. |
| `account_id` | STRING | Account billed. FK to [Account](./account.md) |
| `subscription_id` | STRING | Subscription being billed. FK to [Subscription](./subscription.md) |
| `issued_at` | DATE | Date the invoice was issued. |
| `period_start` | DATE | Start of the billing period. |
| `period_end` | DATE | End of the billing period. |
| `amount` | NUMERIC | Invoice amount before tax. |
| `tax` | NUMERIC | Tax charged on the invoice. |
| `status` | STRING | Payment status of the invoice. |
| `currency` | STRING | Invoice currency, aligned to the account's region. |
| `discount_amount` | NUMERIC | Discount applied to the invoice, if any. |
| `credit_applied` | NUMERIC | Account credit applied to the invoice, if any. |
| `dunning_stage` | STRING | Collections stage: none / retry_1 / retry_2 / final_notice / write_off. |
| `paid_at` | DATE | Date the invoice was paid. |
| `is_failed` | BOOLEAN | Failed payment — involuntary-churn signal. |

## Joins

- [Account](./account.md) — `account_id = account_id`
- [Subscription](./subscription.md) — `subscription_id = subscription_id`
