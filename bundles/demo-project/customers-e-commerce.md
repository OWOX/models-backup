---
type: "OWOX Data Mart"
title: "🥈 Customers (E-Commerce)"
description: "This Data Mart provides a comprehensive profile of registered e-commerce customers, including their segmentation, registration dates, and geographical locations. It is primarily used for analyzing ..."
resource: "https://app.owox.com/api/external/http-data/data-marts/f5035458-0b6e-443a-afdd-c05d03095292.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-06-15T10:45:23.000Z
---

# 🥈 Customers (E-Commerce)

This Data Mart provides a comprehensive profile of registered e-commerce customers, including their segmentation, registration dates, and geographical locations. It is primarily used for analyzing customer acquisition trends and performing user-base segmentation for targeted marketing.

## Overview

- **ID:** `f5035458-0b6e-443a-afdd-c05d03095292`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/f5035458-0b6e-443a-afdd-c05d03095292.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | INTEGER | Unique identifier for an individual registered customer |
| `customer_segment` | STRING | The classification of the customer based on their purchase history or value |
| `registration_date` | DATE | The specific date when the customer account was created in the system |
| `acquisition_traffic_source_id` | INTEGER |  |
| `country_id` | INTEGER | The primary geographical location assigned to the customer FK to [🥈 Countries (E-Commerce)](./countries-e-commerce.md) |

## Joins

- [Acquisition Traffic Source](./traffic-sources-e-commerce.md)
- [Countries](./countries-e-commerce.md)
