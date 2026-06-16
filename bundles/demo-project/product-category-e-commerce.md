---
type: "OWOX Data Mart"
title: "🥈 Product Category (E-Commerce)"
description: "This Data Mart provides a comprehensive list of product categories, their management hierarchy, and financial performance targets. It is used to analyze category-level organizational structure and ..."
resource: "https://app.owox.com/api/external/http-data/data-marts/f33bb078-1183-4951-8b8b-8010f7c91d3f.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-05-26T20:02:01.000Z
---

# 🥈 Product Category (E-Commerce)

This Data Mart provides a comprehensive list of product categories, their management hierarchy, and financial performance targets. It is used to analyze category-level organizational structure and monitor target profit margins across different business groups.

## Overview

- **ID:** `f33bb078-1183-4951-8b8b-8010f7c91d3f`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/f33bb078-1183-4951-8b8b-8010f7c91d3f.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `category_id` | INTEGER | Unique numerical identifier for each product category. |
| `category_name` | STRING | The descriptive name of the product category used for reporting and classification. |
| `category_manager` | STRING | Full name of the individual responsible for managing the specific product category. |
| `target_margin` | FLOAT | The desired profit margin percentage set for the category. |
| `category_group` | STRING | High-level classification used to group related categories together, such as hard or soft goods. |
