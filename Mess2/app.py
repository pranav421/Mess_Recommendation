from flask import Flask, render_template, request
import pandas as pd
from surprise import Dataset, Reader, SVD

app = Flask(__name__)

# Load dataset
data = pd.read_csv('mess_data.csv')

# Convert mess names to unique IDs
data['mess_id'] = data['mess_name'].astype('category').cat.codes

# Initialize Surprise Dataset
reader = Reader(rating_scale=(1, 5))
dataset = Dataset.load_from_df(data[['user_id', 'mess_id', 'rating']], reader)

# Build full trainset
trainset = dataset.build_full_trainset()

# Initialize SVD algorithm
algo = SVD()

# Fit the algorithm on the trainset
algo.fit(trainset)

# Function to get recommendations using collaborative filtering with selected tags
def get_recommendations(filtered_data, selected_tags):
    recommendations = []
    for _, row in filtered_data.iterrows():
        # Check if mess has all selected tags
        if all(tag in row['tags'].split(';') for tag in selected_tags):
            # Predict rating only for messes with selected tags
            pred = algo.predict(row['user_id'], row['mess_id'])
            recommendations.append({
                'mess_name': row['mess_name'],
                'rating': round(pred.est, 2),
                'tags': row['tags'],
                'reviews': row['reviews'],
                'owner_name': row['owner_name'],
                'owner_number': row['owner_number']
            })
    return recommendations

# Route to render index.html template
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle filter and display recommendations
@app.route('/recommendations', methods=['POST'])
def recommendations():
    sort_by = request.form.get('sort_by')
    selected_tags = request.form.getlist('tags')

    # Filter data based on selected tags
    filtered_data = data.copy()

    # Get recommendations for filtered data
    recommendations = get_recommendations(filtered_data, selected_tags)

    # Sort recommendations based on rating if specified
    if sort_by == 'ascending':
        recommendations.sort(key=lambda x: x['rating'])
    elif sort_by == 'descending':
        recommendations.sort(key=lambda x: x['rating'], reverse=True)

    return render_template('recommendations.html', recommendations=recommendations)

# Route to display mess details
@app.route('/mess_details/<mess_name>')
def mess_details(mess_name):
    mess_details = data[data['mess_name'] == mess_name].iloc[0]
    return render_template('mess_details.html', mess_details=mess_details)

if __name__ == '__main__':
    app.run(debug=True)
