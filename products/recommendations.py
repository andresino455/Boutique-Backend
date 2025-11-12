# products/recommendations.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from .models import Product

# ✅ Manejo seguro de NLTK con fallback
try:
    from nltk.corpus import stopwords
    spanish_stopwords = stopwords.words('spanish')
except (ImportError, LookupError):
    # Si NLTK no está disponible o no tiene los datos, usar lista manual
    spanish_stopwords = [
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 
        'haber', 'por', 'con', 'su', 'para', 'como', 'estar', 'tener', 
        'le', 'lo', 'todo', 'pero', 'más', 'hacer', 'o', 'poder', 'decir',
        'este', 'ir', 'otro', 'ese', 'la', 'si', 'me', 'ya', 'ver', 'porque',
        'dar', 'cuando', 'él', 'muy', 'sin', 'vez', 'mucho', 'saber', 'qué',
        'sobre', 'mi', 'alguno', 'mismo', 'yo', 'también', 'hasta', 'año',
        'dos', 'querer', 'entre', 'así', 'primero', 'desde', 'grande', 'eso',
        'ni', 'nos', 'llegar', 'pasar', 'tiempo', 'ella', 'sí', 'día', 'uno',
        'bien', 'poco', 'deber', 'entonces', 'poner', 'cosa', 'tanto', 'hombre',
        'parecer', 'nuestro', 'tan', 'donde', 'ahora', 'parte', 'después', 'vida',
        'quedar', 'siempre', 'creer', 'hablar', 'llevar', 'dejar', 'nada', 'cada',
        'seguir', 'menos', 'nuevo', 'encontrar', 'algo', 'solo', 'decir', 'casa',
        'usar', 'tal', 'allí', 'sólo', 'escribir', 'madre', 'padre', 'trabajar',
        'mes', 'pedir', 'hora', 'gente', 'estar', 'tener', 'los', 'las', 'del',
        'al', 'una', 'unos', 'unas', 'estos', 'estas', 'esos', 'esas', 'aquel',
        'aquella', 'aquellos', 'aquellas'
    ]

def get_recommended_products(product_id, top_n=5):
    """
    Obtiene productos recomendados basados en similitud de contenido
    
    Args:
        product_id: ID del producto base
        top_n: Número de recomendaciones a devolver
        
    Returns:
        Lista de productos recomendados
    """
    try:
        # Obtener todos los productos
        products = list(Product.objects.all())

        if not products:
            return []

        # Crear DataFrame
        df = pd.DataFrame([{
            'id': p.id,
            'name': p.name,
            'description': p.description or '',
            'category': p.category.name if hasattr(p, 'category') and p.category else ''
        } for p in products])

        # Combinar texto
        df['content'] = df['name'] + " " + df['description'] + " " + df['category']

        # Vectorizar texto con stopwords
        tfidf = TfidfVectorizer(
            stop_words=spanish_stopwords,
            max_features=1000,  # Limitar features para mejor rendimiento
            ngram_range=(1, 2)  # Usar unigramas y bigramas
        )
        tfidf_matrix = tfidf.fit_transform(df['content'])

        # Calcular similaridad de coseno
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        # Crear mapa de índices
        indices = pd.Series(df.index, index=df['id'])

        # Verificar que el producto existe
        if product_id not in indices.index:
            return []

        # Obtener índice del producto
        idx = indices[product_id]
        
        # Calcular scores de similitud
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Excluir el producto actual y limitar resultados
        sim_scores = [s for s in sim_scores if s[0] != idx][:top_n]
        similar_indices = [i[0] for i in sim_scores]

        # Devolver productos recomendados
        return [products[i] for i in similar_indices]
        
    except Exception as e:
        # Log del error (en producción esto debería ir a tu sistema de logs)
        print(f"Error en get_recommended_products: {str(e)}")
        # Devolver lista vacía en caso de error
        return []