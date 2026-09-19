import imagehash
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def check_script_similarity(new_transcript, existing_transcripts_list, threshold=0.85):
    """
    Compares TF-IDF text vectors locally to detect plagiarized scripts.
    """
    if not existing_transcripts_list:
        return False, 0.0

    documents = existing_transcripts_list + [new_transcript]
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()

    # Compare last document (new_transcript) against all previous ones
    new_vec = vectors[-1].reshape(1, -1)
    past_vecs = vectors[:-1]
    
    similarities = cosine_similarity(new_vec, past_vecs)[0]
    max_similarity = float(max(similarities)) if len(similarities) > 0 else 0.0

    is_duplicate = max_similarity >= threshold
    return is_duplicate, round(max_similarity * 100, 2)