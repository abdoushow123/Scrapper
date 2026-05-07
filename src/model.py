"""
Machine Learning Model Module for Books Scraping Project
Time series prediction model for book prices
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import os
import glob


class PricePredictor:
    """Time series prediction model for book prices"""
    
    def __init__(self, data_path: str = "data/cleaned/cleaned_books.csv"):
        self.data_path = data_path
        self.df = None
        self.model = LinearRegression()
        self.model_tax = LinearRegression()
        self.X = None
        self.y_price = None
        self.y_tax = None
        self.prepare_data()
    
    def load_data(self) -> pd.DataFrame:
        """Load data from the latest cleaned CSV file"""
        cleaned_dir = os.path.dirname(self.data_path)
        files = glob.glob(os.path.join(cleaned_dir, "*.csv"))
        
        if not files:
            raise FileNotFoundError(f"No cleaned CSV found in {cleaned_dir}")
        
        latest_file = max(files, key=os.path.getctime)
        self.df = pd.read_csv(latest_file)
        return self.df
    
    def prepare_time_series_data(self) -> None:
        """Prepare time series data for prediction"""
        if self.df is None:
            self.load_data()
        
        # Add synthetic date column for demonstration
        # In a real scenario, you'd have actual dates from scraping
        self.df['scrape_date'] = pd.date_range(start='2024-01-01', periods=len(self.df))
        self.df['day_number'] = (self.df['scrape_date'] - self.df['scrape_date'].min()).dt.days
        
        # Aggregate by date for time series
        daily_data = self.df.groupby('scrape_date').agg({
            'price_excl_tax': 'mean',
            'price_incl_tax': 'mean'
        }).reset_index()
        
        self.X = daily_data.index.values.reshape(-1, 1)
        self.y_price = daily_data['price_excl_tax'].values
        self.y_tax = daily_data['price_incl_tax'].values
    
    def prepare_data(self) -> None:
        """Alias for prepare_time_series_data for compatibility"""
        self.prepare_time_series_data()
    
    def train_price_prediction_model(self) -> None:
        """Train linear regression model for price trends"""
        if self.X is None or self.y_price is None:
            self.prepare_data()
        
        self.model.fit(self.X, self.y_price)
        self.model_tax.fit(self.X, self.y_tax)
    
    def train_model(self) -> None:
        """Alias for train_price_prediction_model"""
        self.train_price_prediction_model()
    
    def predict_future_prices(self, days: int = 7) -> Dict[str, np.ndarray]:
        """Predict prices for next specified number of days"""
        if self.X is None:
            self.train_model()
        
        last_day = self.X[-1][0]
        future_days = np.array([[last_day + i] for i in range(1, days + 1)])
        
        price_pred = self.model.predict(future_days)
        tax_pred = self.model_tax.predict(future_days)
        
        return {
            'predicted_prices': price_pred,
            'predicted_taxes': tax_pred,
            'future_days': future_days.flatten()
        }
    
    def predict_next_week(self) -> Dict[str, float]:
        """Predict prices for next 7 days and return summary"""
        predictions = self.predict_future_prices(7)
        
        price_pred = predictions['predicted_prices']
        tax_pred = predictions['predicted_taxes']
        
        return {
            'predicted_avg_price_next_week': np.mean(price_pred),
            'predicted_avg_tax_next_week': np.mean(tax_pred),
            'price_trend': 'increasing' if price_pred[-1] > price_pred[0] else 'decreasing',
            'price_change_percent': ((price_pred[-1] - price_pred[0]) / price_pred[0] * 100) if price_pred[0] != 0 else 0
        }
    
    def evaluate_model(self) -> Dict[str, float]:
        """Evaluate model accuracy metrics"""
        if self.X is None:
            self.train_model()
        
        # Make predictions on training data
        y_pred_price = self.model.predict(self.X)
        y_pred_tax = self.model_tax.predict(self.X)
        
        # Calculate metrics
        mse_price = mean_squared_error(self.y_price, y_pred_price)
        r2_price = r2_score(self.y_price, y_pred_price)
        
        mse_tax = mean_squared_error(self.y_tax, y_pred_tax)
        r2_tax = r2_score(self.y_tax, y_pred_tax)
        
        return {
            'price_mse': mse_price,
            'price_r2': r2_price,
            'tax_mse': mse_tax,
            'tax_r2': r2_tax,
            'avg_price': np.mean(self.y_price),
            'avg_tax': np.mean(self.y_tax)
        }


# Legacy compatibility functions
def predict_next_price(cleaned_dir: str = "data/cleaned") -> Tuple[Optional[float], Optional[LinearRegression], Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Legacy function for compatibility
    Load the latest cleaned CSV, train a LinearRegression on index -> price,
    and predict the next price (index + 1).
    """
    try:
        predictor = PricePredictor()
        predictor.train_model()
        
        # Get the next prediction
        next_day = np.array([[predictor.X[-1][0] + 1]])
        pred = float(predictor.model.predict(next_day)[0])
        
        return pred, predictor.model, predictor.X.flatten(), predictor.y_price
    
    except Exception as e:
        print(f"predict_next_price error: {e}")
        return None, None, None, None


if __name__ == "__main__":
    # Test the prediction model
    try:
        predictor = PricePredictor()
        predictor.train_model()
        
        print("=== Price Prediction Model ===")
        
        # Get predictions for next week
        predictions = predictor.predict_next_week()
        print(f"Predicted average price next week: £{predictions['predicted_avg_price_next_week']:.2f}")
        print(f"Predicted average tax next week: £{predictions['predicted_avg_tax_next_week']:.2f}")
        print(f"Price trend: {predictions['price_trend']}")
        print(f"Price change: {predictions['price_change_percent']:.2f}%")
        
        # Evaluate model
        metrics = predictor.evaluate_model()
        print("\n=== Model Evaluation ===")
        print(f"Price R² Score: {metrics['price_r2']:.3f}")
        print(f"Tax R² Score: {metrics['tax_r2']:.3f}")
        print(f"Average Price: £{metrics['avg_price']:.2f}")
        print(f"Average Tax: £{metrics['avg_tax']:.2f}")
        
        print("\n✅ Prediction model working successfully!")
        
    except Exception as e:
        print(f"❌ Error testing prediction model: {e}")
