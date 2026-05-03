"""
Data Analysis Module for Books Scraping Project
"""

import pandas as pd
import os
import glob
import matplotlib.pyplot as plt


class DataAnalyzer:

    def __init__(self, cleaned_dir="data/cleaned"):
        self.cleaned_dir = cleaned_dir
        self.df = None

    # 📂 Charger automatiquement le dernier fichier cleaned
    def load_data(self):
        files = glob.glob(os.path.join(self.cleaned_dir, "*.csv"))

        if not files:
            raise FileNotFoundError("Aucun fichier cleaned trouvé dans data/cleaned")

        latest_file = max(files, key=os.path.getctime)

        print(f" Loading file: {latest_file}")

        self.df = pd.read_csv(latest_file)
        return self.df

    # 📊 TOP / BOTTOM BOOKS
    def get_top_bottom_books(self, column="price_excl_tax"):
        top5 = self.df.sort_values(column, ascending=False).head(5)
        bottom5 = self.df.sort_values(column, ascending=True).head(5)
        return top5, bottom5

    # 📊 MÉDIANE
    def get_median(self):
        cols = ["price_excl_tax", "price_incl_tax", "tax", "stock_count", "number_of_reviews"]
        return self.df[cols].median()

    # 📊 MOYENNE
    def get_mean(self):
        cols = ["price_excl_tax", "price_incl_tax", "tax", "stock_count", "number_of_reviews"]
        return self.df[cols].mean()

    # 📊 CATÉGORIES
    def category_analysis(self):
        return self.df["category"].value_counts()

    # 📦 STOCK
    def stock_analysis(self):
        return {
            "in_stock": int(self.df["in_stock"].sum()),
            "out_of_stock": int((~self.df["in_stock"]).sum())
        }

    # 📊 GRAPH 1 - Catégories
    def plot_categories(self):
        self.df["category"].value_counts().head(10).plot(kind="bar")
        plt.title("Top 10 Categories")
        plt.xlabel("Category")
        plt.ylabel("Number of Books")
        plt.tight_layout()
        plt.show()

    # 📊 GRAPH 2 - Prix
    def plot_prices(self):
        self.df["price_excl_tax"].plot(kind="hist", bins=20)
        plt.title("Price Distribution")
        plt.xlabel("Price")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.show()

    # 📊 GRAPH 3 - Stock
    def plot_stock(self):
        self.df["in_stock"].value_counts().plot(kind="pie", autopct="%1.1f%%")
        plt.title("Stock Availability")
        plt.ylabel("")
        plt.tight_layout()
        plt.show()


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