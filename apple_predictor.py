import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, MACD
from ta.volatility import AverageTrueRange
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)  

start_date = '2013-01-01'
train_end_date = '2023-01-01'
end_date = '2024-08-01'  
df = None  

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

print("Computing technical indicators...")
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


for i in range(1, 6):  
    df[f'Close_Lag{i}'] = df['Close'].shift(i)

df_clean = df.dropna()
print(f"After computing indicators and dropping NaN values: {len(df_clean)} days of data")

features = ['SMA_5', 'SMA_20', 'RSI', 'MACD', 'MACD_Signal', 'ATR',
            'Year', 'Month', 'Day', 'DayOfWeek'] + [f'Close_Lag{i}' for i in range(1, 6)]
target = 'Close'

X = df_clean[features]
y = df_clean[target]

X_train = X[X.index <= train_end_date]
y_train = y[y.index <= train_end_date]

print(f"Training model on {len(X_train)} days of data from {start_date} to {train_end_date}")
model = RandomForestRegressor(n_estimators=1000, random_state=42, n_jobs=-1,
                            max_depth=25, min_samples_split=5, min_samples_leaf=2)
model.fit(X_train, y_train)
print("Model training complete")

def predict_and_get_actual(query_date_str):
    try:
        query_date = pd.to_datetime(query_date_str)

        if query_date < pd.to_datetime(start_date) or query_date > pd.to_datetime(end_date):
            return f"Please enter a date between {start_date} and {end_date}."

        if query_date not in df.index:
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
        actual_price = float(df.loc[query_date, 'Close'])  # Convert to float

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

X_test = X[X.index > train_end_date]
y_test = y[y.index > train_end_date]

y_pred = model.predict(X_test)
y_true = y_test.values

from sklearn.metrics import accuracy_score

# Calculate RMSE
from sklearn.metrics import mean_squared_error
import numpy as np

mse = mean_squared_error(y_true, y_pred)
rmse = np.sqrt(mse)
print(f"RMSE on test set: {rmse:.2f}")  

@app.route('/predict', methods=['POST'])
def predict_api():
    try:
        data = request.get_json()
        query_date = data.get('date')
        if not query_date:
            return jsonify({"error": "No date provided"}), 400

        result = predict_and_get_actual(query_date)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\nStarting Flask API...")
    app.run(debug=True)




