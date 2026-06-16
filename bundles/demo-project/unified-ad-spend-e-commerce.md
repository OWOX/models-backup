---
type: "OWOX Data Mart"
title: "🥈 Unified Ad Spend (E-Commerce)"
description: "This dataset provides a consolidated view of daily advertising expenditures and performance metrics across multiple marketing platforms. It allows users to analyze spend, clicks, and impressions at..."
resource: "https://app.owox.com/api/external/http-data/data-marts/c36e7a4e-e6c0-49ca-99f2-d8440d475363.ndjson"
tags: ["owox", "google_bigquery", "sql"]
timestamp: 2026-06-16T15:28:23.000Z
---

# 🥈 Unified Ad Spend (E-Commerce)

This dataset provides a consolidated view of daily advertising expenditures and performance metrics across multiple marketing platforms. It allows users to analyze spend, clicks, and impressions at the campaign level to evaluate cross-channel marketing efficiency.

## Overview

- **ID:** `c36e7a4e-e6c0-49ca-99f2-d8440d475363`
- **Status:** PUBLISHED
- **Definition type:** SQL
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/c36e7a4e-e6c0-49ca-99f2-d8440d475363.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | The calendar date when the advertising activity occurred. |
| `source` | STRING | The name of the advertising platform or network where the traffic originated. |
| `medium` | STRING | The marketing channel or payment model used, such as cost-per-click. |
| `campaign` | STRING | The specific marketing campaign name associated with the ad spend. |
| `spend` | FLOAT | The total cost of advertising incurred during the specified period. |
| `clicks` | INTEGER | The total number of times users clicked on the advertisements. |
| `impressions` | INTEGER | The total number of times the advertisements were displayed to users. |
