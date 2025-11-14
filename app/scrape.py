import random
from datetime import datetime, timedelta
from . import db
from .models import CompetitorPrice

# Nairobi-specific competitor data
NAIROBI_HOTELS = {
    'Westlands': [
        "Sankara Nairobi", "Radisson Blu Nairobi", "The Sarova Stanley",
        "Villa Rosa Kempinski", "Nairobi Serena Hotel", "Hemingways Nairobi",
        "Fairmont The Norfolk", "The Boma Nairobi", "Tribe Hotel",
        "DoubleTree by Hilton Nairobi"
    ],
    'CBD': [
        "Intercontinental Nairobi", "The Sarova Stanley", "Panari Hotel",
        "Sixeighty Hotel", "Laico Regency Hotel", "The Heron Portico",
        "Milimani Hotel", "The Clarion Hotel", "Stanley Court Hotel"
    ],
    'Kilimani': [
        "Palacina Residence & Suites", "The Mirage", "Mövenpick Residence Nairobi",
        "Applewood Apartments", "Kilimani Heights", "Kile Apartments",
        "The Masterson", "Galana Suites"
    ],
    'Karen': [
        "Karen Gables", "The Hub Karen", "Karen Blixen Camp",
        "Matbronze Café & Art Gallery", "The Talisman", "Karen Portuguese Hotel"
    ],
    'Lavington': [
        "Lavington Green Apartments", "The Ridge", "Lavington Gardens",
        "Muthaiga Executive Suites", "Rosslyn Riviera"
    ]
}

PLATFORMS = ['Airbnb', 'Booking.com', 'Agoda', 'Expedia', 'Hotels.com', 'Direct Website']

def get_nairobi_seasonal_factor(date):
    """Calculate seasonal pricing factor for Nairobi market"""
    month = date.month
    
    # High season: July-September (peak tourism), December (holidays)
    if month in [7, 8, 9, 12]:
        return random.uniform(1.2, 1.5)
    
    # Medium season: January, June, October
    elif month in [1, 6, 10]:
        return random.uniform(1.0, 1.2)
    
    # Low season: February-May, November
    else:
        return random.uniform(0.8, 1.0)

def get_location_base_price(location, property_type):
    """Get realistic base prices for Nairobi locations"""
    base_prices = {
        'Westlands': {'Serviced Apartment': 18000, 'Boutique Hotel': 22000, 'Guest House': 12000},
        'CBD': {'Serviced Apartment': 15000, 'Boutique Hotel': 18000, 'Guest House': 10000},
        'Kilimani': {'Serviced Apartment': 16000, 'Boutique Hotel': 20000, 'Guest House': 11000},
        'Karen': {'Serviced Apartment': 20000, 'Boutique Hotel': 25000, 'Guest House': 13000},
        'Lavington': {'Serviced Apartment': 17000, 'Boutique Hotel': 21000, 'Guest House': 11500},
    }
    
    return base_prices.get(location, {}).get(property_type, 15000)

def run_scraper(user_id: int, property_id: int, location: str = 'Westlands', limit: int = 200, headless: bool = True):
    """
    Enhanced scraper with realistic Nairobi hospitality data
    """
    from .models import Property
    property_obj = Property.query.get(property_id)
    if not property_obj:
        return 0

    competitors = NAIROBI_HOTELS.get(location, NAIROBI_HOTELS['Westlands'])
    entries_saved = 0
    base_date = datetime.now().date()
    
    # Clear existing data for this property to avoid duplicates
    CompetitorPrice.query.filter_by(user_id=user_id, property_id=property_id).delete()
    
    # Generate exactly 200 entries across 60 days
    for days_ago in range(60):
        if entries_saved >= limit:
            break
            
        entry_date = base_date - timedelta(days=days_ago)
        
        # Apply Nairobi seasonal pricing
        seasonal_factor = get_nairobi_seasonal_factor(entry_date)
        
        # Create 3-4 entries per day
        entries_today = min(4, limit - entries_saved)
        daily_competitors = random.sample(competitors, entries_today)
        
        for competitor in daily_competitors:
            base_price = get_location_base_price(location, property_obj.type)
            
            # Apply platform-specific pricing variations
            platform_factor = random.uniform(0.9, 1.1)
            
            # Weekend pricing premium (Friday, Saturday)
            if entry_date.weekday() in [4, 5]:
                weekend_factor = random.uniform(1.1, 1.3)
            else:
                weekend_factor = 1.0
            
            final_price = round(base_price * seasonal_factor * platform_factor * weekend_factor * random.uniform(0.95, 1.05))
            
            availability_options = ["Available", "Limited", "Last Unit", "Sold Out", "Good Availability"]
            availability_weights = [0.4, 0.3, 0.15, 0.05, 0.1]
            
            competitor_entry = CompetitorPrice(
                user_id=user_id,
                property_id=property_id,
                competitor_name=competitor,
                platform=random.choice(PLATFORMS),
                price=final_price,
                currency='KES',
                date=entry_date,
                availability=random.choices(availability_options, availability_weights)[0],
                min_stay=random.randint(1, 3),
                rating=round(random.uniform(3.5, 5.0), 2),
                review_count=random.randint(10, 500)
            )
            
            db.session.add(competitor_entry)
            entries_saved += 1
    
    db.session.commit()
    print(f"🎯 Generated {entries_saved} Nairobi competitor price entries in KES")
    return entries_saved