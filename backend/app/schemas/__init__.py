from app.schemas.schemas import Product, ProductCreate, Market, MarketCreate, Price, PriceCreate
# Expor para compatibilidade com importações anteriores
schemas = type('schemas', (), {
    'Product': Product, 
    'ProductCreate': ProductCreate, 
    'Market': Market, 
    'MarketCreate': MarketCreate, 
    'Price': Price, 
    'PriceCreate': PriceCreate
})
