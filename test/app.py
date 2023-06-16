from flask import Flask, render_template, request
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

app = Flask(__name__)

# Load the pre-trained ARIMA model
with open('ARIMA_AH.pkl', 'rb') as f:
    model_fit = pickle.load(f)


@app.route('/')
def home():
    return 'Welcome to the TomatoCare web application.'

# Define the route for the forecasting page
@app.route('/forecasting', methods=['GET', 'POST'])
def forecasting():
    if request.method == 'POST':
        # Retrieve user input from the form
        num_years = int(request.form['num_years'])

        # Step 1: Load the data
        data = pd.read_csv('AreaHarvested.csv')

        # Convert 'Year' column to string type
        data['Year'] = data['Year'].astype(str)
        data['YearQuarter'] = data['Year'] + '-' + data['TimePeriod']

        data['AreaHarvested_log'] = np.log(data['AreaHarvested'])
        train_data = data['AreaHarvested_log'].iloc[:int(len(data) * 0.7)]
        train_data_diff = train_data.diff().dropna()

        # Step 3: Fit the ARIMA model
        model = ARIMA(train_data, order=(4, 1, 0))
        model_fit = model.fit()

        # Step 4: Make time series predictions
        test_data = data['AreaHarvested_log'].iloc[int(len(data) * 0.7):]
        forecast = model_fit.forecast(steps=len(test_data))

        # Step 2: Fit the ARIMA model
        model = ARIMA(data['AreaHarvested_log'], order=(4, 1, 0))
        model_fit = model.fit()

        combined_data = pd.concat([data[['YearQuarter', 'AreaHarvested_log']], pd.Series(forecast)], axis=1)
        combined_data.columns = ['Year', 'Actual', 'Forecast']

        # Fit the ARIMA model using the actual series
        train_data = data['AreaHarvested'].iloc[:int(len(data) * 0.7)]
        model = ARIMA(train_data, order=(4, 1, 0))
        model_fit = model.fit()

        # Step 3: Make time series predictions
        last_year = int(data['Year'].iloc[-1])
        last_year = last_year + 1
        future_years = pd.date_range(start=f'{last_year}-01-01', periods=num_years * 4, freq='Q')
        forecast = pd.Series(model_fit.forecast(steps=num_years * 4).values)

        # Step 4: Create a DataFrame with the predicted data
        prediction_df = pd.DataFrame({
            'Year': future_years.year,
            'TimePeriod': future_years.quarter,
            'Actual': data['AreaHarvested'].values[-num_years * 4:],
            'Forecast': forecast
        })

        # Render the forecasting_results.html template with the predicted data
        return render_template('forecasting_results.html', prediction_df=prediction_df.to_dict(orient='records'))

     # Render the forecasting.html template for user input
    return render_template('forecasting.html')

if __name__ == '__main__':
    app.run()
