from rapidfuzz import process
from sqlalchemy.orm import Session
from app.models.product import Product as ProductModel
from typing import List, Tuple

def search_products(db: Session, query: str, limit: int = 5) -> List[Tuple[ProductModel, float]]:
    """
    Busca produtos usando fuzzy matching sobre os nomes armazenados.
    Retorna uma lista de tuplas (produto, score).
    """
    products = db.query(ProductModel).all()
    # Cria uma lista de tuplas (nome, objeto_produto)
    # Convertemos para str explicitamente pois o SQLAlchemy pode retornar Column
    product_names = [str(p.name) for p in products]
    product_map = {str(p.name): p for p in products}
    
    # Busca os melhores matches
    matches = process.extract(query, product_names, limit=limit)
    
    return [(product_map[match[0]], float(match[1])) for match in matches]
