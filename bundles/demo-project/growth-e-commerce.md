---
type: "OWOX Data Mart"
title: "🥇 Growth (E-Commerce)"
description: "Demo guide"
resource: "https://app.owox.com/api/external/http-data/data-marts/b4f59656-d52e-4ae3-847e-c34c025956bf.ndjson"
tags: ["owox", "google_bigquery", "sql"]
timestamp: 2026-06-09T13:01:14.000Z
---

# 🥇 Growth (E-Commerce)

Demo guide
  
  ▎ What it is. A gold-layer Data Mart built the OWOX way: a thin SQL base that pulls one row per web 
  ▎ session, enriched entirely through Joinable Data Marts — zero join SQL. Five governed marts are 
  ▎ attached: Traffic Sources, Countries, Customers, Orders, and Purchases (Purchases reached 
  ▎ transitively: session → order → line item).
  ▎
  ▎ Headline message. "This is how you build a star-schema gold layer in OWOX without writing join SQL. 
  ▎ The base reads raw sessions; every other dimension and metric is composed by joining governed Data 
  ▎ Marts and picking an aggregation. OWOX rolls the 1-to-many order lines back up to the session grain 
  ▎ automatically — nothing fans out, and the join logic stays reusable instead of buried in one giant 
  ▎ query."
  ▎
  ▎ Demo cases it supports:
  ▎ - Full funnel in one mart — traffic (source / medium / campaign, paid vs organic, channel grouping) → 
  ▎ session → conversion → order → revenue. Show conversion rate by channel.
  ▎ - Acquisition & geo growth — revenue and conversions sliced by channel grouping and country/region; 
  ▎ spot the markets and channels driving growth.
  ▎ - Customer quality — Platinum / Gold / Standard segments against revenue and conversion: is high-value
  ▎  demand growing?
  ▎ - Transitive-join showcase — Purchases joins through Orders (session → order → item): multi-hop joins 
  ▎ with SUM roll-up to the session grain.
  ▎ - Governance — some upstream marts are marked hidden from reporting to keep the analyst's field picker
  ▎  clean; show how you curate the catalog.
  ▎ - Self-serve in Sheets — the same mart powers a live, refreshable Google Sheets report via the OWOX 
  ▎ extension.
  ▎
  ▎ Metrics (after the revenue push-down): sessions, conversion rate, orders, units, gross revenue, net 
  ▎ (Completed-only) revenue, gross profit, AOV — by date/month, channel, country, segment, device.
  ▎
  ▎ Presenter caveat: product/SKU/category breakdowns are intentionally out of scope here (session grain).
  ▎  For item-level analysis, use a purchases-grain mart.

## Overview

- **ID:** `b4f59656-d52e-4ae3-847e-c34c025956bf`
- **Status:** PUBLISHED
- **Definition type:** SQL
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/b4f59656-d52e-4ae3-847e-c34c025956bf.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | The calendar date when the session occurred. |
| `session_id` | STRING | Unique identifier for an individual web or app session. |
| `visitor_id` | STRING | Unique identifier for the anonymous visitor or browser. |
| `traffic_source_id` | INTEGER | Numeric identifier for the marketing channel or referral source that directed the user. |
| `country_id` | INTEGER | Numeric identifier representing the geographic country of the visitor. |
| `customer_id` | INTEGER | Unique identifier for a registered user, which is null for guest visitors. |
| `device_category` | STRING | The type of hardware used by the visitor, such as mobile or desktop. |
| `is_conversion` | BOOLEAN | Indicates whether the session resulted in a successful transaction or goal completion. |
