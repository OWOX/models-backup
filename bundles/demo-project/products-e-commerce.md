---
type: "OWOX Data Mart"
title: "🥈 Products (E-Commerce)"
description: "This Data Mart provides a comprehensive catalog of e-commerce products, including pricing, cost structures, and website categorization. It is primarily used for analyzing product margins and managi..."
resource: "https://app.owox.com/api/external/http-data/data-marts/f6b33805-84ed-4469-9f7d-438e99c48696.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-06-16T07:00:41.000Z
---

# 🥈 Products (E-Commerce)

This Data Mart provides a comprehensive catalog of e-commerce products, including pricing, cost structures, and website categorization. It is primarily used for analyzing product margins and managing web content mapping.

## Overview

- **ID:** `f6b33805-84ed-4469-9f7d-438e99c48696`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/f6b33805-84ed-4469-9f7d-438e99c48696.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | INTEGER | Unique identifier for a specific product in the catalog |
| `product_name` | STRING | The full commercial name of the product |
| `price` | FLOAT | The current selling price of a single unit of the product |
| `cost` | FLOAT | The acquisition cost or production expense per unit of the product |
| `sub_category` | STRING | The specific sub-classification of the product within its broader category. |
| `category_id` | INTEGER | Unique identifier for the high-level category the product belongs to. |
| `page_path` | STRING | The URL relative path for the product's detail page on the website. |
| `page_id` | INTEGER | Unique identifier for the specific web page associated with the product. |
