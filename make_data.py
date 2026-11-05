import pandas as pd
import numpy as np

np.random.seed(42)

# القارات السبع والدول (الوزن = حصة القارة من المبيعات)
world = {
    "North America": (0.28, ["United States", "Canada", "Mexico"]),
    "Europe":        (0.26, ["Germany", "United Kingdom", "France", "Spain"]),
    "Asia":          (0.22, ["Saudi Arabia", "United Arab Emirates", "Japan", "India", "Jordan"]),
    "Oceania":       (0.08, ["Australia", "New Zealand"]),
    "South America": (0.07, ["Brazil", "Argentina", "Chile"]),
    "Africa":        (0.085, ["Egypt", "South Africa", "Nigeria", "Morocco"]),
    "Antarctica":    (0.005, ["Antarctica"]),
}

places, weights = [], []
for continent, (w, countries) in world.items():
    for c in countries:
        places.append((continent, c))
        weights.append(w / len(countries))
weights = np.array(weights) / sum(weights)

products = {
    "Headphones":  ("Electronics", 45),
    "Charger":     ("Electronics", 15),
    "Smart Watch": ("Electronics", 90),
    "T-Shirt":     ("Clothing", 25),
    "Sneakers":    ("Clothing", 60),
    "Backpack":    ("Accessories", 40),
    "Sunglasses":  ("Accessories", 30),
}

dates = pd.date_range("2025-11-01", "2026-10-31")
rows = []
for i in range(3000):
    name = np.random.choice(list(products.keys()))
    category, price = products[name]
    continent, country = places[np.random.choice(len(places), p=weights)]
    rows.append({
        "order_id": 1000 + i,
        "date": np.random.choice(dates),
        "product": name,
        "category": category,
        "continent": continent,
        "country": country,
        "quantity": np.random.randint(1, 4),
        "unit_price": price,
    })

df = pd.DataFrame(rows)
df["revenue"] = df["quantity"] * df["unit_price"]
df = df.sort_values("date")
df.to_csv("sales.csv", index=False, encoding="utf-8-sig")
print("Done. Orders:", len(df))