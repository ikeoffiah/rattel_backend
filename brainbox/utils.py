import cloudinary.uploader as cloud
import os
import ast
from langchain.text_splitter import RecursiveCharacterTextSplitter
import cloudinary
import requests
from bs4 import BeautifulSoup
import chardet
import json
import PyPDF2
import faiss
import json
import numpy as np


def scrap_website(web_link, project_name):

    """Function to scrap websites"""

    web_text = requests.get(f"{web_link}").text
    web_soup = BeautifulSoup(web_text, 'lxml')
    all_data = web_soup.find_all('div')
    text = ""
    for i in all_data:
        if i == " ":
            pass
        text = text + i.text

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(text)
    url = upload_data(texts, project_name)
    return url



def upload_data(texts, project_name):

    """Operations to Upload and delete a csv file"""

    json_data = []

    for text in texts:
        data = {
            "text": text
        }
        json_data.append(data)

    json_string = json.dumps(json_data)
    with open(f'{project_name}.json', "w") as f:
        f.write(json_string)
    # Upload the CSV file to Cloudinary
    result = cloudinary.uploader.upload(f'{project_name}.json', resource_type="raw")

    # Delete the local file
    os.remove(f'{project_name}.json')

    # Print the URL of the uploaded JSON file
    return result['url']


def changeJson(url):
    response = requests.get(url)
    detected = chardet.detect(response.content)
    json_data = response.content.decode(detected["encoding"])

    json_data = ast.literal_eval(json_data)

    text = []

    for data in json_data:
        text.append(data["text"])

    return text



def scrap_pdf(file, project_name):
    pdf_reader = PyPDF2.PdfReader(file)
    text_in = ''
    for page_num in range(len(pdf_reader.pages)):
        text_in = text_in + pdf_reader.pages[page_num].extract_text()


    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(text_in)
    url = upload_data(texts, project_name)
    return url



# Parse JSON data and extract relevant information
def parse_json(json_data):
    parsed_data = []
    for item in json_data:
        # Assuming 'text' is the field containing textual data to vectorize
        text = item.get('text', '')
        # Assuming 'category' is the field containing categorical data to encode
        category = item.get('category', '')
        # You may have additional fields to parse
        # Your parsing logic here
        parsed_data.append((text, category))
    return parsed_data

# Vectorize data
def vectorize_data(parsed_data):
    vectors = []
    for text, category in parsed_data:
        # Your vectorization logic here
        # Example: Combining text and category into a single vector
        vector = np.random.rand(10)  # Placeholder vector
        vectors.append(vector)
    return np.array(vectors).astype(np.float32)

# Example JSON data
json_data = '''
[
    {"id": 1, "text": "example text 1", "category": "cat1"},
    {"id": 2, "text": "example text 2", "category": "cat2"}
]
'''

parsed_data = parse_json(json.loads(json_data))
vectors = vectorize_data(parsed_data)

# Indexing
index = faiss.IndexFlatL2(vectors.shape[1])  # You can choose other index types based on your needs
index.add(vectors)

# Example search
query_vector = np.random.rand(1, vectors.shape[1]).astype(np.float32)  # Example query vector
k = 5  # Number of nearest neighbors to retrieve
distances, indices = index.search(query_vector, k)

print("Indices of nearest neighbors:", indices)
print("Distances to nearest neighbors:", distances)
