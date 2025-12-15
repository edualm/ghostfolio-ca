# Ghostfolio Certificados de Aforro Integration

Integration for Portuguese Certificados de Aforro into [Ghostfolio](https://github.com/ghostfolio/ghostfolio).

This tool fetches real-time values from the IGCP (Agência de Gestão da Tesouraria e da Dívida Pública) API and generates an HTML file that can be imported as a manual scraper into Ghostfolio. It calculates your portfolio's performance ratio (current value / invested value) for tracking in Ghostfolio.

## Features

- 🔄 Fetches current values from official IGCP API
- 📊 Calculates portfolio performance ratio (current value / invested value)
- 📝 Generates HTML file for Ghostfolio manual scraper integration
- 🇵🇹 Portuguese number formatting
- 🔐 Privacy-focused: data stays local
- 💼 Track your Certificados de Aforro alongside your other investments in Ghostfolio

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ghostfolio-ca.git
cd ghostfolio-ca
```

2. Install dependencies:
```bash
uv sync
```

## Configuration

1. Create your subscriptions configuration file:
```bash
cp subscriptions.example.json subscriptions.json
```

2. Edit `subscriptions.json` with your Certificados de Aforro subscriptions:
```json
[
  {
    "series": "E",
    "subscription_number": "206769894",
    "acquisition_date": "2022-08-11",
    "units": 30000
  }
]
```

### Field Descriptions

- **series**: Certificate series (A, B, C, D, E, or F)
- **subscription_number**: Your subscription number
- **acquisition_date**: Date of acquisition in YYYY-MM-DD format
- **units**: Number of units purchased

## Usage

Run the script to generate the report:

```bash
uv run generate.py
```

This will:
1. Fetch current values for all subscriptions from IGCP API
2. Calculate total current value, invested value, and performance ratio
3. Generate `out.html` with the results

### Example Output

```
Fetching current values from IGCP API...
  [1/2] Fetching E - 206769894... ✓ 32 563,80 EUR
  [2/2] Fetching E - 206993329... ✓ 10 823,40 EUR

Generating HTML report...
Report generated: out.html

Total current value: 43 387,20 EUR
Total invested value: 40 000,00 EUR
Ratio (current/invested): 1,08468
```

The generated `out.html` contains a simple page with the performance ratio (current value divided by invested value) that can be scraped by Ghostfolio.

## Configuration for Ghostfolio

In your self-hosted Ghostfolio instance, create a manual scraper:

> Admin Control → Market Data → + (Add Asset Profile) → Add Manually

Fill in the asset details:
- **Symbol:** `CA` (or any symbol you prefer)
- **Name:** Certificados de Aforro
- **Asset Class:** Cash
- **Asset Sub Class:** Cash

Then configure the scraper:
- **Locale:** US (due to the number format used)
- **Mode:** Lazy (IGCP updates values daily)
- **URL:** Path to your `out.html` file (can be a local file path or hosted URL, e.g., `file:///path/to/out.html` or a GitHub raw URL if you host it)
- **Selector:** `#currentMarketPrice_value`

Save the configuration.

### Using in Ghostfolio

Once configured, add activities using your Certificados de Aforro as the asset:

1. Go to **Activities** → **Buy**
2. Select your CA symbol
3. Add each subscription as a separate buy activity:
   - Date: Your acquisition date
   - Quantity: Number of units
   - Unit cost: 1.00 (since the base value is always 1)

Ghostfolio will automatically track the current value using your scraper and calculate gains/losses based on the performance ratio.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Related Projects

- [ghostfolio-goldensgf-ppr](https://github.com/enen92/ghostfolio-goldensgf-ppr) - Similar integration for Golden SGF PPRs (Portuguese retirement savings plans)

## Disclaimer

This tool is for informational purposes only. Always verify values with official IGCP sources and your financial institution. This is an unofficial integration and is not affiliated with IGCP or Ghostfolio.
