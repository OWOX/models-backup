---
type: "OWOX Data Mart"
title: "🥈 Purchases (E-Commerce)"
description: "Describes typical Purchases Data Mart in e-commerce domain for demo puprposes."
resource: "https://app.owox.com/api/external/http-data/data-marts/0212efac-2c7d-4bcb-aaf2-055229de4b75.ndjson"
tags: ["owox", "google_bigquery", "view"]
timestamp: 2026-06-15T16:01:26.000Z
---

# 🥈 Purchases (E-Commerce)

Describes typical Purchases Data Mart in e-commerce domain for demo puprposes.

This Data Mart acts as the foundational layer for understanding purchasing behavior and sales performance. By breaking down transactions into specific line items, it enables the business to move beyond simple revenue tracking and dive deep into SKU-level analytics. Whether you are analyzing sales trends by currency or evaluating the quantity of specific products sold, this data provides the necessary precision for informed decision-making.

The schema is built for flexibility and scalability, supporting multi-currency transactions and varying product quantities per order. It provides a clean, standardized output that allows analysts to quickly generate insights into which products drive growth and how pricing strategies impact customer purchasing habits at the point of sale.

## Overview

- **ID:** `0212efac-2c7d-4bcb-aaf2-055229de4b75`
- **Status:** PUBLISHED
- **Definition type:** VIEW
- **Storage:** BigQuery [Common] (GOOGLE_BIGQUERY)
- **Data endpoint:** `GET https://app.owox.com/api/external/http-data/data-marts/0212efac-2c7d-4bcb-aaf2-055229de4b75.ndjson`

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `purchase_id` | STRING | A unique identifier for each individual item row within an order |
| `order_id` | STRING | The unique identifier of the transaction. Used to join with the Orders Data Mart. |
| `product_id` | INTEGER | The unique identifier of the purchased product |
| `quantity` | INTEGER | The number of units of this specific product included in the purchase line |
| `sale_price` | FLOAT | The price per unit at the moment of purchase |
| `currency` | STRING | The currency used for the transaction (e.g., USD) |
| `unit_cost` | FLOAT | The cost incurred by the business to acquire or produce a single unit of the product. |
| `line_revenue` | FLOAT | Gross revenue for this order line = Item Sale Price × Quantity. Sum across lines for total gross revenue (all order statuses). |
| `line_cost` | FLOAT | Cost of goods sold for this order line = Unit Cost × Quantity. Sum for total COGS. |
| `line_net_revenue` | FLOAT | Revenue recognised only for Completed orders (Cancelled / Returned = 0). Sum for net  revenue. |
| `line_net_profit` | FLOAT | Profit for Completed orders = (Item Sale Price − Unit Cost) × Quantity, else 0. Sum for  total net profit. |

## Joins

- [Products](./products-e-commerce.md)
- [Orders](./orders-e-commerce.md)
