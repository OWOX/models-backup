---
type: "OWOX Data Mart"
title: "🥈 Orders (E-Commerce)"
description: "This data mart contains transaction-level records for all completed and in-progress orders, enabling analysis of customer purchasing behavior, order timelines, and fulfillment status. Each row repr..."
resource: "https://app.owox.com/api/external/http-data/data-marts/d565c4cb-5f68-480e-917d-c1709b59ae02.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-06-08T11:42:26.000Z
---

# 🥈 Orders (E-Commerce)

This data mart contains transaction-level records for all completed and in-progress orders, enabling analysis of customer purchasing behavior, order timelines, and fulfillment status. Each row represents a single order, linked to both a customer and a session, allowing you to track conversions and attribute purchases to user activity

## Overview

- **ID:** `d565c4cb-5f68-480e-917d-c1709b59ae02`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/d565c4cb-5f68-480e-917d-c1709b59ae02.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `session_id` | STRING | Unique identifier of the session where the order was placed |
| `customer_id` | INTEGER | Unique identifier of the customer who placed the order |
| `order_date` | DATE | The date when the transaction was completed |
| `order_id` | STRING | Unique identifier of the purchase transaction |
| `status` | STRING | Current fulfillment state of the order (e.g., Completed) |

## Joins

- [Products](./products-e-commerce.md)
- [Purchases](./purchases-e-commerce.md)
- [Customers](./customers-e-commerce.md)
- [Sessions](./sessions-e-commerce.md)
