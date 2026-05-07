"""
Data Analysis Module for Books Scraping Project
"""

import pandas as pd
import os
import glob
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple


class DataAnalyzer:

    def __init__(self, cleaned_dir="data/cleaned"):
        self.cleaned_dir = cleaned_dir
        self.df = None
        self.load_data()

    # 📂 Charger automatiquement le dernier fichier cleaned
    def load_data(self):
        """Load data from single cleaned file"""
        files = glob.glob(os.path.join(self.cleaned_dir, "*.csv"))

        if not files:
            print("No cleaned files found in data/cleaned")
            self.df = pd.DataFrame()
            return self.df

        # Look for cleaned_books.csv file (single big file)
        cleaned_books_files = [f for f in files if 'cleaned_books.csv' in f]
        
        if cleaned_books_files:
            latest_file = max(cleaned_books_files, key=os.path.getctime)
            print(f"Loading cleaned data from: {latest_file}")
            self.df = pd.read_csv(latest_file)
        else:
            # Fallback to any cleaned CSV file
            latest_file = max(files, key=os.path.getctime)
            print(f"Fallback to latest cleaned file: {latest_file}")
            self.df = pd.read_csv(latest_file)
        
        return self.df

    # 📊 TOP / BOTTOM BOOKS
    def get_top_bottom_books(self, metric: str = 'price_excl_tax', n: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Return top n and bottom n books by specified metric"""
        if self.df is None:
            self.load_data()
        sorted_df = self.df.sort_values(metric, ascending=False)
        top_n = sorted_df.head(n)
        bottom_n = sorted_df.tail(n)
        return top_n, bottom_n

    # 📊 MÉDIANE
    def calculate_median_stats(self) -> Dict[str, float]:
        """Calculate median statistics for numeric fields"""
        if self.df is None:
            self.load_data()
        numeric_cols = ['price_excl_tax', 'price_incl_tax', 'tax', 'stock_count', 'number_of_reviews']
        return {col: self.df[col].median() for col in numeric_cols}
    
    def get_median(self):
        """Legacy method for compatibility"""
        return self.calculate_median_stats()

    def get_available_categories(self) -> List[str]:
        """Get list of available categories from the data"""
        if self.df is not None and 'category' in self.df.columns:
            return sorted(self.df['category'].unique().tolist())
        else:
            return []

    # 📊 CATÉGORIES
    def category_analysis(self):
        return self.df["category"].value_counts()

    # 📦 STOCK
    def stock_analysis(self):
        return {
            "in_stock": int(self.df["in_stock"].sum()),
            "out_of_stock": int((~self.df["in_stock"]).sum())
        }

    # 📊 PLOTLY VISUALIZATIONS
    def create_price_distribution(self) -> go.Figure:
        """Create price distribution histogram"""
        if self.df is None:
            self.load_data()
        fig = px.histogram(self.df, x='price_excl_tax', title='Price Distribution', 
                         labels={'price_excl_tax': 'Price (£)', 'count': 'Frequency'})
        fig.update_layout(template='plotly_white')
        return fig
    
    def create_category_chart(self) -> go.Figure:
        """Create category distribution pie chart"""
        if self.df is None:
            self.load_data()
        category_counts = self.df['category'].value_counts().head(10)
        fig = px.pie(values=category_counts.values, names=category_counts.index, 
                    title='Top 10 Book Categories')
        fig.update_layout(template='plotly_white')
        return fig
    
    def create_availability_chart(self) -> go.Figure:
        """Create stock availability bar chart"""
        if self.df is None:
            self.load_data()
        stock_counts = self.df['in_stock'].value_counts()
        fig = px.bar(x=['In Stock', 'Out of Stock'], y=[stock_counts.get(True, 0), stock_counts.get(False, 0)],
                    title='Stock Availability', labels={'x': 'Status', 'y': 'Number of Books'})
        fig.update_layout(template='plotly_white')
        return fig
    
    def create_price_evolution(self) -> go.Figure:
        """Create price trends line chart (synthetic data for demonstration)"""
        if self.df is None:
            self.load_data()
        # Create synthetic price evolution data
        price_trend = self.df['price_excl_tax'].sort_values().reset_index(drop=True)
        fig = px.line(x=range(len(price_trend)), y=price_trend, 
                    title='Price Evolution (Sorted by Price)',
                    labels={'x': 'Book Index (Sorted by Price)', 'y': 'Price (£)'})
        fig.update_layout(template='plotly_white')
        return fig
    
    def create_top_bottom_chart(self, metric: str = 'price_excl_tax') -> go.Figure:
        """Create top/bottom books bar chart"""
        if self.df is None:
            self.load_data()
        top, bottom = self.get_top_bottom_books(metric, 5)
        combined = pd.concat([top, bottom])
        labels = ['Top'] * 5 + ['Bottom'] * 5
        fig = px.bar(combined, x='title', y=metric, color=labels,
                    title=f'Top/Bottom 5 Books by {metric.replace("_", " ").title()}',
                    labels={'title': 'Book Title', metric: metric.replace("_", " ").title()})
        fig.update_layout(template='plotly_white', xaxis_tickangle=-45)
        return fig


# 🧪 TEST DU MODULE
if __name__ == "__main__":

    analyzer = DataAnalyzer()

    # Charger les données
    df = analyzer.load_data()

    print("\n===== TOP 5 BOOKS =====")
    top, bottom = analyzer.get_top_bottom_books()
    print(top[["title", "price_excl_tax"]])

    print("\n===== MÉDIANE =====")
    print(analyzer.get_median())

    print("\n===== MOYENNE =====")
    print(analyzer.get_mean())

    print("\n===== CATÉGORIES =====")
    print(analyzer.category_analysis().head())

    print("\n===== STOCK =====")
    print(analyzer.stock_analysis())

    print("\n===== GRAPHIQUES =====")

    analyzer.plot_categories()
    analyzer.plot_prices()
    analyzer.plot_stock()

    print("\n ANALYSIS COMPLETED SUCCESSFULLY")