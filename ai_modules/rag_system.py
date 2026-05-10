import os
import json
import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    faiss = None
    SentenceTransformer = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, 'knowledge_base')
VS_DIR = os.path.join(BASE_DIR, 'vector_store')

# Initialize the model if available
try:
    if SentenceTransformer:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    else:
        model = None
except Exception:
    model = None

INDEX_PATH = os.path.join(VS_DIR, 'gemstone_faiss.index')
CHUNKS_PATH = os.path.join(VS_DIR, 'chunks.npy')

def build_vector_store():
    """Reads gemstone_knowledge.txt, chunks it, and builds a FAISS index."""
    if model is None or faiss is None:
        return
        
    os.makedirs(VS_DIR, exist_ok=True)
    
    kb_file = os.path.join(KB_DIR, 'gemstone_knowledge.txt')
    if not os.path.exists(kb_file):
        return
            
    with open(kb_file, 'r', encoding='utf-8') as f:
        text = f.read()
        
    chunks = [c.strip() for c in text.split('\n') if c.strip()]
    if not chunks:
        return
        
    embeddings = model.encode(chunks)
    embeddings = np.array(embeddings).astype('float32')
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    faiss.write_index(index, INDEX_PATH)
    np.save(CHUNKS_PATH, np.array(chunks, dtype=object))

def retrieve_context(query: str, k=2) -> str:
    """Retrieves top-k most relevant chunks for the query."""
    if model is None or faiss is None:
        return "RAG environment not fully initialized (missing modules/model)."
        
    if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        build_vector_store()
        
    if not os.path.exists(INDEX_PATH):
        return "Failed to build vector store."
        
    index = faiss.read_index(INDEX_PATH)
    chunks = np.load(CHUNKS_PATH, allow_pickle=True)
    
    query_vector = model.encode([query]).astype('float32')
    distances, indices = index.search(query_vector, min(k, len(chunks)))
    
    results = []
    for idx in indices[0]:
        if idx < len(chunks):
            results.append(str(chunks[idx]))
            
    return " ".join(results)

def load_zodiac_traits(zodiac: str) -> str:
    """Loads astrological traits for a zodiac sign."""
    traits_path = os.path.join(KB_DIR, 'zodiac_traits.json')
    try:
        with open(traits_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(zodiac, f"Individuals of {zodiac} possess highly unique and dynamic cosmic traits.")
    except Exception:
        return f"Individuals of {zodiac} possess highly unique and dynamic cosmic traits."

def generate_explanation(life_path: int, zodiac_sign: str, planet: str, gemstone: str, problem: str, gender: str, weight: str, context: str) -> str:
    """
    Generates a structured astrology-style explanation using RAG context.
    """
    zodiac_trait = load_zodiac_traits(zodiac_sign)
    
    if "RAG environment not fully initialized" in context or "Failed to build" in context:
        rag_insight = "Embrace its cosmic energy to find balance and resolution."
    else:
        rag_insight = f"{context}"
        
    explanation = (
        f"1. Numerology Insight\n"
        f"Your life path number is {life_path}. In Vedic numerology, this signifies a powerful journey designed for your spiritual and worldly evolution.\n\n"
        f"2. Zodiac Influence\n"
        f"Born under the cosmic vibrations of {zodiac_sign}, you carry its essence. {zodiac_trait}\n\n"
        f"3. Planetary Energy\n"
        f"Your ruling planet is {planet}. The immense gravitational and spiritual pull of {planet} governs your natural inclinations, offering distinct strengths to navigate life's currents.\n\n"
        f"4. Gemstone Recommendation\n"
        f"To align your celestial energies, the ancient texts recommend {gemstone}. This divine stone acts as a conduit for {planet}'s purest vibrations.\n"
        f"Based on your body weight and gender, this gemstone suits your energy profile.\n\n"
        f"5. Guidance\n"
        f"Regarding your concerns about '{problem}', {gemstone} serves as your cosmic remedy. {rag_insight}"
    )
    return explanation
