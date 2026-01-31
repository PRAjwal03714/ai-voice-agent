import json
import random
from datetime import datetime, timedelta

def load_baseline_data():
    try:
        with open('real_data_baseline.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Error: real_data_baseline.json not found")
        print("Run fetch_real_baseline.py first")
        return None


def generate_property_from_baseline(baseline_data):
    stats = baseline_data['statistics']
    neighborhoods = baseline_data['neighborhoods']
    
    neighborhood_names = list(neighborhoods.keys())
    neighborhood_weights = [neighborhoods[n]['count'] for n in neighborhood_names]
    
    neighborhood = random.choices(neighborhood_names, weights=neighborhood_weights)[0]
    
    hood_stats = neighborhoods[neighborhood]
    
    avg = hood_stats['avg_value']
    std_dev = (hood_stats['max_value'] - hood_stats['min_value']) / 4
    
    price = int(random.normalvariate(avg, std_dev))
    price = max(hood_stats['min_value'], min(price, hood_stats['max_value']))
    
    street_names = ["Meridian", "College", "Pennsylvania", "Washington", "Capitol", 
                   "Delaware", "Illinois", "Alabama", "Market", "Ohio"]
    street_types = ["St", "Ave", "Blvd", "Dr", "Ln", "Way"]
    
    street_num = random.randint(100, 9999)
    street = random.choice(street_names)
    street_type = random.choice(street_types)
    
    address = f"{street_num} {street} {street_type}, Indianapolis, IN"
    
    if price < 250000:
        bedrooms = random.choices([2, 3], weights=[60, 40])[0]
    elif price < 400000:
        bedrooms = random.choices([2, 3, 4], weights=[20, 60, 20])[0]
    elif price < 600000:
        bedrooms = random.choices([3, 4, 5], weights=[30, 50, 20])[0]
    else:
        bedrooms = random.choices([4, 5, 6], weights=[40, 50, 10])[0]
    
    bathrooms = max(1, bedrooms - random.choice([0, 1]))
    
    price_per_sqft = random.uniform(150, 280)
    sqft = int(price / price_per_sqft)
    
    year_built = random.randint(1950, 2024)
    
    if random.random() < 0.7:
        days_ago = random.randint(30, 1825)
        sale_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        sale_price = int(price * random.uniform(0.92, 1.08))
    else:
        sale_date = None
        sale_price = None
    
    comp_low = int(price * 0.93)
    comp_high = int(price * 1.07)
    n_comps = random.randint(3, 8)
    
    comparable_sales = f"{n_comps} recent sales in {neighborhood}: ${comp_low//1000}K-${comp_high//1000}K"
    
    return {
        "address": address,
        "assessed_value": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "sqft": sqft,
        "year_built": year_built,
        "last_sale_price": sale_price,
        "last_sale_date": sale_date,
        "neighborhood": neighborhood,
        "comparable_sales": comparable_sales,
        "price_per_sqft": int(price / sqft),
        "notes": f"Generated from {stats['total_records']} real market properties"
    }


def generate_dataset(count=500):
    baseline = load_baseline_data()
    
    if not baseline:
        return None
    
    properties = []
    
    for i in range(count):
        prop = generate_property_from_baseline(baseline)
        properties.append(prop)
        
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/{count} properties")
    
    return properties


def main():
    print("Generating 500 properties from baseline data...\n")
    
    properties = generate_dataset(500)
    
    if not properties:
        print("Generation failed")
        return
    
    with open('generated_from_real_baseline.json', 'w') as f:
        json.dump(properties, f, indent=2)
    
    avg_price = sum(p['assessed_value'] for p in properties) / len(properties)
    
    print(f"\nGenerated {len(properties)} properties")
    print(f"Average price: ${avg_price:,.0f}")
    print(f"Saved to generated_from_real_baseline.json")


if __name__ == "__main__":
    main()