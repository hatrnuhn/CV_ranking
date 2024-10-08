from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import os
from ranking import CVRanking
from dotenv import load_dotenv

load_dotenv()

app =  Flask(__name__)
cors = CORS(app, resources={r'/*': {'origins': '*'}})

processor = CVRanking()

@app.route('/cvs', methods=['POST'])
def process_uploaded_cv():
    print(request)
    if 'file' not in request.files:
        return jsonify('cvs401'), 400

    file = request.files['file']
    
    # Ensure the uploaded file is a PDF
    if not file.filename.endswith('.pdf'):
        return jsonify('cvs402'), 400

    # Read the file content directly into memory
    file_content = file.read()

    extracted_text = processor.extract_cv(file_content)

    return jsonify(extracted_text)

@app.route('/applicants/rank', methods=['POST'])
def rank_applicants():
    data = request.get_json()
    job_description = data.get('job_description')
    candidates = data.get('candidates')

    if not job_description or not candidates:
        return jsonify({'error': 'Job description and candidates are required'}), 400

    try:
        # Rank candidates using the provided job description and candidates array
        candidate_ranking = processor.rank_candidates(job_description, candidates)
    except Exception as e:
        return jsonify({'error': f'Could not rank candidates: {str(e)}'}), 500

    return jsonify(candidate_ranking), 200


if __name__ == "__main__":
    if os.getenv('FLASK_ENV') == 'development':
        app.run(debug=True, port=os.getenv('PORT'))
    else :
        from waitress import serve
        import logging
        logging.basicConfig(level=logging.INFO)
        serve(app, host="0.0.0.0", port=os.getenv('PORT'))