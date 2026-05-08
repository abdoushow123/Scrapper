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

st.set_page_config(page_title="📚 Books Scraping Dashboard", layout="wide", page_icon="📖")

# Enhanced Custom CSS for better styling
st.markdown("""
<style>
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Subheader styling */
    h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 0.5rem;
        padding: 0.5rem;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 0.5rem;
        overflow: hidden;
    }
    
    /* Footer styling */
    footer {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-top: 2rem;
    }
    
    /* Warning and info styling */
    .stWarning, .stInfo {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    /* Success styling */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    /* Error styling */
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-radius: 0.5rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Sidebar
st.sidebar.title("📚 Books Scraping Dashboard")
st.sidebar.markdown("### 🎨 Your Personal Book Analytics")
st.sidebar.markdown("---")

# Add sidebar image/logo placeholder
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem;'>
    <div style='font-size: 3rem; margin-bottom: 0.5rem;'>📖</div>
    <div style='color: #666; font-style: italic;'>Discover • Analyze • Predict</div>
</div>
""", unsafe_allow_html=True)
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

# Enhanced Filters Section
st.sidebar.markdown("### 🔍 **Data Filters**")
st.sidebar.markdown("*Customize your data view*")

if not filter_df.empty and 'category' in filter_df.columns:
    categories = ["All"] + sorted(filter_df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("📚 **Category Selection**", categories, key="category_filter")
else:
    selected_category = st.sidebar.selectbox("📚 **Category Selection**", ["All"], key="category_filter_default")

if not filter_df.empty and 'price_excl_tax' in filter_df.columns:
    min_price = float(filter_df['price_excl_tax'].min())
    max_price = float(filter_df['price_excl_tax'].max())
    price_range = st.sidebar.slider("💰 **Price Range** (£)", min_price, max_price, (min_price, max_price), key="price_filter")
else:
    price_range = st.sidebar.slider("💰 **Price Range** (£)", 0, 100, (0, 100), key="price_filter_default")

in_stock_only = st.sidebar.checkbox("📦 **In Stock Only**", key="stock_filter")

# Enhanced Actions Section
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ **Quick Actions**")
st.sidebar.markdown("*Manage your data pipeline*")

if st.sidebar.button("🔄 **Launch Scraping**", type="primary"):
    with st.spinner("🌐 Scraping data... This may take a few minutes..."):
        try:
            scraper = BookScraper()
            scraper.scrape_all_books()
            st.success("✅ Scraping completed successfully!")
            st.cache_data.clear()  # Clear cache to refresh data
        except Exception as e:
            st.error(f"❌ Scraping failed: {e}")

if st.sidebar.button("🧹 **Clean Data**"):
    with st.spinner("🧹 Cleaning data..."):
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

if st.sidebar.button("📊 **Refresh Dashboard**"):
    st.cache_data.clear()
    st.rerun()

# Enhanced Main Content Header
st.markdown('<h1 class="main-header">📊 Books Analysis Dashboard</h1>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <p style='color: #666; font-style: italic;'>Your comprehensive book data analytics platform</p>
</div>
""", unsafe_allow_html=True)

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
    # Enhanced Key Metrics Section
    st.markdown("### 📈 **Key Metrics**")
    st.markdown("*Overview of your book collection*")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 **Total Books**", len(filtered_df), help="Total number of books in your dataset")
    
    with col2:
        if 'price_excl_tax' in filtered_df.columns:
            avg_price = filtered_df['price_excl_tax'].mean()
            st.metric("💰 **Avg Price**", f"£{avg_price:.2f}", help="Average price across all books")
        else:
            st.metric("💰 **Avg Price**", "N/A")
    
    with col3:
        if 'in_stock' in filtered_df.columns:
            in_stock = filtered_df['in_stock'].sum()
            stock_percentage = (in_stock / len(filtered_df)) * 100
            st.metric("📦 **In Stock**", f"{in_stock} ({stock_percentage:.1f}%)", help="Number of books currently in stock")
        else:
            st.metric("📦 **In Stock**", "N/A")
    
    with col4:
        if 'category' in filtered_df.columns:
            num_categories = filtered_df['category'].nunique()
            st.metric("🏷️ **Categories**", num_categories, help="Number of unique book categories")
        else:
            st.metric("🏷️ **Categories**", "N/A")
    
    # Enhanced Visualizations Section
    st.markdown("---")
    st.markdown("### 📊 **Visualizations**")
    st.markdown("*Interactive charts and graphs*")
    
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
    
    # Enhanced Top/Bottom Analysis Section
    st.markdown("---")
    st.markdown("### 🏆 **Top/Bottom Analysis**")
    st.markdown("*Discover highest and lowest performing books*")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        metric_options = ['price_excl_tax', 'price_incl_tax', 'number_of_reviews', 'stock_count']
        available_metrics = [m for m in metric_options if m in filtered_df.columns]
        if available_metrics:
            selected_metric = st.selectbox("📊 **Analyze by Metric**", available_metrics, 
                                          format_func=lambda x: x.replace('_', ' ').title(),
                                          help="Select a metric to analyze top and bottom performers")
        else:
            selected_metric = None
    
    if selected_metric:
        try:
            fig5 = analyzer.create_top_bottom_chart(selected_metric)
            st.plotly_chart(fig5, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating top/bottom chart: {e}")
    
    # Enhanced Predictions Section
    st.markdown("---")
    st.markdown("### 🔮 **Price Predictions**")
    st.markdown("*AI-powered forecasting for next week*")
    
    try:
        predictor = PricePredictor()
        predictor.train_model()
        predictions = predictor.predict_next_week()
        
        if 'error' not in predictions:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📈 **Predicted Avg Price**", f"£{predictions['predicted_avg_price_next_week']:.2f}", help="Predicted average price for next week")
            
            with col2:
                st.metric("📋 **Predicted Avg Tax**", f"£{predictions['predicted_avg_tax_next_week']:.2f}", help="Predicted average tax for next week")
            
            with col3:
                trend_icon = "📈" if predictions['price_trend'] == 'increasing' else "📉"
                st.metric(f"{trend_icon} **Price Trend**", predictions['price_trend'].title(), help="Predicted price movement direction")
            
            # Model evaluation
            evaluation = predictor.evaluate_model()
            if 'error' not in evaluation:
                with st.expander("📊 **Model Performance Metrics**"):
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
    
    # Enhanced Data Table Section
    st.markdown("---")
    with st.expander("📋 **View Data Table**"):
        st.dataframe(filtered_df, use_container_width=True)
    
    # Enhanced Category Statistics Section
    with st.expander("📊 **Category Statistics**"):
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
    
    # Enhanced Instructions Section
    st.markdown("---")
    st.markdown("### 🚀 **Getting Started**")
    st.markdown("*Quick guide to get your dashboard up and running*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Step 1: Launch Scraping**
        - Click the **"🔄 Launch Scraping"** button
        - Wait for data collection to complete
        - This may take a few minutes
        
        **Step 2: Clean Data**
        - Click the **"🧹 Clean Data"** button
        - Process the scraped data
        - Prepare for analysis
        """)
    
    with col2:
        st.markdown("""
        **Step 3: Refresh Dashboard**
        - Click **"📊 Refresh Dashboard"** button
        - View your processed data
        - Start exploring analytics
        
        **Step 4: Explore Features**
        - Use filters to customize your view
        - Analyze visualizations
        - Try predictions
        """)
    
    st.markdown("---")
    st.markdown("### 📋 **Dashboard Features**")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        **🌐 Data Scraping**
        - Real-time data collection
        - Comprehensive book information
        - Automated data extraction
        """)
    
    with feature_col2:
        st.markdown("""
        **📊 Interactive Analytics**
        - Dynamic filtering options
        - Multiple chart types
        - Category analysis
        """)
    
    with feature_col3:
        st.markdown("""
        **🔮 Predictive Intelligence**
        - Machine learning predictions
        - Price trend forecasting
        - Performance metrics
        """)

# Enhanced Footer Section
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; margin-top: 2rem;'>
    <h3 style='color: white; margin-bottom: 0.5rem;'>📚 Books Scraping Dashboard</h3>
    <p style='color: rgba(255,255,255,0.9); margin-bottom: 0.5rem;'>Built with ❤️ using Streamlit, Plotly & Scikit-learn</p>
    <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem;'>Data sourced from <a href='http://books.toscrape.com' style='color: white; text-decoration: underline;'>books.toscrape.com</a></p>
    <p style='color: rgba(255,255,255,0.7); font-size: 0.8rem; margin-top: 1rem;'>© 2024 Books Analytics Platform</p>
</div>
""", unsafe_allow_html=True)
