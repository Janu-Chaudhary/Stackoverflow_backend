from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # ✅ Enable Cross-Origin Resource Sharing

YEARLY_CSV = os.path.join('data', 'yearly_tag_counts.csv')
MONTHLY_CSV = os.path.join('data', 'monthly_tag_counts.csv')


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/yearly-tags')
def yearly_tags():
    df = pd.read_csv(YEARLY_CSV)
    if 'Tag' not in df.columns or 'Year' not in df.columns or 'Count' not in df.columns:
        return jsonify({'error': 'Invalid column names in yearly CSV'}), 500

    results = []
    for tag, group in df.groupby('Tag'):
        results.append({
            'tag': tag,
            'data': group.sort_values('Year')[['Year', 'Count']].rename(
                columns={'Year': 'year', 'Count': 'count'}).to_dict(orient='records')
        })
    return jsonify(results)


@app.route('/api/monthly-tags')
def monthly_tags():
    lang = request.args.get('lang')
    year = request.args.get('year', type=int)

    if not lang or not year:
        return jsonify({'error': 'Missing lang or year'}), 400

    df = pd.read_csv(MONTHLY_CSV)
    if 'Tag' not in df.columns or 'Year' not in df.columns or 'Month' not in df.columns or 'Count' not in df.columns:
        return jsonify({'error': 'Invalid column names in monthly CSV'}), 500

    filtered = df[(df['Tag'] == lang) & (df['Year'] == year)]

    # Convert numeric month to name
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_map = {i + 1: month for i, month in enumerate(months_order)}
    filtered['Month'] = filtered['Month'].map(month_map)

    filtered['Month'] = pd.Categorical(filtered['Month'], categories=months_order, ordered=True)
    filtered = filtered.sort_values('Month')

    return jsonify({
        'tag': lang,
        'year': year,
        'data': filtered[['Month', 'Count']].rename(columns={'Month': 'month', 'Count': 'count'}).to_dict(orient='records')
    })


@app.route('/api/meta')
def meta_info():
    df = pd.read_csv(MONTHLY_CSV)
    tags = sorted(df['Tag'].unique())
    years = sorted(df['Year'].unique())
    return jsonify({
        'tags': [str(t) for t in tags],
        'years': [int(y) for y in years]
    })


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # ✅ Explicitly use port 5000
