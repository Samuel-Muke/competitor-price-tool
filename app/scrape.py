import random
from datetime import datetime, timedelta
from . import db
from .models import CompetitorPrice

def run_scraper(user_id: int, property_id: int, location: str = None, limit: int = 200, headless: bool = True):
    """
    Mock scraper that generates exactly 200 realistic competitor price entries in KES
    """
    competitors = [
        "LuxuryStays Inc", "Premium Rentals", "Elite Properties", "City View Apartments",
        "Urban Living Co", "Metro Homes", "Downtown Suites", "Skyline Rentals",
        "Parkside Residences", "Harbor View Homes", "Garden District Properties",
        "Metropolitan Living", "Uptown Apartments", "Riverside Condos"
    ]
    
    entries_saved = 0
    base_date = datetime.now().date()
    
    # Clear existing data for this property to avoid duplicates
    CompetitorPrice.query.filter_by(user_id=user_id, property_id=property_id).delete()
    
    # Generate exactly 200 entries across 60 days
    for days_ago in range(60):
        if entries_saved >= 200:
            break
            
        entry_date = base_date - timedelta(days=days_ago)
        
        # Create 3-4 entries per day
        entries_today = min(4, 200 - entries_saved)
        daily_competitors = random.sample(competitors, entries_today)
        
        for competitor in daily_competitors:
            # KES pricing: typical Nairobi apartment prices (8,000 - 25,000 KES)
            days_ago_factor = 1.0 + (days_ago * 0.002)  # Slight price increase over time
            base_price = random.uniform(8000, 25000)  # 8,000 - 25,000 KES range
            price = round(base_price * days_ago_factor * random.uniform(0.9, 1.1), 2)
            
            availability = random.choice(["Available", "Limited", "Last Unit", "Good Availability"])
            
            competitor_entry = CompetitorPrice(
                user_id=user_id,
                property_id=property_id,
                competitor_name=competitor,
                price=price,
                date=entry_date,
                availability=availability
            )
            
            db.session.add(competitor_entry)
            entries_saved += 1
    
    db.session.commit()
    print(f"🎯 Generated exactly {entries_saved} competitor price entries in KES")
    return entries_saved