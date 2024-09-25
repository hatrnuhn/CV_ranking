from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import os
from ranking import CVRanking

app =  Flask(__name__)
cors = CORS(app, resources={r'/*': {'origins': '*'}})

processor = CVRanking()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process-uploaded_cv', methods=['POST'])
def process_uploaded_cv():
    if 'file' not in request.files:
        return jsonify({'botResponse': 'Tolong upload file PDF'}), 400

    file = request.files['file']
    
    # Store file in a user-specific directory
    user_cv_pdf = "user_cv_pdf"
    os.makedirs(user_cv_pdf, exist_ok=True)

    user_cv_pdf_path = os.path.join(user_cv_pdf, file.filename)
    file.save(user_cv_pdf_path)

    processor.extract_cv(user_cv_pdf_path, file.filename)

    return jsonify({'response' : 'Your CV sucessfully uploaded'})

@app.route('/rank-applicants', methods=['POST'])
def rank_applicants():
    job_description = request.form['job_description']

    try:
        candidate_ranking = processor.rank_candicate(job_description)
        print(candidate_ranking)
    except:
        return jsonify({'error':'error in ranking the candidates'})

    return jsonify({'response':candidate_ranking})

if __name__ == "__main__":
    app.run(debug=True, port=5000)