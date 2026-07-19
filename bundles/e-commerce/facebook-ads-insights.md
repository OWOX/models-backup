---
type: "OWOX Data Mart"
title: "Facebook Ads Insights"
description: "Facebook Ads Account Insights. "
resource: "https://app.owox.com/api/external/http-data/data-marts/cbec554e-11b4-426b-a066-d32cab44ab66.ndjson"
tags: ["owox", "google_bigquery", "connector"]
timestamp: 2026-05-26T20:09:30.000Z
---

# Facebook Ads Insights

Facebook Ads Account Insights. 
Ad-level granularity.

## Overview

- **ID:** `cbec554e-11b4-426b-a066-d32cab44ab66`
- **Status:** PUBLISHED
- **Definition type:** CONNECTOR
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/cbec554e-11b4-426b-a066-d32cab44ab66.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `ad_id` | STRING | PK. The unique ID of the ad you're viewing in reporting. |
| `date_start` | DATE | PK. The start date for your data. This is controlled by the date range you've selected for your reporting view. |
| `date_stop` | DATE | PK. The end date for your data. This is controlled by the date range you've selected for your reporting view. |
| `ad_name` | STRING | The name of the ad you're viewing in reporting. |
| `adset_id` | STRING | The unique ID of the ad set you're viewing in reporting. An ad set is a group of ads that share the same budget, schedule, delivery optimization and targeting. |
| `adset_name` | STRING | The name of the ad set you're viewing in reporting. An ad set is a group of ads that share the same budget, schedule, delivery optimization and targeting. |
| `campaign_id` | STRING | The unique ID number of the ad campaign you're viewing in reporting. Your campaign contains ad sets and ads. |
| `campaign_name` | STRING | The name of the ad campaign you're viewing in reporting. Your campaign contains ad sets and ads. |
| `clicks` | FLOAT | The number of clicks on your ads. |
| `conversions` | STRING | conversions |
| `conversion_values` | STRING | conversion_values |
| `cpc` | FLOAT | The average cost for each click (all). |
| `cpm` | FLOAT | The average cost for 1,000 impressions. |
| `cpp` | FLOAT | The average cost to reach 1,000 people. This metric is estimated. |
| `ctr` | FLOAT | The percentage of times people saw your ad and performed a click (all). |
| `frequency` | FLOAT | The average number of times each person saw your ad. This metric is estimated. |
| `impressions` | FLOAT | The number of times your ads were on screen. |
| `results` | STRING | The number of results you received out of all the views of your ads. |
| `spend` | FLOAT | The estimated total amount of money you've spent on your campaign, ad set or ad during its schedule. This metric is estimated. |
