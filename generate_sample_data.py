import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

PRODUCTS = [
    ("Widget A", "Electronics"), ("Widget B", "Electronics"), ("Gadget X", "Electronics"),
    ("Steel Rod", "Raw Materials"), ("Aluminum Sheet", "Raw Materials"), ("Copper Wire", "Raw Materials"),
    ("Bolt M10", "Fasteners"), ("Nut M10", "Fasteners"), ("Washer 20mm", "Fasteners"),
    ("Cardboard Box L", "Packaging"), ("Bubble Wrap Roll", "Packaging"), ("Foam Sheet", "Packaging"),
    ("Motor 12V", "Components"), ("Capacitor 100uF", "Components"), ("Resistor 10k", "Components"),
]

SUPPLIERS = {
    "Electronics": ["TechSource Co", "DigiParts Ltd"],
    "Raw Materials": ["MetalWorks Inc", "SteelWorld"],
    "Fasteners": ["BoltKing", "FastenRight"],
    "Packaging": ["PackPro", "BoxCraft Ltd"],
    "Components": ["ComponentHub", "TechSource Co"],
}

def generate_orders(n=600, start_date=datetime(2024, 1, 1)):
    rows = []
    inventory = {p[0]: random.randint(200, 500) for p in PRODUCTS}

    for i in range(n):
        product, category = random.choice(PRODUCTS)
        supplier = random.choice(SUPPLIERS[category])
        order_date = start_date + timedelta(days=random.randint(0, 364))

        nominal_lead = random.randint(5, 14)
        # Unreliable suppliers have high variance
        unreliable = supplier in ["MetalWorks Inc", "PackPro", "ComponentHub"]
        variance = random.randint(-2, 15) if unreliable else random.randint(-1, 4)
        actual_lead = max(1, nominal_lead + variance)

        expected_delivery = order_date + timedelta(days=nominal_lead)
        actual_delivery = order_date + timedelta(days=actual_lead)

        qty_ordered = random.randint(50, 300)
        # Occasionally short-ship
        qty_received = qty_ordered if random.random() > 0.12 else int(qty_ordered * random.uniform(0.5, 0.9))

        inventory[product] = max(0, inventory[product] - random.randint(10, 60) + qty_received)
        inv_snapshot = inventory[product]

        rows.append({
            "order_id": f"ORD-{10000 + i}",
            "product": product,
            "category": category,
            "supplier": supplier,
            "order_date": order_date.date(),
            "expected_delivery": expected_delivery.date(),
            "actual_delivery": actual_delivery.date(),
            "quantity_ordered": qty_ordered,
            "quantity_received": qty_received,
            "inventory_level": inv_snapshot,
            "unit_cost": round(random.uniform(1.5, 120.0), 2),
        })

    df = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate_orders(600)
    df.to_csv("data/sample_orders.csv", index=False)
    print(f"Generated {len(df)} orders → data/sample_orders.csv")
