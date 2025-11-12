"""
Configuración de NLTK para producción en Render
"""
import nltk
import os

def setup_nltk():
    """
    Descarga los recursos de NLTK necesarios
    """
    # Definir directorio de datos de NLTK
    nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
    
    # Crear directorio si no existe
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
    
    # Agregar al path de NLTK
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.append(nltk_data_dir)
    
    # Recursos necesarios
    resources = ['stopwords', 'punkt', 'wordnet', 'averaged_perceptron_tagger']
    
    for resource in resources:
        try:
            nltk.data.find(f'corpora/{resource}')
            print(f"✓ {resource} ya está instalado")
        except LookupError:
            print(f"📥 Descargando {resource}...")
            nltk.download(resource, download_dir=nltk_data_dir, quiet=True)

if __name__ == '__main__':
    setup_nltk()