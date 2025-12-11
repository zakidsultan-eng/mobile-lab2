from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

stock_df = pd.read_csv('AAPL.csv', parse_dates=['Date'])
stock_df.columns = stock_df.columns.str.strip()
stock_df.sort_values('Date', inplace=True)

AK = "zahidwashere"


@app.route('/getData', methods=['GET'])
def get_all_data():
    return stock_df.to_json(orient='records', date_format='iso')

@app.route('/getData/<path:date>', methods=['GET'])
def get_data_by_date(date):
    result = stock_df[stock_df['Date'] == pd.to_datetime(date)]
    if result.empty:
        return jsonify({'error': 'No data found'}), 404
    return result.to_json(orient='records', date_format='iso')

@app.route('/calculate10DayAverage', methods=['GET'])
def calculate_10_day_avg():
    
    last_10 = stock_df.tail(10)
    
    averages = last_10[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].mean().to_dict()
    
    return jsonify(averages)


@app.route('/getData', methods=['POST'])
def get_data_range():
    body = request.get_json()
    start = pd.to_datetime(body.get('startDate'))
    end = pd.to_datetime(body.get('endDate'))
    mask = (stock_df['Date'] >= start) & (stock_df['Date'] <= end)
    return stock_df[mask].to_json(orient='records', date_format='iso')

@app.route('/addData', methods=['POST'])
def add_data():
    global stock_df
    new_row = request.get_json()
    new_row['Date'] = pd.to_datetime(new_row['Date'])
    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
        if col in new_row:
            new_row[col] = float(new_row[col])
    stock_df = pd.concat([stock_df, pd.DataFrame([new_row])], ignore_index=True)
    stock_df.sort_values('Date', inplace=True)
    return jsonify({'message': 'Data added successfully'}), 201


@app.route('/updateData', methods=['PUT'])
def update_data():
    global stock_df
    body = request.get_json()
    date = pd.to_datetime(body.get('Date'))
    idx = stock_df.index[stock_df['Date'] == date]
    if idx.empty:
        return jsonify({'error': 'Date not found'}), 404
    for key, val in body.items():
        if key in stock_df.columns:
            stock_df.loc[idx, key] = val
    return jsonify({'message': 'Data updated successfully'})


@app.route('/deleteDate/<path:date>', methods=['DELETE'])
def delete_date(date):
    global stock_df
    target = pd.to_datetime(date)
    stock_df = stock_df[stock_df['Date'] != target]
    return jsonify({'message': f'Data for {date} deleted'})

@app.route('/deleteAll', methods=['DELETE'])
def delete_all():
    global stock_df
    api_key = request.headers.get('X-API-Key')
    if api_key != AK:
        return jsonify({'error': 'Unauthorized'}), 401
    stock_df = stock_df.iloc[0:0]
    return jsonify({'message': 'All data deleted'})

if __name__ == '__main__':
    app.run(debug=True)
