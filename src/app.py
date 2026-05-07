"""
Streamlit Dashboard for Books Scraping Project
Complete web interface with filters, visualizations, and predictions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from typing import Dict, Any

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from analysis import DataAnalyzer
    from model import PricePredictor
    from scraper import BookScraper
    from cleaning import DataCleaner
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all modules are in the src directory.")
    st.stop()

st.set_page_config(page_title="📚 Books Scraping Dashboard", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📚 Books Scraping Dashboard")
st.sidebar.markdown("---")

# Load data for filters
@st.cache_data
def load_data_for_filters():
    try:
        # Get the latest cleaned file
        files = [f for f in os.listdir("data/cleaned") if f.endswith('.csv')]
        if files:
            latest_file = os.path.join("data/cleaned", max(files, key=lambda f: os.path.getctime(os.path.join("data/cleaned", f))))
            return pd.read_csv(latest_file)
    except:
        pass
    return pd.DataFrame()

filter_df = load_data_for_filters()

# Filters
st.sidebar.subheader("🔍 Filters")
if not filter_df.empty and 'category' in filter_df.columns:
    categories = ["All"] + sorted(filter_df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories, key="category_filter")
else:
    selected_category = st.sidebar.selectbox("Category", ["All"], key="category_filter_default")

if not filter_df.empty and 'price_excl_tax' in filter_df.columns:
    min_price = float(filter_df['price_excl_tax'].min())
    max_price = float(filter_df['price_excl_tax'].max())
    price_range = st.sidebar.slider("Price Range (£)", min_price, max_price, (min_price, max_price), key="price_filter")
else:
    price_range = st.sidebar.slider("Price Range (£)", 0, 100, (0, 100), key="price_filter_default")

in_stock_only = st.sidebar.checkbox("In Stock Only", key="stock_filter")

# Actions
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Actions")

if st.sidebar.button("🔄 Launch Scraping", type="primary"):
    with st.spinner("Scraping data... This may take a few minutes..."):
        try:
            scraper = BookScraper()
            scraper.scrape_all_categories()
            st.success("✅ Scraping completed successfully!")
            st.cache_data.clear()  # Clear cache to refresh data
        except Exception as e:
            st.error(f"❌ Scraping failed: {e}")

if st.sidebar.button("🧹 Clean Data"):
    with st.spinner("Cleaning data..."):
        try:
            cleaner = DataCleaner()
            # Clean single combined file
            raw_data = cleaner.load_raw_data()
            cleaned_data = cleaner.clean_all_data(raw_data)
            cleaner.save_cleaned_csv(cleaned_data, "cleaned_books.csv")
            st.success(f"✅ Data cleaning completed! Cleaned {len(cleaned_data)} records")
            st.cache_data.clear()
        except Exception as e:
            st.error(f"❌ Data cleaning failed: {e}")

if st.sidebar.button("📊 Refresh Dashboard"):
    st.cache_data.clear()
    st.rerun()

# Main content
st.markdown('<h1 class="main-header">📊 Books Analysis Dashboard</h1>', unsafe_allow_html=True)

# Load and filter data
@st.cache_data
def load_and_filter_data(category, price_min, price_max, stock_only):
    try:
        analyzer = DataAnalyzer()
        df = analyzer.load_data()
        
        # Apply filters
        if category != "All":
            df = df[df['category'] == category]
        
        if 'price_excl_tax' in df.columns:
            df = df[(df['price_excl_tax'] >= price_min) & (df['price_excl_tax'] <= price_max)]
        
        if stock_only and 'in_stock' in df.columns:
            df = df[df['in_stock'] == True]
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load filtered data using the variables from the filter section above
filtered_df = load_and_filter_data(selected_category, price_range[0], price_range[1], in_stock_only)

if not filtered_df.empty:
    # Key Metrics
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Books", len(filtered_df))
    
    with col2:
        if 'price_excl_tax' in filtered_df.columns:
            avg_price = filtered_df['price_excl_tax'].mean()
            st.metric("💰 Avg Price", f"£{avg_price:.2f}")
        else:
            st.metric("💰 Avg Price", "N/A")
    
    with col3:
        if 'in_stock' in filtered_df.columns:
            in_stock = filtered_df['in_stock'].sum()
            stock_percentage = (in_stock / len(filtered_df)) * 100
            st.metric("📦 In Stock", f"{in_stock} ({stock_percentage:.1f}%)")
        else:
            st.metric("📦 In Stock", "N/A")
    
    with col4:
        if 'category' in filtered_df.columns:
            num_categories = filtered_df['category'].nunique()
            st.metric("🏷️ Categories", num_categories)
        else:
            st.metric("🏷️ Categories", "N/A")
    
    # Visualizations
    st.subheader("📊 Visualizations")
    
    # Create analyzer instance for visualizations
    analyzer = DataAnalyzer()
    analyzer.df = filtered_df
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            fig1 = analyzer.create_price_distribution()
            st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating price distribution: {e}")
    
    with col2:
        try:
            fig2 = analyzer.create_category_chart()
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating category chart: {e}")
    
    # Stock availability chart
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            fig3 = analyzer.create_availability_chart()
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating availability chart: {e}")
    
    with col2:
        try:
            fig4 = analyzer.create_price_evolution()
            st.plotly_chart(fig4, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating price evolution: {e}")
    
    # Top/Bottom Analysis
    st.subheader("🏆 Top/Bottom Analysis")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        metric_options = ['price_excl_tax', 'price_incl_tax', 'number_of_reviews', 'stock_count']
        available_metrics = [m for m in metric_options if m in filtered_df.columns]
        if available_metrics:
            selected_metric = st.selectbox("Analyze by", available_metrics, 
                                          format_func=lambda x: x.replace('_', ' ').title())
        else:
            selected_metric = None
    
    if selected_metric:
        try:
            fig5 = analyzer.create_top_bottom_chart(selected_metric)
            st.plotly_chart(fig5, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating top/bottom chart: {e}")
    
    # Predictions
    st.subheader("🔮 Price Predictions")
    
    try:
        predictor = PricePredictor()
        predictor.train_model()
        predictions = predictor.predict_next_week()
        
        if 'error' not in predictions:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📈 Predicted Avg Price", f"£{predictions['predicted_avg_price_next_week']:.2f}")
            
            with col2:
                st.metric("📋 Predicted Avg Tax", f"£{predictions['predicted_avg_tax_next_week']:.2f}")
            
            with col3:
                trend_icon = "📈" if predictions['price_trend'] == 'increasing' else "📉"
                st.metric(f"{trend_icon} Price Trend", predictions['price_trend'].title())
            
            # Model evaluation
            evaluation = predictor.evaluate_model()
            if 'error' not in evaluation:
                with st.expander("📊 Model Performance Metrics"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Price Model:**")
                        st.write(f"MSE: {evaluation['price_mse']:.4f}")
                        st.write(f"R²: {evaluation['price_r2']:.4f}")
                    with col2:
                        st.write("**Tax Model:**")
                        st.write(f"MSE: {evaluation['tax_mse']:.4f}")
                        st.write(f"R²: {evaluation['tax_r2']:.4f}")
        else:
            st.error(f"Prediction failed: {predictions['error']}")
            
    except Exception as e:
        st.error(f"Error in prediction module: {e}")
    
    # Data Table
    with st.expander("📋 View Data Table"):
        st.dataframe(filtered_df, use_container_width=True)
    
    # Category Statistics (from single file)
    with st.expander("📊 Category Statistics"):
        try:
            analyzer = DataAnalyzer()
            
            if not analyzer.df.empty and 'category' in analyzer.df.columns:
                category_stats = analyzer.df.groupby('category').agg({
                    'count': ('title', 'count'),
                    'avg_price': ('price_excl_tax', 'mean'),
                    'in_stock': ('in_stock', 'sum'),
                    'avg_reviews': ('number_of_reviews', 'mean')
                }).round(2)
                
                # Convert to display format
                stats_df = category_stats.reset_index()
                stats_df.columns = ['Books Count', 'Avg Price', 'In Stock', 'Avg Reviews']
                stats_df['Avg Price'] = stats_df['Avg Price'].round(2)
                stats_df['Avg Reviews'] = stats_df['Avg Reviews'].round(1)
                st.dataframe(stats_df, use_container_width=True)
            else:
                st.info("No category statistics available")
        except Exception as e:
            st.error(f"Error loading category statistics: {e}")

else:
    st.warning("⚠️ No data available. Please run the scraper and cleaner first using the sidebar buttons.")
    
    # Instructions
    st.markdown("""
    ### 🚀 Getting Started:
    1. **Launch Scraping**: Click the "🔄 Launch Scraping" button to collect book data
    2. **Clean Data**: Click the "🧹 Clean Data" button to process the scraped data
    3. **Refresh Dashboard**: Click "📊 Refresh Dashboard" to see your data
    4. **Explore**: Use filters and visualizations to analyze the data
    
    ### 📋 Features:
    - **Real-time data scraping** from books.toscrape.com
    - **Interactive filters** for category, price range, and stock availability
    - **Multiple visualizations** including price distribution, categories, and trends
    - **Top/Bottom analysis** for various metrics
    - **Price prediction** using machine learning
    - **Statistical analysis** with median calculations
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📚 Books Scraping Dashboard | Built with Streamlit, Plotly & Scikit-learn</p>
    <p>Data sourced from <a href='http://books.toscrape.com'>books.toscrape.com</a></p>
</div>
""", unsafe_allow_html=True)
