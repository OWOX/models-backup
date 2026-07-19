---
type: "OWOX Data Mart"
title: "🥈 Countries (E-Commerce)"
description: "OWOX data mart '🥈 Countries (E-Commerce)'."
resource: "https://app.owox.com/api/external/http-data/data-marts/bad7e127-2352-4663-8b68-cbd06a9c0eb7.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-07-18T21:00:20.000Z
---

# 🥈 Countries (E-Commerce)

## Overview

- **ID:** `bad7e127-2352-4663-8b68-cbd06a9c0eb7`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/bad7e127-2352-4663-8b68-cbd06a9c0eb7.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `country_id` | INTEGER | PK. Unique internal identifier for each country record. |
| `country` | STRING | Full name of the country. |
| `country_code` | STRING | Two-letter ISO country code representing the nation. |
| `weight` | INTEGER | Numerical value used to prioritize or rank countries in the e-commerce system. |
