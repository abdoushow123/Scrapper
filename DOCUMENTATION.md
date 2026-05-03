# Implementation Documentation

## Table of Contents
1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Scraper Module Implementation](#scraper-module-implementation)
4. [Cleaning Module Implementation](#cleaning-module-implementation)
5. [Step-by-Step Usage Guide](#step-by-step-usage-guide)

---

## Overview

This document provides a detailed explanation of the implementation of the web scraping and data cleaning modules for the books.toscrape.com project. The project extracts product information from an online bookstore and processes the data for analysis.

---

## Technology Stack

### Python Libraries Used

1. **requests (v2.31.0)**
   - Purpose: HTTP library for making web requests
   - Why: Simple, intuitive API for fetching web pages
   - Usage: Fetching HTML content from books.toscrape.com

2. **beautifulsoup4 (v4.12.2)**
   - Purpose: HTML and XML parsing library
   - Why: Easy navigation and searching of parsed HTML documents
   - Usage: Extracting data from HTML structure

3. **lxml (v4.9.3)**
   - Purpose: XML and HTML parser
   - Why: Fast and efficient parsing backend for BeautifulSoup
   - Usage: Parser backend for BeautifulSoup

4. **pandas (v2.1.1)**
   - Purpose: Data manipulation and analysis library
   - Why: Powerful data structures and data analysis tools
   - Usage: Converting cleaned data to CSV format and generating statistics

---

## Scraper Module Implementation

### File: `src/scraper.py`

#### Class: `BookScraper`

The scraper is implemented as a class to encapsulate all scraping logic and maintain state.

##### 1. Initialization (`__init__` method)

```python
def __init__(self, output_dir: str = "data/raw"):
```

**Purpose**: Initialize the scraper with configuration settings.

**Implementation Details**:
- Sets the base URL for the target website
- Creates a `requests.Session` object for persistent HTTP connections
- Sets a User-Agent header to mimic a real browser (prevents blocking)
- Creates the output directory if it doesn't exist

**Why Session Object**: Using a session object is more efficient than making individual requests because it:
- Maintains TCP connections (HTTP keep-alive)
- Persists cookies across requests
- Reduces overhead for multiple requests

##### 2. Page Fetching (`get_page` method)

```python
def get_page(self, url: str) -> BeautifulSoup:
```

**Purpose**: Fetch a web page and return a parsed BeautifulSoup object.

**Implementation Details**:
- Uses the session object to make a GET request
- Sets a 10-second timeout to prevent hanging
- Raises an exception for HTTP errors (4xx, 5xx)
- Parses the HTML content using lxml parser
- Returns None on error to handle failures gracefully

**Error Handling**: Catches `requests.RequestException` to handle network issues, invalid URLs, and server errors.

##### 3. Book Details Extraction (`get_book_details` method)

```python
def get_book_details(self, book_url: str) -> Dict[str, str]:
```

**Purpose**: Extract all required product information from a book's detail page.

**Implementation Details**:
- Fetches the book's detail page using `get_page()`
- Locates the product information table using CSS selector `table.table-striped`
- Iterates through table rows (tr elements) to extract key-value pairs
- Maps the extracted data to the required field names
- Additionally extracts the book title and category

**HTML Structure Analysis**:
The product information is stored in a table with the following structure:
```html
<table class="table table-striped">
  <tr>
    <th>UPC</th>
    <td>a897fe39b1053632</td>
  </tr>
  <!-- More rows for other fields -->
</table>
```

**Category Extraction**: Uses breadcrumb navigation to find the category:
- Finds the breadcrumb list (`ul.breadcrumb`)
- Extracts the third list item (index 2) which contains the category name

##### 4. Category Page Scraping (`get_books_from_page` method)

```python
def get_books_from_page(self, page_url: str) -> List[Dict[str, str]]:
```

**Purpose**: Extract all book URLs from a category page and scrape their details.

**Implementation Details**:
- Fetches the category page
- Finds all book elements using CSS selector `article.product_pod`
- For each book, extracts the link from the h3 > a element
- Constructs the full URL for the book's detail page
- Calls `get_book_details()` for each book
- Collects all book information into a list

**URL Construction**: Handles relative URLs by:
- Removing `../../../` prefixes
- Prepending the base URL and `/catalogue/` path

##### 5. Pagination Handling (`get_all_pages_in_category` method)

```python
def get_all_pages_in_category(self, category_url: str) -> List[Dict[str, str]]:
```

**Purpose**: Scrape all pages in a category by following pagination links.

**Implementation Details**:
- Starts with the first page URL
- Scrapes books from the current page
- Looks for a "next" button using CSS selector `li.next`
- If found, constructs the next page URL
- Handles relative URLs by navigating to parent directories
- Adds a 1-second delay between requests to be respectful to the server
- Continues until no next page is found

**Rate Limiting**: The 1-second delay (`time.sleep(1)`) is crucial to:
- Prevent overwhelming the server
- Avoid IP blocking
- Follow ethical scraping practices

##### 6. Full Site Scraping (`scrape_all_categories` method)

```python
def scrape_all_categories(self) -> List[Dict[str, str]]:
```

**Purpose**: Scrape all book categories on the website.

**Implementation Details**:
- Fetches the homepage
- Locates the category section using `div.side_categories`
- Extracts all category links
- Skips the first link ("Books" - which is the parent category)
- For each category:
  - Prints the category name for progress tracking
  - Calls `get_all_pages_in_category()` to scrape all books
  - Saves category-specific data separately
  - Adds a 1-second delay between categories
- Saves all data combined as `all_books.csv`

**Data Organization**: Saves both:
- Individual category files: `books_{category_name}.csv`
- Combined file: `all_books.csv`

##### 7. Data Saving (`save_data` method)

```python
def save_data(self, data: List[Dict], filename: str):
```

**Purpose**: Save scraped data to a CSV file with timestamp.

**Implementation Details**:
- Generates a timestamp in format `YYYYMMDD_HHMMSS`
- Creates the full file path with timestamp prefix
- Converts data to pandas DataFrame
- Writes DataFrame to CSV with UTF-8 encoding
- Prints confirmation message

**Timestamp Purpose**: Allows tracking when data was scraped and prevents overwriting previous runs.

---

## Cleaning Module Implementation

### File: `src/cleaning.py`

#### Class: `DataCleaner`

The cleaner is implemented as a class to encapsulate all data cleaning logic.

##### 1. Initialization (`__init__` method)

```python
def __init__(self, raw_dir: str = "data/raw", cleaned_dir: str = "data/cleaned"):
```

**Purpose**: Initialize the cleaner with directory paths.

**Implementation Details**:
- Sets input directory for raw data
- Sets output directory for cleaned data
- Creates output directory if it doesn't exist

##### 2. Data Loading (`load_raw_data` method)

```python
def load_raw_data(self, filename: str) -> List[Dict]:
```

**Purpose**: Load raw CSV data from file.

**Implementation Details**:
- Constructs the full file path
- If filename doesn't include timestamp, finds the most recent matching file
- Handles file not found errors gracefully
- Handles CSV parsing errors
- Returns empty list on error
- Prints confirmation message

**Smart File Finding**: Uses regex to check if filename has timestamp pattern `\d{8}_\d{6}`. If not, searches for the most recent file with that name.

##### 3. Price Cleaning (`clean_price` method)

```python
def clean_price(self, price_str: str) -> Optional[float]:
```

**Purpose**: Convert price string to float.

**Implementation Details**:
- Handles empty/None input
- Uses regex to remove all characters except digits and decimal point
- Pattern: `[^\d.]` matches anything that's not a digit or dot
- Converts the cleaned string to float
- Returns None if conversion fails

**Example Transformations**:
- `"£51.77"` → `51.77`
- `"£25.00"` → `25.00`
- `""` → `None`

##### 4. Availability Cleaning (`clean_availability` method)

```python
def clean_availability(self, availability_str: str) -> Dict[str, int]:
```

**Purpose**: Parse availability string to extract stock information.

**Implementation Details**:
- Returns a dictionary with two keys:
  - `in_stock`: Boolean indicating if item is available
  - `stock_count`: Integer count of available items
- Checks for "In stock" substring to determine availability
- Uses regex `\d+` to extract the first number from the string
- Returns default values (False, 0) if parsing fails

**Example Transformations**:
- `"In stock (22 available)"` → `{'in_stock': True, 'stock_count': 22}`
- `"In stock (1 available)"` → `{'in_stock': True, 'stock_count': 1}`
- `""` → `{'in_stock': False, 'stock_count': 0}`

##### 5. Reviews Cleaning (`clean_reviews` method)

```python
def clean_reviews(self, reviews_str: str) -> int:
```

**Purpose**: Convert review count from words to integers.

**Implementation Details**:
- Handles empty/None input
- Uses a dictionary mapping word numbers to integers
- Converts input to lowercase for case-insensitive matching
- Returns 0 if word not found in mapping

**Word Mapping**: Covers numbers from "zero" to "twenty" as these are the typical values on the website.

**Example Transformations**:
- `"Zero"` → `0`
- `"One"` → `1`
- `"Twenty"` → `20`
- `"unknown"` → `0`

##### 6. Single Record Cleaning (`clean_book_record` method)

```python
def clean_book_record(self, book: Dict) -> Dict:
```

**Purpose**: Clean a single book record using all cleaning methods.

**Implementation Details**:
- Creates a new dictionary with cleaned field names (snake_case)
- Applies `clean_price()` to price fields
- Applies `clean_availability()` to availability field
- Applies `clean_reviews()` to reviews field
- Strips whitespace from text fields
- Preserves original raw values for reference
- Returns the cleaned dictionary

**Field Mapping**:
- `UPC` → `upc`
- `Product Type` → `product_type`
- `Price (excl. tax)` → `price_excl_tax`
- `Price (incl. tax)` → `price_incl_tax`
- `Tax` → `tax`
- `Availability` → `raw_availability` + `in_stock` + `stock_count`
- `Number of reviews` → `raw_reviews` + `number_of_reviews`

##### 7. Batch Cleaning (`clean_all_data` method)

```python
def clean_all_data(self, data: List[Dict]) -> List[Dict]:
```

**Purpose**: Clean all book records in a list.

**Implementation Details**:
- Iterates through all records with index tracking
- Applies `clean_book_record()` to each record
- Catches and logs errors for individual records
- Continues processing even if some records fail
- Returns list of successfully cleaned records

**Error Handling**: Individual record errors don't stop the entire process, making the cleaning robust.

##### 8. Data Validation (`validate_data` method)

```python
def validate_data(self, data: List[Dict]) -> Dict[str, int]:
```

**Purpose**: Validate cleaned data and generate statistics.

**Implementation Details**:
- Checks for missing critical fields (UPC, title, category)
- Checks for missing or invalid prices
- Counts occurrences of each validation issue
- Returns a dictionary with validation statistics

**Validation Checks**:
- Empty UPC field
- Empty title field
- None price value
- Negative price value
- Empty category field

##### 9. CSV Saving (`save_cleaned_csv` method)

```python
def save_cleaned_csv(self, data: List[Dict], filename: str):
```

**Purpose**: Save cleaned data as CSV file using pandas.

**Implementation Details**:
- Converts list of dictionaries to pandas DataFrame
- Generates timestamp for filename
- Creates full file path
- Writes DataFrame to CSV without index
- Uses UTF-8 encoding
- Prints confirmation message

**Why Pandas**: Pandas provides a simple, efficient way to convert structured data to CSV format.

##### 10. Summary Report Generation (`generate_summary_report` method)

```python
def generate_summary_report(self, data: List[Dict]) -> str:
```

**Purpose**: Generate a comprehensive summary report of the cleaned data.

**Implementation Details**:
- Converts data to pandas DataFrame for analysis
- Calculates total record count
- Counts unique categories
- Shows top 5 categories by book count
- Calculates price statistics (mean, min, max)
- Calculates stock availability percentages
- Calculates review statistics
- Formats everything as a readable text report

**Statistics Calculated**:
- Total records
- Number of unique categories
- Category distribution
- Price statistics (mean, min, max)
- Stock availability (in stock vs out of stock)
- Review statistics (mean, max)

##### 11. Report Saving (`save_summary_report` method)

```python
def save_summary_report(self, data: List[Dict], filename: str = "cleaning_summary.txt"):
```

**Purpose**: Generate and save the summary report to a file.

**Implementation Details**:
- Calls `generate_summary_report()` to create the report
- Generates timestamp for filename
- Writes report to text file
- Prints the report to console
- Prints confirmation message

---

## Step-by-Step Usage Guide

### Step 1: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

This installs:
- `requests` for HTTP requests
- `beautifulsoup4` for HTML parsing
- `lxml` as the parser backend
- `pandas` for data manipulation

### Step 2: Run the Scraper

Execute the scraper to extract data from the website:

```bash
python src/scraper.py
```

**What happens**:
1. The scraper initializes and creates the `data/raw/` directory
2. It fetches the homepage of books.toscrape.com
3. It identifies all book categories
4. For each category:
   - It scrapes all pages in that category
   - It extracts book details for each book
   - It saves category-specific data
5. It saves all data combined as `all_books.csv`
6. It prints progress messages throughout

**Expected output**:
- Multiple CSV files in `data/raw/` (one per category)
- A combined file `all_books.csv` in `data/raw/`
- Console output showing progress

**Time required**: Approximately 2-5 minutes depending on internet speed and server response time.

### Step 3: Run the Cleaner

Execute the cleaner to process the scraped data:

```bash
python src/cleaning.py
```

**What happens**:
1. The cleaner initializes and creates the `data/cleaned/` directory
2. It loads the most recent `all_books.csv` file
3. It cleans each record:
   - Converts prices to floats
   - Parses availability information
   - Converts review words to numbers
4. It validates the cleaned data
5. It saves cleaned data as CSV
6. It generates and saves a summary report
7. It prints the summary report to console

**Expected output**:
- `cleaned_books.csv` in `data/cleaned/`
- `cleaning_summary.txt` in `data/cleaned/`
- Console output showing validation statistics and summary

### Step 4: Review the Results

Check the generated files:

1. **Raw Data**: `data/raw/all_books.csv`
   - Contains original scraped data
   - CSV format with all fields as strings

2. **Cleaned CSV**: `data/cleaned/cleaned_books.csv`
   - Contains cleaned and standardized data
   - Prices as floats
   - Availability parsed into structured fields
   - Reviews as integers
   - Easy to open in Excel or other tools

3. **Summary Report**: `data/cleaned/cleaning_summary.txt`
   - Statistics about the dataset
   - Category distribution
   - Price statistics
   - Availability statistics
   - Review statistics

### Step 5: Use the Data

The cleaned data is now ready for:
- Data analysis (using `src/analysis.py` when implemented)
- Machine learning (using `src/model.py` when implemented)
- Web application display (using `src/app.py` when implemented)

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

---

## Code Quality Features

### Error Handling
- Try-catch blocks for network operations
- Graceful handling of missing data
- Individual record errors don't stop batch processing

### Rate Limiting
- 1-second delay between page requests
- Respects server resources
- Prevents IP blocking

### Data Validation
- Checks for missing critical fields
- Validates data types
- Generates validation statistics

### Logging
- Progress messages during scraping
- Confirmation messages for file operations
- Error messages with context

### Flexibility
- Configurable directory paths
- Timestamped output files
- Modular design for easy extension

---

## Future Enhancements

Potential improvements for the scraper:
- Add proxy support
- Implement retry logic for failed requests
- Add configuration file for settings
- Support for incremental updates
- Parallel processing for faster scraping

Potential improvements for the cleaner:
- Add more data validation rules
- Implement data normalization
- Add outlier detection
- Support for multiple input formats
- Custom cleaning rules via configuration

---

## Conclusion

This implementation provides a robust, production-ready web scraping and data cleaning solution. The code is well-documented, handles errors gracefully, and follows best practices for ethical web scraping. The modular design makes it easy to extend and maintain.
