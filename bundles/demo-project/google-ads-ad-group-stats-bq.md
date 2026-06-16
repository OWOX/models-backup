---
type: "OWOX Data Mart"
title: "Google Ads Ad Group Stats BQ"
description: "Google Ads Ad Group Stats. "
resource: "https://app.owox.com/api/external/http-data/data-marts/9e9035ea-1ab3-44a6-a2a5-f1bf2744dc19.ndjson"
tags: ["owox", "google_bigquery", "connector"]
timestamp: 2026-05-26T20:09:19.000Z
---

# Google Ads Ad Group Stats BQ

Google Ads Ad Group Stats. 
Ad group granularity.

## Overview

- **ID:** `9e9035ea-1ab3-44a6-a2a5-f1bf2744dc19`
- **Status:** PUBLISHED
- **Definition type:** CONNECTOR
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/9e9035ea-1ab3-44a6-a2a5-f1bf2744dc19.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `ad_group_id` | STRING | Ad Group ID |
| `date` | STRING | Date for time series data |
| `ad_group_name` | STRING | Ad Group Name |
| `ad_group_status` | STRING | Ad Group Status (ENABLED, PAUSED, REMOVED) |
| `campaign_id` | STRING | Campaign ID |
| `clicks` | FLOAT | Number of Clicks |
| `cost_micros` | FLOAT | Cost in Micros |
| `conversions` | FLOAT | Number of Conversions |
| `ctr` | FLOAT | Click-Through Rate |
| `average_cpc` | FLOAT | Average Cost Per Click |
| `impressions` | FLOAT | Number of Impressions |
| `conversion_rate` | FLOAT | Conversion Rate |
| `cost_per_conversion` | FLOAT | Cost Per Conversion |
| `conversions_value` | FLOAT | Total Conversion Value |
| `all_conversions` | FLOAT | All Conversions |
| `all_conversions_value` | FLOAT | All Conversions Value |
| `cost_per_all_conversions` | FLOAT | Cost Per All Conversions |
| `average_cpm` | FLOAT | Average CPM |
| `average_cost` | FLOAT | Average Cost |
