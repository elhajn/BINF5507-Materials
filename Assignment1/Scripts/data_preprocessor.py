# import all necessary libraries here
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# 1. Impute Missing Values
def impute_missing_values(data, strategy='mean'):
    """
    Fill missing values in the dataset.
    :param data: pandas DataFrame
    :param strategy: str, imputation method ('mean', 'median', 'mode')
    :return: pandas DataFrame
    """
    # TODO: Fill missing values based on the specified strategy
    data = data.copy()
    
    # use if/elif to separate steps for each 'strategy' option
    if strategy == 'mean':
        
        # use for loop to iterate through each numerical column
        for col in data.select_dtypes(include = [np.number]).columns:
            # use if/else to skip 'target' column; don't want to impute this
            if col == 'target':
                continue
            # impute numerical columns using the mean value of the respective column
            else: 
                data.fillna({col: data[col].mean()}, inplace=True)
                
    elif strategy == 'median':
        # same set-up as 'mean,' but using the median of each numerical column
        for col in data.select_dtypes(include = [np.number]).columns:
            if col == 'target':
                continue
            else: 
                data.fillna({col: data[col].median()}, inplace=True)
                
    elif strategy == 'mode':
        # iterate through numerical columns, skipping target, and using the mode to impute
        for col in data.select_dtypes(include = [np.number]).columns:
            if col == 'target':
                continue
            else: 
                data.fillna({col: data[col].mode()}, inplace=True)
        # iterate through categorical columns, using mode to impute
        for col in data.select_dtypes(include = [np.object_]).columns:
            data.fillna({col: data[col].mode()[0]}, inplace=True)
    
    # because all of the operations above were done directly to data, simply return the updated data
    return data

# 2. Remove Duplicates
def remove_duplicates(data):
    """
    Remove duplicate rows from the dataset.
    :param data: pandas DataFrame
    :return: pandas DataFrame
    """
    # TODO: Remove duplicate rows
    data = data.copy()
    # apply the drop_duplicates function to the data and return the updated df no_dups
    no_dups = data.drop_duplicates()
    return no_dups

# 3. Normalize Numerical Data
def normalize_data(data,method='minmax'):
    """Apply normalization to numerical features.
    :param data: pandas DataFrame
    :param method: str, normalization method ('minmax' (default) or 'standard')
    """
    # TODO: Normalize numerical data using Min-Max or Standard scaling
    data = data.copy()
    
    # use if/elif to separate steps for each 'method' option
    if method == 'minmax':
        
        # define scaling method
        scaler = MinMaxScaler()
        
        # apply scaling to data; returns an array
        scaled = scaler.fit_transform(data.select_dtypes(include = [np.number]))
        
        # convert scaled columns to df, reassign column names from original data
        scaled_df = pd.DataFrame(scaled, columns=data.select_dtypes(include = [np.number]).columns)
        
        # replace numerical columns in original df with corresponding columns in scaled df
        for col in data.select_dtypes(include = [np.number]):
            data[col] = scaled_df[col]
    
    # does the same as above but with Standard scaling (instead of Min-Max)
    elif method == 'standard':
        scaler = StandardScaler()
        scaled = scaler.fit_transform(data.select_dtypes(include = [np.number]))
        scaled_df = pd.DataFrame(scaled, columns=data.select_dtypes(include = [np.number]).columns)
        for col in data.select_dtypes(include = [np.number]):
            data[col] = scaled_df[col]
    return data
    # pass

# 4. Remove Redundant Features   
def remove_redundant_features(data, threshold=0.9):
    """Remove redundant or duplicate columns.
    :param data: pandas DataFrame
    :param threshold: float, correlation threshold
    :return: pandas DataFrame
    """
    # TODO: Remove redundant features based on the correlation threshold (HINT: you can use the corr() method)
    data = data.copy()
    
    # create a correlation matrix: apply corr function to numerical columns from data and create matrix with the absolute values
    corr_matrix = data.select_dtypes(include = [np.number]).corr().abs()
    
    # isolate the upper half of the matrix; ensures the middle diagonal & repeats are ignored
    upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k = 1).astype(bool))
    
    # create a list of column names that have a correlation greater than the threshold; these will be dropped
    cols_to_drop = [col for col in upper_tri.columns if any(upper_tri[col] > threshold)]
    
    # drop columns with a correlation greater than threshold
    data.drop(columns = cols_to_drop, axis = 1, inplace = True)
    return data

# ---------------------------------------------------

def simple_model(input_data, split_data=True, scale_data=False, print_report=False):
    """
    A simple logistic regression model for target classification.
    Parameters:
    input_data (pd.DataFrame): The input data containing features and the target variable 'target' (assume 'target' is the first column).
    split_data (bool): Whether to split the data into training and testing sets. Default is True.
    scale_data (bool): Whether to scale the features using StandardScaler. Default is False.
    print_report (bool): Whether to print the classification report. Default is False.
    Returns:
    None
    The function performs the following steps:
    1. Removes columns with missing data.
    2. Splits the input data into features and target.
    3. Encodes categorical features using one-hot encoding.
    4. Splits the data into training and testing sets (if split_data is True).
    5. Scales the features using StandardScaler (if scale_data is True).
    6. Instantiates and fits a logistic regression model.
    7. Makes predictions on the test set.
    8. Evaluates the model using accuracy score and classification report.
    9. Prints the accuracy and classification report (if print_report is True).
    """

    # if there's any missing data, remove the columns
    input_data.dropna(inplace=True)

    # split the data into features and target
    target = input_data.copy()[input_data.columns[0]]
    features = input_data.copy()[input_data.columns[1:]]

    # if the column is not numeric, encode it (one-hot)
    for col in features.columns:
        if features[col].dtype == 'object':
            features = pd.concat([features, pd.get_dummies(features[col], prefix=col)], axis=1)
            features.drop(col, axis=1, inplace=True)

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, stratify=target, random_state=42)

    if scale_data:
        # scale the data
        X_train = normalize_data(X_train)
        X_test = normalize_data(X_test)
        
    # instantiate and fit the model
    log_reg = LogisticRegression(random_state=42, max_iter=100, solver='liblinear', penalty='l2', C=1.0)
    log_reg.fit(X_train, y_train)

    # make predictions and evaluate the model
    y_pred = log_reg.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print(f'Accuracy: {accuracy}')
    
    # if specified, print the classification report
    if print_report:
        print('Classification Report:')
        print(report)
        print('Read more about the classification report: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html and https://www.nb-data.com/p/breaking-down-the-classification')
    
    return None