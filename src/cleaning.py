"""
Data Cleaning Module for Books Scraping Project
Cleans and standardizes scraped book data
"""

import os
import pandas as pd
import re
import glob
from typing import Dict, List, Optional
from datetime import datetime


class DataCleaner:
    """Cleaner for scraped book data"""
    
    def __init__(self, raw_dir: str = "data/raw", cleaned_dir: str = "data/cleaned"):
        """
        Initialize the data cleaner
        """
        self.raw_dir = raw_dir
        self.cleaned_dir = cleaned_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(cleaned_dir, exist_ok=True)

    # 🔥 NEW: get latest file automatically
    def get_latest_file(self):
        files = glob.glob(os.path.join(self.raw_dir, "*.csv"))
        
        if not files:
            raise FileNotFoundError("No CSV files found in data/raw")

        # Look for all_books.csv file (single big file)
        all_books_files = [f for f in files if 'all_books.csv' in f]
        
        if all_books_files:
            latest_file = max(all_books_files, key=os.path.getctime)
            print(f"Found all_books file: {latest_file}")
            return latest_file
        else:
            # Fallback to any CSV file
            latest_file = max(files, key=os.path.getctime)
            print(f"Fallback to latest file: {latest_file}")
            return latest_file
    
    def load_raw_data(self) -> List[Dict]:
        """
        Load raw data from single combined file
        
        Returns:
            List of book records
        """
        filepath = self.get_latest_file()
        
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
        if not price_str:
            return None
        
        cleaned = re.sub(r'[^\d.]', '', price_str)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def clean_availability(self, availability_str: str) -> Dict[str, int]:
        result = {
            'in_stock': False,
            'stock_count': 0
        }
        
        if not availability_str:
            return result
        
        result['in_stock'] = 'In stock' in availability_str
        
        match = re.search(r'(\d+)', availability_str)
        if match:
            result['stock_count'] = int(match.group(1))
        
        return result
    
    def clean_reviews(self, reviews_str: str) -> int:
        if not reviews_str:
            return 0
        
        word_to_num = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
            'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
            'twenty': 20
        }
        
        lower_str = reviews_str.lower().strip()
        return word_to_num.get(lower_str, 0)
    
    def clean_book_record(self, book: Dict) -> Dict:
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
        
        availability_info = self.clean_availability(book.get('Availability', ''))
        cleaned['in_stock'] = availability_info['in_stock']
        cleaned['stock_count'] = availability_info['stock_count']
        
        cleaned['number_of_reviews'] = self.clean_reviews(book.get('Number of reviews', ''))
        
        return cleaned
    
    def clean_all_data(self, data: List[Dict]) -> List[Dict]:
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.cleaned_dir, f"{timestamp}_{filename}")
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"Saved cleaned data to {filepath}")
    
    def get_latest_cleaned_files(self) -> Dict[str, str]:
        """Get latest cleaned files for each category"""
        files = glob.glob(os.path.join(self.cleaned_dir, "*.csv"))
        
        if not files:
            return {}
        
        # Group files by category
        category_files = {}
        
        for file in files:
            filename = os.path.basename(file)
            # Extract category name from filename
            if 'cleaned_' in filename:
                # Format: timestamp_cleaned_category_name.csv
                parts = filename.split('cleaned_')
                if len(parts) > 1:
                    category_part = parts[1].split('.csv')[0]
                    category_name = category_part.replace('_', ' ').title()
                    
                    # Keep only the latest file for each category
                    if category_name not in category_files or os.path.getctime(file) > os.path.getctime(category_files[category_name]):
                        category_files[category_name] = file
        
        return category_files
    
    def top_bottom_analysis(self, data: List[Dict], metric: str = 'price_excl_tax', n: int = 5) -> Dict[str, List[Dict]]:
        """Perform top/bottom analysis on specified metric"""
        if not data:
            return {'top_n': [], 'bottom_n': []}
        
        df = pd.DataFrame(data)
        
        if metric not in df.columns:
            return {'top_n': [], 'bottom_n': []}
        
        # Sort by metric and get top/bottom
        sorted_df = df.sort_values(metric, ascending=False)
        top_n = sorted_df.head(n).to_dict('records')
        bottom_n = sorted_df.tail(n).to_dict('records')
        
        return {
            'top_n': top_n,
            'bottom_n': bottom_n,
            'metric': metric,
            'count': n
        }
    
    def median_statistics(self, data: List[Dict]) -> Dict[str, float]:
        """Calculate median statistics for all numeric fields"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        numeric_cols = ['price_excl_tax', 'price_incl_tax', 'tax', 'stock_count', 'number_of_reviews']
        
        median_stats = {}
        for col in numeric_cols:
            if col in df.columns:
                median_stats[col] = float(df[col].median())
            else:
                median_stats[col] = 0.0
        
        return median_stats
    def generate_summary_report(self, data: List[Dict]) -> str:
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
        report.append(f"  - Mean: £{df['price_excl_tax'].mean():.2f}")
        report.append(f"  - Min: £{df['price_excl_tax'].min():.2f}")
        report.append(f"  - Max: £{df['price_excl_tax'].max():.2f}")
        
        # Add median statistics
        median_stats = self.median_statistics(data)
        if median_stats:
            report.append(f"\nMedian Statistics:")
            for key, value in median_stats.items():
                if key in ['price_excl_tax', 'price_incl_tax', 'tax']:
                    report.append(f"  - {key.replace('_', ' ').title()}: £{value:.2f}")
                else:
                    report.append(f"  - {key.replace('_', ' ').title()}: {value:.0f}")
        
        report.append(f"\nStock Availability:")
        report.append(f"  - In Stock: {df['in_stock'].sum()}")
        
        # Add top/bottom analysis
        top_bottom = self.top_bottom_analysis(data, 'price_excl_tax', 5)
        if top_bottom['top_n'] and top_bottom['bottom_n']:
            report.append(f"\nTop 5 Books by Price:")
            for i, book in enumerate(top_bottom['top_n'], 1):
                title = book.get('title', 'Unknown')[:50] + '...' if len(book.get('title', 'Unknown')) > 50 else book.get('title', 'Unknown')
                report.append(f"  {i}. {title} - £{book.get('price_excl_tax', 0):.2f}")
            
            report.append(f"\nBottom 5 Books by Price:")
            for i, book in enumerate(top_bottom['bottom_n'], 1):
                title = book.get('title', 'Unknown')[:50] + '...' if len(book.get('title', 'Unknown')) > 50 else book.get('title', 'Unknown')
                report.append(f"  {i}. {title} - £{book.get('price_excl_tax', 0):.2f}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def save_summary_report(self, data: List[Dict], filename: str = "cleaning_summary.txt"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.cleaned_dir, f"{timestamp}_{filename}")
        
        report = self.generate_summary_report(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Saved summary report to {filepath}")
        print(report)


def main():
    cleaner = DataCleaner()
    
    print("Starting data cleaning...")
    print("=" * 50)
    
    # Load raw data from single file
    raw_data = cleaner.load_raw_data()
    
    if not raw_data:
        print("No data to clean. Exiting.")
        return
    
    # Clean all data
    cleaned_data = cleaner.clean_all_data(raw_data)
    
    validation_stats = cleaner.validate_data(cleaned_data)
    print("\nValidation Statistics:")
    for key, value in validation_stats.items():
        print(f"  {key}: {value}")
    
    # Save cleaned data
    cleaner.save_cleaned_csv(cleaned_data, "cleaned_books.csv")
    cleaner.save_summary_report(cleaned_data)
    
    print("=" * 50)
    print("Data cleaning complete!")


if __name__ == "__main__":
    main()