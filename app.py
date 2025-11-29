from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json

app = Flask(__name__)
# CORS(app)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})


@app.route('/')
def index():
    return "Flask is working"

@app.route('/search', methods=['POST'])
def search():
    search_type = request.form.get('search-type')
    search_input = request.form.get('search-input')

    df = pd.read_csv('judgment_data.csv', encoding='utf-8')

    if search_type == 'name':
        results = df[df['Petitioner'].str.contains(search_input, case=False, na=False)]
    else:
        results = df[df['Case Number'].astype(str).str.contains(search_input, case=False, na=False)]

    results['PDF Link'] = results['PDF Link'].apply(
        lambda url: f'<a href="{url}" target="_blank">View PDF</a>' if pd.notna(url) else ''
    )

    if 'HTML Link' in results.columns:
        results['HTML Link'] = results['HTML Link'].apply(
            lambda url: f'<a href="{url}" target="_blank">View HTML</a>' if pd.notna(url) else ''
        )

    results_list = results.to_dict(orient='records')

    return jsonify(results_list)


@app.route('/insights-data')
def insights_data():
    df = pd.read_csv('judgment_data.csv', encoding='utf-8')

    # Court-wise case count
    court_counts = df['Court'].value_counts().to_dict()

    # Year-wise judgment count
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    year_counts = df['Date'].dt.year.value_counts().sort_index().to_dict()

    return json.dumps({
        'court_counts': court_counts,
        'year_counts': year_counts
    }, ensure_ascii=False)

if __name__ == '__main__':
    app.run(debug=True)
