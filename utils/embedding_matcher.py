from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return model.encode(text, convert_to_tensor=True)

def get_similarity_score(embedding1, embedding2):
    return float(util.cos_sim(embedding1, embedding2)[0][0])