---
type: "OWOX Data Mart"
title: "🥈 Sessions (E-Commerce)"
description: "This Data Mart provides a detailed log of individual e-commerce browsing sessions, including traffic sources, device types, and conversion outcomes. It is primarily used to analyze user behavior, m..."
resource: "https://app.owox.com/api/external/http-data/data-marts/22a66e81-1ce3-4c0a-8ead-3a154df490ab.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-16T02:42:23.000Z
---

# 🥈 Sessions (E-Commerce)

This Data Mart provides a detailed log of individual e-commerce browsing sessions, including traffic sources, device types, and conversion outcomes. It is primarily used to analyze user behavior, marketing attribution, and website performance across different geographic regions.

## Overview

- **ID:** `22a66e81-1ce3-4c0a-8ead-3a154df490ab`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/22a66e81-1ce3-4c0a-8ead-3a154df490ab.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | The specific date when the browsing session occurred |
| `session_id` | STRING | PK. Unique identifier for an individual user session |
| `customer_id` | INTEGER | Unique identifier of the customer associated with the session FK to [🥈 Customers (E-Commerce)](./customers-e-commerce.md) |
| `device_category` | STRING | The type of hardware device used during the session (e.g., mobile, desktop) |
| `conversion_seed` | FLOAT | A technical value used to simulate the probability of a transaction. |
| `visitor_id` | STRING | Unique identifier for the anonymous or recognized visitor. FK to [🥈 Visitors (E-Commerce)](./visitors-e-commerce.md) |
| `traffic_source_id` | INTEGER | Internal numeric identifier for the marketing traffic source. |
| `country_id` | INTEGER | Numeric identifier representing the geographic country of the visitor. FK to [🥈 Countries (E-Commerce)](./countries-e-commerce.md) |
| `is_conversion` | BOOLEAN | Indicates whether the session resulted in a successful transaction or goal completion. |
| `source` | STRING | The origin of the traffic, such as Google, Facebook, or direct entry. |
| `medium` | STRING | The high-level channel type of the traffic, such as organic or cost-per-click. |
| `campaign` | STRING | The name of the specific marketing campaign that drove the session. |

## Joins

- [Visitors](./visitors-e-commerce.md) — `visitor_id = visitor_id`
- [Traffic Sources](./traffic-sources-e-commerce.md)
- [Countries](./countries-e-commerce.md) — `country_id = country_id`
- [Pageviews](./pageviews-e-commerce.md)
- [Customers](./customers-e-commerce.md) — `customer_id = customer_id`
- [Orders](./orders-e-commerce.md)
- [Unified Ad Spend](./unified-ad-spend-e-commerce.md)
