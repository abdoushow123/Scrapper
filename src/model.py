"""
Machine Learning Model Module for Books Scraping Project
Placeholder for future ML model functionality
"""

import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from typing import Tuple, Optional


class BookModel:
    """ML Model for book data"""
    
    def __init__(self, cleaned_dir: str = "data/cleaned"):
        """
        Initialize the ML model
        
        Args:
            cleaned_dir: Directory containing cleaned data
        """
        self.cleaned_dir = cleaned_dir
    
    def load_data(self, filename: str = "cleaned_books.csv") -> pd.DataFrame:
        """
        Load cleaned data for model training
        
        Args:
            filename: Name of the cleaned data file
            
        Returns:
            DataFrame with cleaned data
        """
        filepath = os.path.join(self.cleaned_dir, filename)
        return pd.read_csv(filepath)
    
    def train_model(self, df: pd.DataFrame):
        """
        Train ML model on book data
        
        Args:
            df: DataFrame with cleaned book data
        """
        # Placeholder for model training
        pass
    
    def predict(self, features):
        """
        Make predictions using trained model
        
        Args:
            features: Input features for prediction
            
        Returns:
            Prediction results
        """
        # Placeholder for predictions
        pass


def _get_latest_cleaned_file(cleaned_dir: str) -> Optional[str]:
    files = glob.glob(os.path.join(cleaned_dir, "*.csv"))
    if not files:
        return None
    return max(files, key=os.path.getctime)


def predict_next_price(cleaned_dir: str = "data/cleaned") -> Tuple[Optional[float], Optional[LinearRegression], Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Load the latest cleaned CSV, train a LinearRegression on index -> price,
    and predict the next price (index + 1).

    Returns:
        predicted_value (float) or None on error,
        trained model or None,
        X (numpy array) used for training or None,
        y (numpy array) used for training or None
    """
    try:
        latest = _get_latest_cleaned_file(cleaned_dir)
        if not latest:
            raise FileNotFoundError(f"No cleaned CSV found in {cleaned_dir}")

        df = pd.read_csv(latest)

        if 'price' not in df.columns and 'price_excl_tax' in df.columns:
            # support alternate column name
            price_col = 'price_excl_tax'
        elif 'price' in df.columns:
            price_col = 'price'
        else:
            raise KeyError("No 'price' or 'price_excl_tax' column found in latest cleaned CSV")

        # Drop NA and ensure numeric
        series = pd.to_numeric(df[price_col], errors='coerce').dropna()
        if series.empty:
            raise ValueError("Price column is empty or contains no numeric values")

        # Use index as time variable
        X = series.index.to_numpy().reshape(-1, 1)
        y = series.to_numpy()

        # Train linear regression
        model = LinearRegression()
        model.fit(X, y)

        next_index = np.array([[X.max() + 1]])
        pred = float(model.predict(next_index)[0])

        return pred, model, X.flatten(), y

    except Exception as e:
        print(f"predict_next_price error: {e}")
        return None, None, None, None


def plot_prediction(model: LinearRegression, X: np.ndarray, y: np.ndarray, predicted_value: float):
    """
    Plot real points, regression line and the predicted point using matplotlib.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    # scatter real points
    ax.scatter(X, y, label='Observed', color='C0')

    # regression line across range
    xs = np.linspace(X.min(), X.max() + 1, 100).reshape(-1, 1)
    ys = model.predict(xs)
    ax.plot(xs, ys, label='Regression', color='C1')

    # predicted point
    ax.scatter([X.max() + 1], [predicted_value], color='red', label='Predicted', zorder=5)

    ax.set_xlabel('Index (time)')
    ax.set_ylabel('Price')
    ax.set_title('Price prediction (Linear Regression)')
    ax.legend()
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    model = BookModel()
    print("ML model module - Ready for implementation")
