---
type: "OWOX Data Mart"
title: "🥈 Pageviews (E-Commerce)"
description: "OWOX data mart '🥈 Pageviews (E-Commerce)'."
resource: "https://app.owox.com/api/external/http-data/data-marts/ebcc639a-e474-418a-8f62-36e222c61e2e.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-05-26T20:00:22.000Z
---

# 🥈 Pageviews (E-Commerce)

## Overview

- **ID:** `ebcc639a-e474-418a-8f62-36e222c61e2e`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/ebcc639a-e474-418a-8f62-36e222c61e2e.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | The calendar date when the pageview occurred. |
| `session_id` | STRING | Unique identifier for a specific user browsing session. |
| `visitor_id` | STRING | Unique identifier for an individual user or browser. |
| `hit_number` | INTEGER | The sequential order of the pageview within a specific session. |
| `page_id` | INTEGER | Unique identifier for the specific page viewed by the visitor. FK to [🥈 Pages (E-Commerce)](./pages-e-commerce.md) |
| `hit_timestamp` | TIMESTAMP | The exact date and time when the pageview was recorded, in UTC. |

## Joins

- [Pages](./pages-e-commerce.md) — `page_id = page_id`
