#!/usr/bin/env python3
"""
Script to generate Aforro portfolio report in HTML format.
Fetches current values from IGCP API and generates an HTML report.
"""

import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class AforroSeries(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


@dataclass
class Subscription:
    series: AforroSeries
    subscription_number: str
    acquisition_date: datetime
    units: int
    unit_value: Optional[float] = None
    total_value: Optional[float] = None
    acquisition_value: Optional[float] = None


class IGCPClient:
    """Client to fetch certificate values from IGCP API."""
    
    BASE_URL = "https://www.igcp.pt"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def _adjust_dates(self, date: datetime, acquisition_date: datetime) -> tuple[datetime, datetime]:
        """
        Adjust dates for IGCP API: send both as day 01.
        If date.day >= acquisition.day, keep same month, else use previous month.
        """
        d_day = date.day
        a_day = acquisition_date.day
        
        # Acquisition date: first day of its month
        req_acq = datetime(acquisition_date.year, acquisition_date.month, 1)
        
        # Request date logic
        if d_day < a_day:
            # Use previous month
            if date.month == 1:
                req_date = datetime(date.year - 1, 12, 1)
            else:
                req_date = datetime(date.year, date.month - 1, 1)
        else:
            # Use current month
            req_date = datetime(date.year, date.month, 1)
        
        return req_date, req_acq
    
    def fetch_value(
        self, 
        series: AforroSeries, 
        date: datetime,
        acquisition_date: datetime, 
        quantity: int
    ) -> Dict[str, float]:
        """
        Fetch the current value from IGCP API.
        Returns dict with 'field_value' and 'field_acquisition_value'.
        """
        req_date, req_acq = self._adjust_dates(date, acquisition_date)
        
        url = f"{self.BASE_URL}/pt/api/simulator-value/query"
        params = {
            'field_serie': series.value,
            'field_field_date': req_date.strftime('%d/%m/%Y'),
            'field_field_acquisition_date': req_acq.strftime('%d/%m/%Y'),
            'quantity': str(quantity)
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0]
            else:
                raise ValueError(f"Unexpected API response format: {data}")
        except Exception as e:
            print(f"Error fetching value for {series.value} subscription: {e}")
            raise


def format_number(value: float, decimals: int = 2) -> str:
    """Format number in US style (dot for decimal, comma for thousands)."""
    return f"{value:,.{decimals}f}"


def generate_html_report(subscriptions: List[Subscription], output_file: str = "out/index.html"):
    """Generate HTML report with subscription details."""
    
    # Calculate totals
    total_current_value = sum(sub.total_value for sub in subscriptions if sub.total_value)
    total_invested_value = sum(sub.acquisition_value for sub in subscriptions if sub.acquisition_value)
    
    # Calculate ratio
    ratio = total_current_value / total_invested_value if total_invested_value > 0 else 0
    
    # Generate HTML in exact same format as out-example.html
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CA</title>
</head>
<style>
body {{ font-family: Arial; font-size: 0.3cm }}
</style>

<body>
    <h1>CA</h1>
    <div id="currentMarketPrice" class="container">
        <h2 class="title">Most Recent Value:</h2>
        <h3 id="currentMarketPrice_value">{format_number(ratio, 10)}</h3>
    </div>
</body>
</html>"""
    
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Report generated: {output_file}")


def load_subscriptions(config_file: str = "subscriptions.json") -> List[Subscription]:
    """Load subscriptions from JSON config file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        subscriptions = []
        for item in data:
            sub = Subscription(
                series=AforroSeries(item['series']),
                subscription_number=item['subscription_number'],
                acquisition_date=datetime.fromisoformat(item['acquisition_date']),
                units=item['units']
            )
            subscriptions.append(sub)
        
        return subscriptions
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found.")
        print("Please create a subscriptions.json file. See subscriptions.example.json for format.")
        exit(1)
    except Exception as e:
        print(f"Error loading config file: {e}")
        exit(1)


def main():
    """Main function to fetch data and generate report."""
    
    # Load subscriptions from config file
    subscriptions = load_subscriptions()
    
    # Initialize IGCP client
    client = IGCPClient()
    today = datetime.now()
    
    print("Fetching current values from IGCP API...")
    
    # Fetch current values for each subscription
    for i, sub in enumerate(subscriptions, 1):
        print(f"  [{i}/{len(subscriptions)}] Fetching {sub.series.value} - {sub.subscription_number}...", end=' ')
        try:
            result = client.fetch_value(
                series=sub.series,
                date=today,
                acquisition_date=sub.acquisition_date,
                quantity=sub.units
            )
            
            sub.total_value = result['field_value']
            sub.acquisition_value = result['field_acquisition_value']
            sub.unit_value = sub.total_value / sub.units if sub.units > 0 else 0
            
            print(f"✓ {format_number(sub.total_value, 2)} EUR")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Generate HTML report
    print("\nGenerating HTML report...")
    generate_html_report(subscriptions)
    
    # Print summary
    total_current = sum(sub.total_value for sub in subscriptions if sub.total_value)
    total_invested = sum(sub.acquisition_value for sub in subscriptions if sub.acquisition_value)
    ratio = total_current / total_invested if total_invested > 0 else 0
    
    print(f"\nTotal current value: {format_number(total_current, 2)} EUR")
    print(f"Total invested value: {format_number(total_invested, 2)} EUR")
    print(f"Ratio (current/invested): {format_number(ratio, 10)}")


if __name__ == "__main__":
    main()
