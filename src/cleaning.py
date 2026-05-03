"""
Data Cleaning Module for Books Scraping Project
Cleans and standardizes scraped book data
"""

import os
import pandas as pd
import re
from typing import Dict, List, Optional
from datetime import datetime


class DataCleaner:
    """Cleaner for scraped book data"""
    
    def __init__(self, raw_dir: str = "data/raw", cleaned_dir: str = "data/cleaned"):
        """
        Initialize the data cleaner
        
        Args:
            raw_dir: Directory containing raw scraped data
            cleaned_dir: Directory to save cleaned data
        """
        self.raw_dir = raw_dir
        self.cleaned_dir = cleaned_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(cleaned_dir, exist_ok=True)
    
    def load_raw_data(self, filename: str) -> List[Dict]:
        """
        Load raw CSV data from file
        
        Args:
            filename: Name of the raw data file
            
        Returns:
            List of book dictionaries
        """
        filepath = os.path.join(self.raw_dir, filename)
        
        # Find the most recent file if filename doesn't include timestamp
        if not re.match(r'\d{8}_\d{6}', filename):
            files = [f for f in os.listdir(self.raw_dir) if f.endswith(filename)]
            if files:
                filepath = os.path.join(self.raw_dir, sorted(files)[-1])
        
        try:
            df = pd.read_csv(filepath)
            data = df.to_dict('records')
            print(f"Loaded {len(data)} records from {filepath}")
            return data
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return []
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []
    
    def clean_price(self, price_str: str) -> Optional[float]:
        """
        Clean and convert price string to float
        
        Args:
            price_str: Price string (e.g., "£51.77")
            
        Returns:
            Price as float or None if invalid
        """
        if not price_str:
            return None
        
        # Remove currency symbol and whitespace
        cleaned = re.sub(r'[^\d.]', '', price_str)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def clean_availability(self, availability_str: str) -> Dict[str, int]:
        """
        Parse availability string to extract stock information
        
        Args:
            availability_str: Availability string (e.g., "In stock (22 available)")
            
        Returns:
            Dictionary with 'in_stock' (bool) and 'stock_count' (int)
        """
        result = {
            'in_stock': False,
            'stock_count': 0
        }
        
        if not availability_str:
            return result
        
        # Check if in stock
        result['in_stock'] = 'In stock' in availability_str
        
        # Extract number using regex
        match = re.search(r'(\d+)', availability_str)
        if match:
            result['stock_count'] = int(match.group(1))
        
        return result
    
    def clean_reviews(self, reviews_str: str) -> int:
        """
        Convert review count string to integer
        
        Args:
            reviews_str: Review count string (e.g., "Zero", "One", "Twenty")
            
        Returns:
            Number of reviews as integer
        """
        if not reviews_str:
            return 0
        
        # Word to number mapping
        word_to_num = {
            'zero': 0,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12,
            'thirteen': 13,
            'fourteen': 14,
            'fifteen': 15,
            'sixteen': 16,
            'seventeen': 17,
            'eighteen': 18,
            'nineteen': 19,
            'twenty': 20
        }
        
        lower_str = reviews_str.lower().strip()
        return word_to_num.get(lower_str, 0)
    
    def clean_book_record(self, book: Dict) -> Dict:
        """
        Clean a single book record
        
        Args:
            book: Dictionary containing raw book data
            
        Returns:
            Dictionary with cleaned data
        """
        cleaned = {
            'upc': book.get('UPC', ''),
            'product_type': book.get('Product Type', ''),
            'price_excl_tax': self.clean_price(book.get('Price (excl. tax)', '')),
            'price_incl_tax': self.clean_price(book.get('Price (incl. tax)', '')),
            'tax': self.clean_price(book.get('Tax', '')),
            'title': book.get('title', '').strip(),
            'category': book.get('category', '').strip(),
            'url': book.get('url', ''),
            'raw_availability': book.get('Availability', ''),
            'raw_reviews': book.get('Number of reviews', '')
        }
        
        # Parse availability
        availability_info = self.clean_availability(book.get('Availability', ''))
        cleaned['in_stock'] = availability_info['in_stock']
        cleaned['stock_count'] = availability_info['stock_count']
        
        # Parse reviews
        cleaned['number_of_reviews'] = self.clean_reviews(book.get('Number of reviews', ''))
        
        return cleaned
    
    def clean_all_data(self, data: List[Dict]) -> List[Dict]:
        """
        Clean all book records
        
        Args:
            data: List of raw book dictionaries
            
        Returns:
            List of cleaned book dictionaries
        """
        cleaned_data = []
        
        for i, book in enumerate(data):
            try:
                cleaned_book = self.clean_book_record(book)
                cleaned_data.append(cleaned_book)
            except Exception as e:
                print(f"Error cleaning record {i}: {e}")
        
        print(f"Cleaned {len(cleaned_data)} records")
        return cleaned_data
    
    def validate_data(self, data: List[Dict]) -> Dict[str, int]:
        """
        Validate cleaned data and return statistics
        
        Args:
            data: List of cleaned book dictionaries
            
        Returns:
            Dictionary with validation statistics
        """
        stats = {
            'total_records': len(data),
            'missing_upc': 0,
            'missing_title': 0,
            'missing_price': 0,
            'invalid_price': 0,
            'missing_category': 0
        }
        
        for book in data:
            if not book.get('upc'):
                stats['missing_upc'] += 1
            if not book.get('title'):
                stats['missing_title'] += 1
            if book.get('price_excl_tax') is None:
                stats['missing_price'] += 1
            if book.get('price_excl_tax') is not None and book.get('price_excl_tax') < 0:
                stats['invalid_price'] += 1
            if not book.get('category'):
                stats['missing_category'] += 1
        
        return stats
    
    def save_cleaned_csv(self, data: List[Dict], filename: str):
        """
        Save cleaned data as CSV
        
        Args:
            data: List of cleaned book dictionaries
            filename: Name of the output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.cleaned_dir, f"{timestamp}_{filename}")
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"Saved cleaned data to {filepath}")
    
    def generate_summary_report(self, data: List[Dict]) -> str:
        """
        Generate a summary report of the cleaned data
        
        Args:
            data: List of cleaned book dictionaries
            
        Returns:
            String containing the summary report
        """
        if not data:
            return "No data to summarize"
        
        df = pd.DataFrame(data)
        
        report = []
        report.append("=" * 60)
        report.append("DATA CLEANING SUMMARY REPORT")
        report.append("=" * 60)
        report.append(f"\nTotal Records: {len(data)}")
        report.append(f"\nCategories: {df['category'].nunique()}")
        report.append(f"\nTop 5 Categories:")
        report.append(df['category'].value_counts().head().to_string())
        
        report.append(f"\nPrice Statistics:")
        report.append(f"  - Mean (excl. tax): £{df['price_excl_tax'].mean():.2f}")
        report.append(f"  - Min (excl. tax): £{df['price_excl_tax'].min():.2f}")
        report.append(f"  - Max (excl. tax): £{df['price_excl_tax'].max():.2f}")
        
        report.append(f"\nStock Availability:")
        report.append(f"  - In Stock: {df['in_stock'].sum()} ({df['in_stock'].mean()*100:.1f}%)")
        report.append(f"  - Out of Stock: {(~df['in_stock']).sum()} ({(~df['in_stock']).mean()*100:.1f}%)")
        
        report.append(f"\nReview Statistics:")
        report.append(f"  - Mean reviews: {df['number_of_reviews'].mean():.1f}")
        report.append(f"  - Max reviews: {df['number_of_reviews'].max()}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def save_summary_report(self, data: List[Dict], filename: str = "cleaning_summary.txt"):
        """
        Save summary report to file
        
        Args:
            data: List of cleaned book dictionaries
            filename: Name of the output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.cleaned_dir, f"{timestamp}_{filename}")
        
        report = self.generate_summary_report(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Saved summary report to {filepath}")
        print(report)


def main():
    """Main function to run the data cleaner"""
    cleaner = DataCleaner()
    
    print("Starting data cleaning...")
    print("=" * 50)
    
    # Load raw data
    raw_data = cleaner.load_raw_data("all_books.csv")
    
    if not raw_data:
        print("No data to clean. Exiting.")
        return
    
    # Clean data
    cleaned_data = cleaner.clean_all_data(raw_data)
    
    # Validate data
    validation_stats = cleaner.validate_data(cleaned_data)
    print("\nValidation Statistics:")
    for key, value in validation_stats.items():
        print(f"  {key}: {value}")
    
    # Save cleaned data
    cleaner.save_cleaned_csv(cleaned_data, "cleaned_books.csv")
    
    # Generate and save summary report
    cleaner.save_summary_report(cleaned_data)
    
    print("=" * 50)
    print("Data cleaning complete!")


if __name__ == "__main__":
    main()
