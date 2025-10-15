import argparse
from datetime import timedelta
import pandas as pd
from sklearn.linear_model import LinearRegression
from . import create_app, db
from .models import CompetitorPrice, Forecast

def run_forecast(user_id: int, property_id: int, horizon: int = 7):
    # Load historical price data
    historical_data = CompetitorPrice.query.filter_by(
        user_id=user_id, 
        property_id=property_id
    ).all()
    
    if not historical_data:
        return 0

    # Convert to DataFrame
    df = pd.DataFrame([{
        'date': entry.date, 
        'price': float(entry.price)
    } for entry in historical_data])
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Aggregate by date
    daily_avg = df.groupby('date', as_index=False)['price'].mean().sort_values('date')
    daily_avg['day_num'] = (daily_avg['date'] - daily_avg['date'].min()).dt.days

    X = daily_avg[['day_num']].values
    y = daily_avg['price'].values

    predictions = []
    
    if len(daily_avg) < 2:
        # Fallback: use last known average
        last_avg = float(daily_avg['price'].iloc[-1])
        for i in range(1, horizon + 1):
            prediction_date = daily_avg['date'].iloc[-1] + timedelta(days=i)
            predictions.append((prediction_date.date(), last_avg))
    else:
        # Linear regression forecast
        model = LinearRegression()
        model.fit(X, y)
        
        last_day = int(daily_avg['day_num'].max())
        for i in range(1, horizon + 1):
            prediction_date = daily_avg['date'].max() + timedelta(days=i)
            day_num = last_day + i
            predicted_price = float(model.predict([[day_num]])[0])
            predictions.append((prediction_date.date(), round(predicted_price, 2)))

    # Store forecasts in database
    forecast_dates = [date for date, _ in predictions]
    
    # Remove existing forecasts for these dates
    Forecast.query.filter(
        Forecast.user_id == user_id,
        Forecast.property_id == property_id,
        Forecast.date.in_(forecast_dates)
    ).delete(synchronize_session=False)

    # Add new forecasts
    for forecast_date, predicted_price in predictions:
        forecast = Forecast(
            user_id=user_id,
            property_id=property_id,
            date=forecast_date,
            predicted_price=predicted_price,
            model_info='LinearRegression'
        )
        db.session.add(forecast)

    db.session.commit()
    return len(predictions)

def cli():
    parser = argparse.ArgumentParser(description='Generate price forecasts')
    parser.add_argument('--user', type=int, required=True, help='User ID')
    parser.add_argument('--property', type=int, required=True, help='Property ID')
    parser.add_argument('--horizon', type=int, default=7, help='Forecast horizon in days')
    
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        forecasts_count = run_forecast(args.user, args.property, args.horizon)
        print(f"✅ Forecasts generated: {forecasts_count}")

if __name__ == '__main__':
    cli()