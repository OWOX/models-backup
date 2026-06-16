---
type: "OWOX Data Mart"
title: "🥈 Visitors (E-Commerce)"
description: "This dataset provides a comprehensive overview of website visitor behavior and acquisition history at the individual visitor level. It tracks engagement metrics like total sessions and visit dates ..."
resource: "https://app.owox.com/api/external/http-data/data-marts/13e040df-a062-4f38-803b-54a7e0b75a3e.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-06-05T19:26:56.000Z
---

# 🥈 Visitors (E-Commerce)

This dataset provides a comprehensive overview of website visitor behavior and acquisition history at the individual visitor level. It tracks engagement metrics like total sessions and visit dates alongside marketing attribution details to help analyze user retention and campaign effectiveness.

## Overview

- **ID:** `13e040df-a062-4f38-803b-54a7e0b75a3e`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/13e040df-a062-4f38-803b-54a7e0b75a3e.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `visitor_id` | STRING | Unique identifier for the website visitor. |
| `linked_customer_id` | INTEGER | Identifier of the registered customer account associated with this visitor, if applicable. |
| `first_seen_date` | DATE | The date when the visitor first interacted with the website. |
| `last_seen_date` | DATE | The date of the most recent recorded interaction from this visitor. |
| `total_sessions` | INTEGER | Total number of distinct browsing sessions initiated by the visitor. |
| `acquisition_source` | STRING | The specific platform or site that referred the visitor to the website. |
| `acquisition_medium` | STRING | The high-level channel type used to acquire the visitor, such as organic or paid search. |
| `acquisition_campaign` | STRING | The name of the marketing campaign that originally brought the visitor to the site. |
| `cohort_month` | DATE | The month and year of the visitor's first visit, used for retention analysis. |
| `visitor_segment` | STRING | Classification of the visitor based on their engagement behavior or frequency. |
| `country_id` | INTEGER | Numeric identifier representing the country where the visitor is located. |
