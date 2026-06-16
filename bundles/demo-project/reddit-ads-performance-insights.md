---
type: "OWOX Data Mart"
title: "Reddit Ads Performance Insights"
description: "OWOX data mart 'Reddit Ads Performance Insights'."
resource: "https://app.owox.com/api/external/http-data/data-marts/16c4f348-a2d4-41ed-b8ee-f5803bc976c7.ndjson"
tags: ["owox", "databricks", "connector"]
timestamp: 2026-06-16T06:00:41.000Z
---

# Reddit Ads Performance Insights

## Overview

- **ID:** `16c4f348-a2d4-41ed-b8ee-f5803bc976c7`
- **Status:** PUBLISHED
- **Definition type:** CONNECTOR
- **Storage:** Databricks [Common] (DATABRICKS)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/16c4f348-a2d4-41ed-b8ee-f5803bc976c7.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `ad_id` | STRING | The ID of the ad. |
| `date` | DATE | The date for this metric. |
| `clicks` | BIGINT | The number of clicks detected for this report period. |
| `cpc` | DOUBLE | The cost-per-click for this period. |
| `ecpm` | DOUBLE | The effective CPM for this period. |
| `cpv` | DOUBLE | [Broken] The cost-per-view for this period. |
| `ctr` | DOUBLE | The click-through-rate for this period. |
| `hour` | STRING | The hour for this metric in ISO-8601. |
| `engaged_click` | BIGINT | The number of engaged clicks such as RSVPs. |
| `impressions` | BIGINT | The number of impressions served for this report period. |
| `post_id` | STRING | The unique identifier of the post. |
| `spend` | BIGINT | The amount (in microcurrency) spent for this report period. |
