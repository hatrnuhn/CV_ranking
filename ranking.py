import pytesseract
import requests
import os
import pdf2image
import concurrent.futures
import numpy as np
from numpy.linalg import norm

class CVRanking:
    def __init__(self):
        self.model_id = "sentence-transformers/LaBSE"
        self.hf_token = os.getenv('HUGGING_FACE_API_KEY')

        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_id}"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}

    def generate_embeddings(self, texts):
        response = requests.post(self.api_url, headers=self.headers, json={"inputs": texts, "options":{"wait_for_model":True}})
        return response.json()
    
    def ocr_page(self, page):
        return pytesseract.image_to_string(page)

    def extract_cv(self, file_content):
        pdf_pages = pdf2image.convert_from_bytes(file_content, dpi=350)

                    # Use concurrent futures for parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
                        # Process pages in parallel and get OCR text for each page
            results = executor.map(self.ocr_page, pdf_pages)

            extracted_text = "\n".join(results)
            
        return extracted_text

    def calculate_cosine_similarity(self, applicant_resume, expected_competency):
        cosine = np.dot(applicant_resume,expected_competency)/(norm(applicant_resume)*norm(expected_competency))
        return cosine

    def rank_candidates(self, expected_competency, candidates):
        scores = {}

        # Generate embedding for the expected competency text
        expected_competency_embedding = self.generate_embeddings(expected_competency)

        try:
            # Loop through the provided candidates, generate embeddings, and calculate cosine similarity
            for candidate_name, candidate_desc in candidates:
                # Generate embedding for the candidate's resume text
                candidate_desc_embedding = self.generate_embeddings(candidate_desc)

                # Calculate cosine similarity between candidate's resume and expected competency
                score = self.calculate_cosine_similarity(candidate_desc_embedding, expected_competency_embedding)
                print(f'Cosine similarity score for applicant named {candidate_name} is {score}')
                scores[candidate_name] = score
        except Exception as e:
            print(f'Could not calculate cosine similarity: {e}')

        # Sort candidates by score (descending) to rank them
        sorted_candidates = sorted(scores.items(), key=lambda item: item[1], reverse=True)

        # Create a ranked dictionary (rank starts from 1)
        ranked_candidates = {rank + 1: {'candidate': candidate, 'score': score} for rank, (candidate, score) in enumerate(sorted_candidates)}

        return ranked_candidates