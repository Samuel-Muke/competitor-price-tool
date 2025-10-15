import os
import argparse
from datetime import datetime, timedelta
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import current_app
from .models import CompetitorPrice, Forecast, Property
from . import db

def make_pdf(user_id: int, property_id: int, output_path: str):
    """
    Generate a clean, well-formatted PDF report with business insights and recommendations.
    """
    try:
        property = Property.query.get(property_id)
        historical_data = CompetitorPrice.query.filter_by(
            user_id=user_id, property_id=property_id
        ).all()
        forecast_data = Forecast.query.filter_by(
            user_id=user_id, property_id=property_id
        ).all()

        historical_df = pd.DataFrame([{
            'date': entry.date,
            'price': float(entry.price),
            'competitor': entry.competitor_name
        } for entry in historical_data]) if historical_data else pd.DataFrame()

        # Default insights
        insights = {
            'avg_competitor_price': 0,
            'price_difference': 0,
            'price_position': 'Unknown',
            'market_trend': 'Unknown',
            'recommendation': 'Collect more market data for better insights',
            'data_confidence': 'Low',
            'competitors_count': 0,
            'total_data_points': len(historical_data)
        }

        # Compute insights only if data exists
        if historical_data and not historical_df.empty:
            avg_price = historical_df['price'].mean()
            diff = float(property.base_price) - avg_price if property else 0
            insights.update({
                'avg_competitor_price': avg_price,
                'price_difference': diff,
                'competitors_count': len(historical_df['competitor'].unique())
            })

            # Price positioning
            if diff > 2000:
                insights['price_position'] = "Premium Position"
                insights['recommendation'] = "You're priced significantly above market. Consider if your amenities justify this premium."
            elif diff > 500:
                insights['price_position'] = "Above Average"
                insights['recommendation'] = "Good pricing strategy. You're competitively positioned with room for premium features."
            elif diff < -2000:
                insights['price_position'] = "Budget Position"
                insights['recommendation'] = "You're priced well below market. Consider increasing price to maximize revenue."
            elif diff < -500:
                insights['price_position'] = "Below Average"
                insights['recommendation'] = "You have pricing flexibility. Consider a moderate increase to match market rates."
            else:
                insights['price_position'] = "Competitively Priced"
                insights['recommendation'] = "Excellent! Your pricing aligns perfectly with market conditions."

            # Trend & confidence
            if len(historical_data) > 14:
                recent_cutoff = datetime.now().date() - timedelta(days=7)
                recent = historical_df[historical_df['date'] >= recent_cutoff]['price'].mean()
                old = historical_df[historical_df['date'] < recent_cutoff]['price'].mean()

                if recent > old * 1.05:
                    insights['market_trend'] = "Strong Upward Trend ↗"
                elif recent < old * 0.95:
                    insights['market_trend'] = "Strong Downward Trend ↘"
                else:
                    insights['market_trend'] = "Stable Market →"

            data_len = len(historical_data)
            if data_len > 100:
                insights['data_confidence'] = "Very High"
            elif data_len > 50:
                insights['data_confidence'] = "High"
            elif data_len > 20:
                insights['data_confidence'] = "Medium"

        # Chart setup
        chart_path = output_path + ".png"
        plt.figure(figsize=(11, 7))
        if not historical_df.empty:
            daily_avg = historical_df.groupby('date')['price'].mean()
            plt.plot(daily_avg.index, daily_avg.values, label='Market Avg Price', linewidth=3, color='#1f77b4', marker='o')
            if len(daily_avg) > 7:
                plt.plot(daily_avg.index, daily_avg.rolling(7).mean(), 'r--', label='7-Day Trend', linewidth=2)
        if property:
            plt.axhline(y=float(property.base_price), color='#28a745', linestyle='-', linewidth=3,
                        label=f"Your Price: {float(property.base_price):,.0f} KES")
        if forecast_data:
            f_dates = [f.date for f in forecast_data]
            f_prices = [float(f.predicted_price) for f in forecast_data]
            plt.plot(f_dates, f_prices, 'orange', marker='s', linestyle=':', linewidth=2.5, label='Forecast (7 Days)')

        plt.legend(fontsize=9)
        plt.title(f"Price Intelligence Dashboard – {property.name if property else 'Property'}", fontsize=15, fontweight='bold', color='#003366')
        plt.xlabel("Date"); plt.ylabel("Price (KES)")
        plt.grid(True, alpha=0.3); plt.xticks(rotation=45)
        plt.tight_layout(); plt.savefig(chart_path, dpi=150); plt.close()

        # Begin PDF
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        margin = 70
        line_gap = 15
        y = height - 70

        # Title
        pdf.setFont("Helvetica-Bold", 18)
        pdf.setFillColorRGB(0.1, 0.2, 0.6)
        pdf.drawString(margin, y, "PRICE INTELLIGENCE REPORT")

        y -= 20
        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(0.3, 0.3, 0.3)
        pdf.drawString(margin, y, "Data-Driven Pricing Strategy for Maximum Revenue")

        # Property Box
        y -= 35
        pdf.setFillColorRGB(0.9, 0.95, 1)
        pdf.rect(margin - 2, y - 55, width - 2 * margin + 4, 55, fill=1)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margin, y - 15, "PROPERTY OVERVIEW")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(margin, y - 30, f"Property: {property.name if property else 'N/A'}")
        pdf.drawString(margin, y - 45, f"Location: {property.location if property else 'N/A'}")
        pdf.drawString(width / 2, y - 30, f"Your Price: KES {float(property.base_price):,.2f}")
        pdf.drawString(width / 2, y - 45, f"Report Date: {datetime.now().strftime('%Y-%m-%d')}")

        # Insights
        y -= 90
        pdf.setFont("Helvetica-Bold", 13)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        pdf.drawString(margin, y, "KEY BUSINESS INSIGHTS")

        y -= 25
        pdf.setFont("Helvetica", 10)
        items = [
            f"• Market Avg Price: KES {insights['avg_competitor_price']:,.2f}",
            f"• Your Price Position: {insights['price_position']}",
            f"• Price Difference: KES {insights['price_difference']:,.2f}",
            f"• Market Trend: {insights['market_trend']}",
            f"• Competitors Tracked: {insights['competitors_count']}",
            f"• Data Confidence: {insights['data_confidence']}"
        ]
        for item in items:
            pdf.drawString(margin + 10, y, item)
            y -= line_gap

        # Recommendation Box
        y -= 20
        pdf.setFillColorRGB(0.95, 1, 0.95)
        pdf.rect(margin - 2, y - 40, width - 2 * margin + 4, 40, fill=1)
        pdf.setFillColorRGB(0, 0.5, 0)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margin, y - 15, "STRATEGIC RECOMMENDATION")

        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(0, 0, 0)
        rec = insights['recommendation']
        wrapped = []
        words = rec.split(' ')
        line = ""
        for w in words:
            if len(line + w) < 90:
                line += w + " "
            else:
                wrapped.append(line.strip())
                line = w + " "
        wrapped.append(line.strip())

        y -= 35
        for w in wrapped:
            pdf.drawString(margin + 10, y, w)
            y -= line_gap

        # Chart
        try:
            pdf.drawImage(chart_path, margin, y - 270, width - 2 * margin, 250)
            y -= 290
            pdf.setFont("Helvetica-Oblique", 9)
            pdf.drawString(margin, y, "Market price trends with 7-day forecast and moving average")
        except Exception:
            pdf.drawString(margin, y, "Chart unavailable")

        # Forecast
        if forecast_data:
            y -= 20
            pdf.setFillColorRGB(1, 0.96, 0.9)
            pdf.rect(margin - 2, y - 85, width - 2 * margin + 4, 85, fill=1)
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(margin, y - 15, "7-DAY FORECAST OUTLOOK")
            pdf.setFont("Helvetica", 9)
            col1, col2 = margin + 10, width / 2
            f_y = y - 30
            for i, f in enumerate(forecast_data):
                symbol = "🔺" if float(f.predicted_price) > float(property.base_price) else "🔻" if float(f.predicted_price) < float(property.base_price) else "➡️"
                line = f"{f.date.strftime('%a %d %b')}: KES {float(f.predicted_price):,.2f} {symbol}"
                if i < 4:
                    pdf.drawString(col1, f_y, line)
                    f_y -= line_gap
                else:
                    pdf.drawString(col2, y - 30 - (i - 4) * line_gap, line)

        # Footer
        pdf.setFont("Helvetica-Oblique", 8)
        pdf.setFillColorRGB(0.3, 0.3, 0.3)
        pdf.drawString(margin, 30, "Generated by Price Intelligence Platform • Turning Market Data into Revenue Opportunities")

        pdf.showPage()
        pdf.save()

        try:
            os.remove(chart_path)
        except:
            pass

        return output_path

    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")
