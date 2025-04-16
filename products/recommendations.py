# products/recommendations.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from .models import Product
from nltk.corpus import stopwords

# Solo descarga esto una vez en tu entorno, no aquí
# import nltk
# nltk.download('stopwords')

spanish_stopwords = stopwords.words('spanish')

def get_recommended_products(product_id, top_n=5):
    # Obtener todos los productos
    products = list(Product.objects.all())

    if not products:
        return []

    # Crear DataFrame
    df = pd.DataFrame([{
        'id': p.id,
        'name': p.name,
        'description': p.description or '',
        'category': p.category.name if hasattr(p, 'category') else ''
    } for p in products])

    # Combinar texto
    df['content'] = df['name'] + " " + df['description'] + " " + df['category']

    # Vectorizar texto
    tfidf = TfidfVectorizer(stop_words=spanish_stopwords)
    tfidf_matrix = tfidf.fit_transform(df['content'])

    # Similaridad de coseno
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Mapa de índices
    indices = pd.Series(df.index, index=df['id'])

    if product_id not in indices:
        return []

    idx = indices[product_id]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Excluir el producto actual y limitar resultados
    sim_scores = [s for s in sim_scores if s[0] != idx][:top_n]
    similar_indices = [i[0] for i in sim_scores]

    return [products[i] for i in similar_indices]
