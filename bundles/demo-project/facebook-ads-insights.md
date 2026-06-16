---
type: "OWOX Data Mart"
title: "Facebook Ads Insights"
description: "Facebook Ads Insights."
resource: "https://app.owox.com/api/external/http-data/data-marts/5f67ccdd-1eaf-486d-981c-e37d970d82ed.ndjson"
tags: ["owox", "snowflake", "connector"]
timestamp: 2026-05-26T06:02:09.000Z
---

# Facebook Ads Insights

Facebook Ads Insights.
Owner: Ievgen - Head of Marketing
Ad-level granularity

## Overview

- **ID:** `5f67ccdd-1eaf-486d-981c-e37d970d82ed`
- **Status:** PUBLISHED
- **Definition type:** CONNECTOR
- **Storage:** Snowflake [Marketing] (SNOWFLAKE)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/5f67ccdd-1eaf-486d-981c-e37d970d82ed.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `ad_id` | STRING | The unique ID of the ad you're viewing in reporting. |
| `date_start` | DATE | The start date for your data. This is controlled by the date range you've selected for your reporting view. |
| `date_stop` | DATE | The end date for your data. This is controlled by the date range you've selected for your reporting view. |
| `account_name` | STRING | The name of your ad account, which groups your advertising activity. Your ad account includes your campaigns, ads and billing. |
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
| `reach` | FLOAT | The number of people who saw your ads at least once. Reach is different from impressions, which may include multiple views of your ads by the same people. This metric is estimated. |
| `results` | STRING | The number of results you received out of all the views of your ads. |
| `spend` | FLOAT | The estimated total amount of money you've spent on your campaign, ad set or ad during its schedule. This metric is estimated. |
