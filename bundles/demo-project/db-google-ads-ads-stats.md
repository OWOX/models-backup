---
type: "OWOX Data Mart"
title: "[DB] Google Ads | Ads Stats"
description: "OWOX data mart '[DB] Google Ads | Ads Stats'."
resource: "https://app.owox.com/api/external/http-data/data-marts/25471996-6576-4dd2-95bb-125db136c322.ndjson"
tags: ["owox", "databricks", "connector"]
timestamp: 2026-04-14T10:41:14.361Z
---

# [DB] Google Ads | Ads Stats

## Overview

- **ID:** `25471996-6576-4dd2-95bb-125db136c322`
- **Status:** PUBLISHED
- **Definition type:** CONNECTOR
- **Storage:** Databricks [Common] (DATABRICKS)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/25471996-6576-4dd2-95bb-125db136c322.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `ad_id` | STRING | Ad ID |
| `date` | STRING | Date for time series data |
| `ad_status` | STRING | Ad Status (ENABLED, PAUSED, REMOVED) |
| `ad_final_urls` | STRING | Final URLs for the Ad |
| `ad_group_id` | STRING | Ad Group ID |
| `impressions` | DOUBLE | Number of Impressions |
| `campaign_id` | STRING | Campaign ID |
| `clicks` | DOUBLE | Number of Clicks |
| `cost_micros` | DOUBLE | Cost in Micros |
| `conversions` | DOUBLE | Number of Conversions |
| `ctr` | DOUBLE | Click-Through Rate |
| `average_cpc` | DOUBLE | Average Cost Per Click |
| `conversions_value` | DOUBLE | Total Conversion Value |
| `cost_per_conversion` | DOUBLE | Cost Per Conversion |
| `ad_type` | STRING | Ad Type (TEXT_AD, EXPANDED_TEXT_AD, RESPONSIVE_SEARCH_AD, etc.) |
| `ad_name` | STRING | Ad Name |
| `ad_group_name` | STRING | Ad Group Name |
| `campaign_name` | STRING | Campaign Name |
| `conversion_rate` | DOUBLE | Conversion Rate |
| `view_through_conversions` | DOUBLE | View-Through Conversions |
| `all_conversions` | DOUBLE | All Conversions |
| `average_cost` | DOUBLE | Average Cost |
| `all_conversions_value` | DOUBLE | All Conversions Value |
| `average_cpm` | DOUBLE | Average CPM |
| `interactions` | DOUBLE | Number of Interactions |
| `interaction_rate` | DOUBLE | Interaction Rate |
