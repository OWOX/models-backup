---
type: "OWOX Data Mart"
title: "🥈 Traffic Sources (E-Commerce)"
description: "This Data Mart provides a comprehensive breakdown of website traffic origins, categorizing visitors by source, medium, and specific marketing campaigns. It is used to analyze the effectiveness of d..."
resource: "https://app.owox.com/api/external/http-data/data-marts/61b3c045-b334-440d-9913-bf52bc622af4.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-16T14:08:48.000Z
---

# 🥈 Traffic Sources (E-Commerce)

This Data Mart provides a comprehensive breakdown of website traffic origins, categorizing visitors by source, medium, and specific marketing campaigns. It is used to analyze the effectiveness of different acquisition channels and distinguish between paid and organic traffic performance.

## Overview

- **ID:** `61b3c045-b334-440d-9913-bf52bc622af4`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/61b3c045-b334-440d-9913-bf52bc622af4.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `traffic_source_id` | INTEGER | Unique internal identifier for a specific combination of traffic source, medium, and campaign. |
| `source` | STRING | The origin of the website traffic, such as a search engine, social network, or domain. |
| `medium` | STRING | The high-level category of the traffic source, such as organic, cost-per-click, or referral. |
| `campaign` | STRING | The specific marketing campaign name associated with the traffic. |
| `is_paid` | BOOLEAN | Indicates whether the traffic was generated through a paid marketing channel. |
| `channel_grouping` | STRING | The classification of traffic into broad categories like Paid Marketing, Direct, or Organic. |
