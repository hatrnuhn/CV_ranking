import pytesseract
import requests
from dotenv import load_dotenv
import os
from pdf2image import convert_from_path
import concurrent.futures
import numpy as np
from numpy.linalg import norm

load_dotenv()

class CVRanking:
    def __init__(self):
        self.model_id = "sentence-transformers/LaBSE"
        self.hf_token = os.getenv('HUGGING_FACE_API_KEY')

        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_id}"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}

        self.user_txt_folder = 'cv_candicates_text'
        os.makedirs(self.user_txt_folder, exist_ok=True)

    def generate_embeddings(self, texts):
        response = requests.post(self.api_url, headers=self.headers, json={"inputs": texts, "options":{"wait_for_model":True}})
        return response.json()
    
    def ocr_page(self, page):
        return pytesseract.image_to_string(page)

    def extract_cv(self, document_path, filename):
        pdf_pages = convert_from_path(document_path, dpi=350)

        text_file_path = os.path.join(self.user_txt_folder, f'{filename}.txt')

                    # Use concurrent futures for parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
                        # Process pages in parallel and get OCR text for each page
            results = executor.map(self.ocr_page, pdf_pages)

                        # Write the extracted text to a file
            with open(text_file_path, 'a', encoding='utf-8') as f:
                for text in results:
                    f.write(text + "\n")


    def calculate_cosine_similarity(self, applicant_resume, expected_competency):
        cosine = np.dot(applicant_resume,expected_competency)/(norm(applicant_resume)*norm(expected_competency))
        return cosine

    def rank_candicate(self, expected_competency):
        scores = {}

        # Generate embedding for the expected competency text
        expected_competency_embedding = self.generate_embeddings(expected_competency)

        try:
            # Loop through all candidate CV files, generate embeddings, and calculate cosine similarity
            for cv_candidate in os.listdir(self.user_txt_folder):
                cv_candidate_file_path = os.path.join(self.user_txt_folder, cv_candidate)
                with open(cv_candidate_file_path, 'r') as f:
                    candidate_desc = f.read()

                # Generate embedding for the candidate's resume text
                candidate_desc_embedding = self.generate_embeddings(candidate_desc)

                # Calculate cosine similarity between candidate's resume and expected competency
                score = self.calculate_cosine_similarity(candidate_desc_embedding, expected_competency_embedding)
                print(f'cosine similarity score for applicant named {cv_candidate} is {score}')
                scores[cv_candidate] = score
        except:
            print('error in calculating cosine similarity')

        # Sort candidates by score (descending) to rank them
        sorted_candidates = sorted(scores.items(), key=lambda item: item[1], reverse=True)

        # Create a ranked dictionary (rank starts from 1)
        ranked_candidates = {rank + 1: candidate for rank, (candidate, score) in enumerate(sorted_candidates)}

        return ranked_candidates











# pdf_pages = convert_from_path(document_path, dpi=350)

# user_folder = os.path.join('user_txt', user_uuid)
# os.makedirs(user_folder, exist_ok=True)

# text_file_path = os.path.join(user_folder, f'{user_uuid}.txt')

#             # Use concurrent futures for parallel processing
# with concurrent.futures.ThreadPoolExecutor() as executor:
#                 # Process pages in parallel and get OCR text for each page
#     results = executor.map(self.ocr_page, pdf_pages)

#                 # Write the extracted text to a file
#     with open(text_file_path, 'a', encoding='utf-8') as f:
#         for text in results:
#             f.write(text + "\n")
    # def ocr_page(self, page):
    #     return pytesseract.image_to_string(page)