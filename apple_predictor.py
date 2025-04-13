import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, MACD
from ta.volatility import AverageTrueRange
from datetime import datetime, timedelta

# Step 1: Download Apple stock data - include data up to current date to allow predictions
start_date = '2013-01-01'
train_end_date = '2023-01-01'
end_date = '2025-03-31'  # Include data up to the most recent date needed for predictions

try:
    print("Downloading historical stock data...")
    df = yf.download('AAPL', start=start_date, end=end_date)
    
    if df.empty:
        raise ValueError("Failed to download data from Yahoo Finance")
    
    print(f"Successfully downloaded {len(df)} days of data")
except Exception as e:
    print(f"Error downloading data: {str(e)}")
    print("Try installing the latest version of yfinance with: pip install yfinance --upgrade")
    import sys
    sys.exit(1)

# Step 2: Feature Engineering with Technical Indicators and Lagged Prices
print("Computing technical indicators...")
# Use .squeeze() to convert to 1D series for the TA library
df['SMA_5'] = SMAIndicator(close=df['Close'].squeeze(), window=5).sma_indicator()
df['SMA_20'] = SMAIndicator(close=df['Close'].squeeze(), window=20).sma_indicator()
df['RSI'] = RSIIndicator(close=df['Close'].squeeze(), window=14).rsi()
macd = MACD(close=df['Close'].squeeze())
df['MACD'] = macd.macd()
df['MACD_Signal'] = macd.macd_signal()
df['ATR'] = AverageTrueRange(high=df['High'].squeeze(), low=df['Low'].squeeze(), close=df['Close'].squeeze(), window=14).average_true_range()

df['Year'] = df.index.year
df['Month'] = df.index.month
df['Day'] = df.index.day
df['DayOfWeek'] = df.index.dayofweek

# Add lagged closing prices
for i in range(1, 6):  # Add lags of 1 to 5 days
    df[f'Close_Lag{i}'] = df['Close'].shift(i)

# Drop rows with NaN values that result from the lag features
df_clean = df.dropna()
print(f"After computing indicators and dropping NaN values: {len(df_clean)} days of data")

# Step 3: Select Features and Target
features = ['SMA_5', 'SMA_20', 'RSI', 'MACD', 'MACD_Signal', 'ATR', 
           'Year', 'Month', 'Day', 'DayOfWeek'] + [f'Close_Lag{i}' for i in range(1, 6)]
target = 'Close'

X = df_clean[features]
y = df_clean[target]

# Step 4: Train the model on data up to train_end_date
X_train = X[X.index <= train_end_date]
y_train = y[y.index <= train_end_date]

print(f"Training model on {len(X_train)} days of data from {start_date} to {train_end_date}")
model = RandomForestRegressor(n_estimators=1000, random_state=42, n_jobs=-1, 
                             max_depth=25, min_samples_split=5, min_samples_leaf=2)
model.fit(X_train, y_train)
print("Model training complete")

# Step 5: Function to Predict and Get Actual Price for a Given Date
def predict_and_get_actual(query_date_str):
    try:
        query_date = pd.to_datetime(query_date_str)
        
        # Check if date is within range
        if query_date < pd.to_datetime(start_date) or query_date > pd.to_datetime(end_date):
            return f"Please enter a date between {start_date} and {end_date}."
        
        # Check if the date exists in our DataFrame
        if query_date not in df.index:
            # Find the next trading day if this was a weekend or holiday
            days_to_check = 5  # Check up to 5 days forward
            found_date = None
            
            for i in range(1, days_to_check + 1):
                next_date = query_date + pd.Timedelta(days=i)
                if next_date in df.index:
                    found_date = next_date
                    break
            
            if found_date:
                return f"No data for {query_date_str} (likely a non-trading day). The next trading day was {found_date.strftime('%Y-%m-%d')}."
            else:
                return f"No data for {query_date_str} and couldn't find the next trading day within {days_to_check} days."
        
        # Get actual price directly from our dataframe
        actual_price = float(df.loc[query_date, 'Close'])  # Convert to float to avoid Series formatting issue
        
        # For prediction, we need a complete row with all features
        if query_date in df_clean.index:
            # Use the features from our cleaned DataFrame for prediction
            prediction_features = df_clean.loc[query_date, features].values.reshape(1, -1)
            predicted_price = float(model.predict(prediction_features)[0])  # Convert to float
            
            return f"Date: {query_date_str}\nPredicted Price: ${predicted_price:.2f}\nActual Price: ${actual_price:.2f}"
        else:
            return f"Date: {query_date_str}\nActual Price: ${actual_price:.2f}\nPrediction not available (missing indicators or lag values)"
            
    except KeyError:
        return f"Data for {query_date_str} not found in the dataset."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Step 6: Example Usage
print("\nTesting the prediction function:")

# Test with a weekend date
query_date_weekend = '2023-05-20'  # A Saturday
result_weekend = predict_and_get_actual(query_date_weekend)
print(f"\nWeekend test: {result_weekend}")

# Test with a weekday during training period
query_date_train = '2015-07-20'
result_train = predict_and_get_actual(query_date_train)
print(f"\nTraining period test: {result_train}")

# Test with a recent date
query_date_recent = '2023-05-15'  # A weekday
result_recent = predict_and_get_actual(query_date_recent)
print(f"\nRecent date test: {result_recent}")

# For interactive use
def interactive_prediction():
    while True:
        user_date = input("\nEnter a date (YYYY-MM-DD) between 2013-01-01 and 2024-05-31 (or 'quit' to exit): ")
        if user_date.lower() == 'quit':
            break
        result = predict_and_get_actual(user_date)
        print(result)

print("\nEntering interactive mode. You can test any date:")
interactive_prediction()