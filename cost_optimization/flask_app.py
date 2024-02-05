from flask import Flask, request, jsonify
from sklearn.ensemble import GradientBoostingRegressor
import pandas as pd
import numpy as np
import pandas as pd

# Load the data
data_path = '/Users/aimaldastagirzada/Downloads/supply_chain_synthetic.csv'
synthetic_data = pd.read_csv(data_path)

app = Flask(__name__)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Assuming 'synthetic_data' is your DataFrame
# Correctly identifying numerical and categorical columns while excluding target variables
numerical_cols = synthetic_data.select_dtypes(include=['int64', 'float64']).drop(['Lead times', 'Costs'], axis=1).columns
categorical_cols = synthetic_data.select_dtypes(include=['object']).columns

# Preprocessing for numerical data: simple imputation and standard scaling
numerical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

# Preprocessing for categorical data: simple imputation and one hot encoding
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Defining features and targets
Y = synthetic_data[['Lead times', 'Costs']]
X = synthetic_data.drop(['Lead times', 'Costs'], axis=1)

# Splitting the dataset into training and testing sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Setting up the ColumnTransformer with the updated column references
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_cols),
        ('cat', categorical_transformer, categorical_cols)
    ])

# Applying the preprocessing to the X data
X_train_prepared = preprocessor.fit_transform(X_train)
X_test_prepared = preprocessor.transform(X_test)

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error

# For simplicity, let's focus on optimizing 'Lead time' first
Y_train_lead_time = Y_train['Lead times']
Y_test_lead_time = Y_test['Lead times']

# Initializing and training the Gradient Boosting Regressor
gb_reg = GradientBoostingRegressor(random_state=42)
gb_reg.fit(X_train_prepared, Y_train_lead_time)

# Predicting on the test set
Y_pred_lead_time = gb_reg.predict(X_test_prepared)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    # Assuming data is received as a dictionary matching the model's features, except targets
    
    # Convert input data to DataFrame to match the input expectation of the preprocessor
    input_df = pd.DataFrame([data])
    
    # Preprocess the input
    processed_input = preprocessor.transform(input_df)
    
    # Predict
    predictions = gb_reg.predict(processed_input)
    
    # Assuming we're predicting both lead times and costs, adjust as necessary
    lead_time_prediction, cost_prediction = predictions[0], predictions[1]
    
    # Return the predictions as a JSON response
    return jsonify({'lead_time': lead_time_prediction, 'cost': cost_prediction})

if __name__ == '__main__':
    app.run(debug=True)
