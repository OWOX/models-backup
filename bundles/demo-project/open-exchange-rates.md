---
type: "OWOX Data Mart"
title: "Open Exchange Rates"
description: "OWOX data mart 'Open Exchange Rates'."
resource: "https://app.owox.com/api/external/http-data/data-marts/2d064db4-a6f2-4539-ac89-7f20be662340.ndjson"
tags: ["owox", "google_bigquery", "connector"]
timestamp: 2026-06-16T07:00:38.000Z
---

# Open Exchange Rates

## Overview

- **ID:** `2d064db4-a6f2-4539-ac89-7f20be662340`
- **Status:** PUBLISHED
- **Definition type:** CONNECTOR
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/2d064db4-a6f2-4539-ac89-7f20be662340.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Date of exchange rate |
| `base` | STRING | Base currency |
| `currency` | STRING | Target currency |
| `rate` | FLOAT | Exchange rate |
