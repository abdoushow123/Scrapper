"""
Web Scraper for books.toscrape.com
Extracts product information: UPC, Product Type, Price (excl. tax), 
Price (incl. tax), Tax, Availability, Number of reviews
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from datetime import datetime
from typing import List, Dict


class BookScraper:
    """Scraper for books.toscrape.com website"""
    
    BASE_URL = "https://books.toscrape.com"
    
    def __init__(self, output_dir: str = "data/raw"):
        """
        Initialize the scraper
        
        Args:
            output_dir: Directory to save scraped data
        """
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def get_page(self, url: str) -> BeautifulSoup:
        """
        Fetch a page and return BeautifulSoup object
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object with parsed HTML
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def get_book_details(self, book_url: str) -> Dict[str, str]:
        """
        Extract product information from a book's detail page
        
        Args:
            book_url: URL of the book's detail page
            
        Returns:
            Dictionary containing product information
        """
        soup = self.get_page(book_url)
        if not soup:
            return None
        
        book_info = {}
        
        # Extract product information from the product table
        product_table = soup.find('table', class_='table table-striped')
        if product_table:
            rows = product_table.find_all('tr')
            for row in rows:
                header = row.find('th').text.strip()
                value = row.find('td').text.strip()
                book_info[header] = value
        
        # Map to required fields
        mapped_info = {
            'UPC': book_info.get('UPC', ''),
            'Product Type': book_info.get('Product Type', ''),
            'Price (excl. tax)': book_info.get('Price (excl. tax)', ''),
            'Price (incl. tax)': book_info.get('Price (incl. tax)', ''),
            'Tax': book_info.get('Tax', ''),
            'Availability': book_info.get('Availability', ''),
            'Number of reviews': book_info.get('Number of reviews', ''),
            'url': book_url,
            'title': soup.find('h1').text.strip() if soup.find('h1') else '',
            'category': self._extract_category(soup)
        }
        
        return mapped_info
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        """
        Extract book category from breadcrumb navigation
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Category name
        """
        breadcrumb = soup.find('ul', class_='breadcrumb')
        if breadcrumb:
            links = breadcrumb.find_all('li')
            if len(links) >= 3:
                return links[2].text.strip()
        return ''
    
    def get_books_from_page(self, page_url: str) -> List[Dict[str, str]]:
        """
        Get all book URLs from a category page and extract their details
        
        Args:
            page_url: URL of the category page
            
        Returns:
            List of book information dictionaries
        """
        soup = self.get_page(page_url)
        if not soup:
            return []
        
        books = []
        book_elements = soup.find_all('article', class_='product_pod')
        
        for book in book_elements:
            book_link = book.find('h3').find('a')
            if book_link:
                # Construct full URL for book detail page
                book_url = self.BASE_URL + '/catalogue/' + book_link['href'].replace('../../../', '')
                book_info = self.get_book_details(book_url)
                if book_info:
                    books.append(book_info)
                    print(f"Scraped: {book_info['title']}")
        
        return books
    
    def get_all_pages_in_category(self, category_url: str) -> List[Dict[str, str]]:
        """
        Scrape all pages in a category
        
        Args:
            category_url: URL of the category's first page
            
        Returns:
            List of all books in the category
        """
        all_books = []
        current_url = category_url
        
        while current_url:
            print(f"Scraping page: {current_url}")
            books = self.get_books_from_page(current_url)
            all_books.extend(books)
            
            # Check for next page
            soup = self.get_page(current_url)
            if soup:
                next_button = soup.find('li', class_='next')
                if next_button:
                    next_link = next_button.find('a')
                    if next_link:
                        # Handle relative URLs
                        if next_link['href'].startswith('..'):
                            # Navigate to parent directory
                            current_url = current_url.rsplit('/', 1)[0] + '/' + next_link['href'].replace('../', '')
                        else:
                            current_url = self.BASE_URL + '/catalogue/' + next_link['href']
                        time.sleep(1)  # Be respectful to the server
                    else:
                        current_url = None
                else:
                    current_url = None
            else:
                current_url = None
        
        return all_books
    
    def scrape_all_categories(self) -> List[Dict[str, str]]:
        """
        Scrape all categories on the website
        
        Returns:
            List of all books from all categories
        """
        soup = self.get_page(self.BASE_URL)
        if not soup:
            return []
        
        # Find all category links
        category_section = soup.find('div', class_='side_categories')
        if not category_section:
            return []
        
        category_links = category_section.find_all('a')
        all_books = []
        
        for link in category_links[1:]:  # Skip the first "Books" link
            category_name = link.text.strip()
            category_url = self.BASE_URL + '/' + link['href']
            print(f"\n=== Scraping category: {category_name} ===")
            
            books = self.get_all_pages_in_category(category_url)
            all_books.extend(books)
            
            # Save category data separately
            self.save_data(books, f"books_{category_name.lower().replace(' ', '_')}.csv")
            
            time.sleep(1)  # Be respectful to the server
        
        # Save all data
        self.save_data(all_books, "all_books.csv")
        return all_books
    
    def save_data(self, data: List[Dict], filename: str):
        """
        Save scraped data to CSV file
        
        Args:
            data: List of book information dictionaries
            filename: Name of the output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.output_dir, f"{timestamp}_{filename}")
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"Saved {len(data)} books to {filepath}")


def main():
    """Main function to run the scraper"""
    scraper = BookScraper()
    
    print("Starting web scraping...")
    print("=" * 50)
    
    # Scrape all categories
    all_books = scraper.scrape_all_categories()
    
    print("=" * 50)
    print(f"Scraping complete! Total books scraped: {len(all_books)}")


if __name__ == "__main__":
    main()
