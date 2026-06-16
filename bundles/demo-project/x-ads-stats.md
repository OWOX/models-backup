---
type: "OWOX Data Mart"
title: "X Ads Stats"
description: "OWOX data mart 'X Ads Stats'."
resource: "https://app.owox.com/api/external/http-data/data-marts/bb3c6227-3642-4cad-9195-201c795c4f86.ndjson"
tags: ["owox", "google_bigquery", "connector"]
timestamp: 2026-04-20T15:49:56.000Z
---

# X Ads Stats

## Overview

- **ID:** `bb3c6227-3642-4cad-9195-201c795c4f86`
- **Status:** PUBLISHED
- **Definition type:** CONNECTOR
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/bb3c6227-3642-4cad-9195-201c795c4f86.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | STRING | The unique identifier for the stats record. |
| `date` | STRING | The date for which the statistics were collected. |
| `placement` | STRING | The placement type (ALL_ON_TWITTER or PUBLISHER_NETWORK). |
| `impressions` | INTEGER | Number of impressions. |
| `tweets_send` | INTEGER | Number of tweets sent. |
| `likes` | INTEGER | Number of likes. |
| `unfollows` | INTEGER | Number of unfollows. |
| `retweets` | INTEGER | Number of retweets. |
| `app_clicks` | INTEGER | Number of app clicks. |
| `follows` | INTEGER | Number of follows. |
| `qualified_impressions` | INTEGER | Number of qualified impressions. |
| `billed_charge_local_micro` | INTEGER | Billed amount in micros. |
