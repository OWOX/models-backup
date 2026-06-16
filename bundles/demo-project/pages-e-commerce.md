---
type: "OWOX Data Mart"
title: "🥈 Pages (E-Commerce)"
description: "This dataset provides a comprehensive directory of all web pages within the e-commerce platform, categorized by their functional purpose. It is used to map specific URL paths to human-readable titl..."
resource: "https://app.owox.com/api/external/http-data/data-marts/5a7b5950-330c-4833-add0-033097440fe7.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-06-05T09:13:22.000Z
---

# 🥈 Pages (E-Commerce)

This dataset provides a comprehensive directory of all web pages within the e-commerce platform, categorized by their functional purpose. It is used to map specific URL paths to human-readable titles and page types, such as Product, Category, or Checkout, to support website navigation and conversion analysis.

## Overview

- **ID:** `5a7b5950-330c-4833-add0-033097440fe7`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/5a7b5950-330c-4833-add0-033097440fe7.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `page_id` | INTEGER | Unique numerical identifier for each specific page on the website. |
| `page_path` | STRING | The URL path of the page relative to the domain root. |
| `page_title` | STRING | The human-readable name or display title of the web page. |
| `page_type` | STRING | Functional category of the page, such as Product, Category, or Checkout. |
