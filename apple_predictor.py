import yfinance as yf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Step 1: Get data
data = yf.download('AAPL', start='2015-01-01', end='2024-12-31')
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
data.dropna(inplace=True)

# Step 2: Add features
data['Prev_Close'] = data['Close'].shift(1)
data['7_MA'] = data['Close'].rolling(window=7).mean()
data['30_MA'] = data['Close'].rolling(window=30).mean()
data.dropna(inplace=True)

# Step 3: Define X and y
X = data[['Open', 'High', 'Low', 'Volume', 'Prev_Close', '7_MA', '30_MA']]
y = data['Close']

# Step 4: Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Step 5: Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 6: Predict
predictions = model.predict(X_test)

# Step 7: Evaluate
rmse = mean_squared_error(y_test, predictions) ** 0.5  # Manually take sqrt for RMSE
print(f"RMSE: {rmse:.2f}")

# Step 8: Plot results
plt.figure(figsize=(10, 5))
plt.plot(y_test.values, label="Actual")
plt.plot(predictions, label="Predicted")
plt.legend()
plt.title("Apple Stock Price Prediction")
plt.show()
