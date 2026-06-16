---
type: "OWOX Data Mart"
title: "Google Ads Ad Group Stats [A]"
description: "OWOX data mart 'Google Ads Ad Group Stats [A]'."
resource: "https://app.owox.com/api/external/http-data/data-marts/16e026de-f69e-4453-8c8d-a4d6f4bfe2d2.ndjson"
tags: ["owox", "aws_athena", "connector"]
timestamp: 2026-04-14T10:41:14.361Z
---

# Google Ads Ad Group Stats [A]

## Overview

- **ID:** `16e026de-f69e-4453-8c8d-a4d6f4bfe2d2`
- **Status:** PUBLISHED
- **Definition type:** CONNECTOR
- **Storage:** AWS Athena [Marketing] (AWS_ATHENA)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/16e026de-f69e-4453-8c8d-a4d6f4bfe2d2.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `ad_group_id` | VARCHAR | Ad Group ID |
| `date` | VARCHAR | Date for time series data |
| `ad_group_name` | VARCHAR | Ad Group Name |
| `ad_group_status` | VARCHAR | Ad Group Status (ENABLED, PAUSED, REMOVED) |
| `campaign_id` | VARCHAR | Campaign ID |
| `impressions` | DOUBLE | Number of Impressions |
| `clicks` | DOUBLE | Number of Clicks |
| `cost_micros` | DOUBLE | Cost in Micros |
| `conversions` | DOUBLE | Number of Conversions |
| `ctr` | DOUBLE | Click-Through Rate |
| `average_cpc` | DOUBLE | Average Cost Per Click |
| `conversions_value` | DOUBLE | Total Conversion Value |
| `cost_per_conversion` | DOUBLE | Cost Per Conversion |
| `conversion_rate` | DOUBLE | Conversion Rate |
| `view_through_conversions` | DOUBLE | View-Through Conversions |
| `all_conversions` | DOUBLE | All Conversions |
| `all_conversions_value` | DOUBLE | All Conversions Value |
| `cost_per_all_conversions` | DOUBLE | Cost Per All Conversions |
| `average_cost` | DOUBLE | Average Cost |
| `average_cpm` | DOUBLE | Average CPM |
| `engagement_rate` | DOUBLE | Engagement Rate |
| `engagements` | DOUBLE | Number of Engagements |
