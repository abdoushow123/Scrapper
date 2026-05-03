# Books Web Scraping Project

A web scraping tool to extract product information from [books.toscrape.com](https://books.toscrape.com).

## Project Structure

```
projet-web-scraping/
│
├── data/
│   ├── raw/           # Raw scraped data (CSV format)
│   └── cleaned/       # Cleaned and processed data (CSV format)
│
├── src/
│   ├── scraper.py     # Web scraping module
│   ├── cleaning.py    # Data cleaning module
│   ├── analysis.py    # Data analysis module (placeholder)
│   ├── model.py       # ML model module (placeholder)
│   └── app.py         # Web application module (placeholder)
│
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── DOCUMENTATION.md   # Detailed implementation documentation
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Scraping Data

Run the scraper to extract book data from the website:

```bash
python src/scraper.py
```

This will:
- Scrape all book categories from books.toscrape.com
- Extract product information for each book
- Save raw data to `data/raw/` directory as CSV files

### Cleaning Data

Clean the scraped data:

```bash
python src/cleaning.py
```

This will:
- Load raw data from `data/raw/`
- Clean and standardize the data
- Validate data quality
- Save cleaned data to `data/cleaned/` as CSV

**Expected output**:
- Multiple CSV files in `data/raw/` (one per category)
- A combined file `all_books.csv` in `data/raw/`
- Console output showing progress

**Time required**: Approximately 2-5 minutes depending on internet speed and server response time.

### Step 3: Review the Results

Check the generated files:

1. **Raw Data**: `data/raw/all_books.csv`
   - Contains original scraped data
   - CSV format with all fields as strings

2. **Cleaned CSV**: `data/cleaned/cleaned_books.csv`
   - Contains cleaned and standardized data
   - Prices as floats
   - Availability parsed into structured fields
   - Reviews as integers

3. **Summary Report**: `data/cleaned/cleaning_summary.txt`
   - Statistics about the dataset
   - Category distribution
   - Price statistics
   - Availability statistics
   - Review statistics

### Troubleshooting

**Scraper Issues**:
- If the scraper fails, check your internet connection
- If you get blocked, wait a few minutes and try again
- The scraper includes rate limiting to avoid blocking

**Cleaner Issues**:
- Ensure the scraper has successfully run first
- Check that `data/raw/all_books.csv` exists
- If data loading fails, check the file path

**Import Errors**:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using Python 3.7 or higher

## Extracted Product Information

- **UPC**: Universal Product Code
- **Product Type**: Type/category of the product
- **Price (excl. tax)**: Price excluding tax
- **Price (incl. tax)**: Price including tax
- **Tax**: Tax amount
- **Availability**: Stock availability information
- **Number of reviews**: Review count

## Documentation

For detailed implementation information, see [DOCUMENTATION.md](DOCUMENTATION.md).

## Future Development

- Data analysis module implementation
- Machine learning model for price prediction
- Web application for data visualization
