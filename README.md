# Supply Chain Health Dashboard

An interactive supply chain analytics dashboard built with Python, Streamlit, and Plotly.

Upload your own orders CSV or explore with the included sample dataset (600 synthetic orders).

![Dashboard preview](https://raw.githubusercontent.com/datawithdon/supply-chain-dashboard/main/preview.png)

## Features

| KPI | Description |
|-----|-------------|
| On-Time Rate | % of orders delivered by expected date |
| Avg Fulfillment Time | Days from order to delivery (monthly trend) |
| Fill Rate | % of ordered quantity actually received |
| Stockout Rate | % of inventory snapshots at zero stock |
| Demand vs Supply | Monthly ordered vs received quantities |
| Supplier Reliability | Scatter — delay variance vs on-time rate |
| Inventory Health | Treemap by category with stockout highlighting |
| On-Time Heatmap | Supplier × Month breakdown |

Sidebar filters let you slice by **category**, **supplier**, and **month range**.

## Quick Start

```bash
git clone https://github.com/datawithdon/supply-chain-dashboard.git
cd supply-chain-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Bring Your Own Data

Upload any CSV with these columns via the sidebar file uploader:

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | string | Unique order identifier |
| `product` | string | Product name |
| `category` | string | Product category |
| `supplier` | string | Supplier name |
| `order_date` | date | Date order was placed |
| `expected_delivery` | date | Originally promised delivery date |
| `actual_delivery` | date | Actual delivery date |
| `quantity_ordered` | int | Units ordered |
| `quantity_received` | int | Units actually received |
| `inventory_level` | int | Inventory snapshot at time of receipt |
| `unit_cost` | float | Cost per unit |

## Regenerate Sample Data

```bash
python generate_sample_data.py
```

## Tech Stack

- [Streamlit](https://streamlit.io) — dashboard framework
- [Plotly](https://plotly.com/python/) — interactive charts
- [pandas](https://pandas.pydata.org) — data wrangling

## License

MIT
