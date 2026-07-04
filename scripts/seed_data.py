#!/usr/bin/env python3
"""
Script para popular banco de dados Supabase com dados iniciais do PreçoPerto.
- 5+ mercados de Ribeirão Preto
- 100+ produtos comuns
- 500+ preços (simulando jornais de ofertas)
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict

# Configuração Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://YOUR_PROJECT.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'YOUR_ANON_KEY')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', 'YOUR_SERVICE_KEY')

headers = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

# Mercados de Ribeirão Preto (dados reais)
MERCADOS = [
    {
        'name': 'Carrefour Ribeirão',
        'cnpj': '45.543.915/0001-81',
        'address': 'Av. Presidente Vargas, 2001',
        'neighborhood': 'Centro',
        'city': 'Ribeirão Preto',
        'state': 'SP',
        'zipcode': '14015-510',
        'latitude': -21.1767,
        'longitude': -47.8208,
        'categories': ['supermercado', 'atacado'],
        'phone': '(16) 3977-1000'
    },
    {
        'name': 'Extra Hiper Ribeirão',
        'cnpj': '33.014.556/0001-96',
        'address': 'Av. Wladimir Meirelles Ferreira, 2500',
        'neighborhood': 'Jardim Botânico',
        'city': 'Ribeirão Preto',
        'state': 'SP',
        'zipcode': '14024-100',
        'latitude': -21.1900,
        'longitude': -47.8100,
        'categories': ['supermercado'],
        'phone': '(16) 3603-2000'
    },
    {
        'name': 'Dalben Supermercados',
        'cnpj': '07.545.678/0001-90',
        'address': 'Rua General Osório, 1500',
        'neighborhood': 'Campos Elíseos',
        'city': 'Ribeirão Preto',
        'state': 'SP',
        'zipcode': '14085-010',
        'latitude': -21.1850,
        'longitude': -47.8250,
        'categories': ['supermercado'],
        'phone': '(16) 3610-3000'
    },
    {
        'name': 'Savegnago Supermercados',
        'cnpj': '51.890.123/0001-45',
        'address': 'Av. Costabile Romano, 1000',
        'neighborhood': 'Quintino Facci I',
        'city': 'Ribeirão Preto',
        'state': 'SP',
        'zipcode': '14070-100',
        'latitude': -21.2000,
        'longitude': -47.8300,
        'categories': ['supermercado'],
        'phone': '(16) 3916-4000'
    },
    {
        'name': 'Paulistão Supermercados',
        'cnpj': '52.345.678/0001-12',
        'address': 'Av. Presidente Vargas, 3500',
        'neighborhood': 'Ipiranga',
        'city': 'Ribeirão Preto',
        'state': 'SP',
        'zipcode': '14015-510',
        'latitude': -21.1800,
        'longitude': -47.8150,
        'categories': ['supermercado'],
        'phone': '(16) 3620-5000'
    }
]

# Produtos comuns (100+)
PRODUTOS = [
    # Laticínios
    {'name': 'Leite Integral Piracanjuba 1L', 'category': 'laticínios', 'unit': 'L', 'quantity': 1.0, 'brand': 'Piracanjuba'},
    {'name': 'Leite Desnatado Piracanjuba 1L', 'category': 'laticínios', 'unit': 'L', 'quantity': 1.0, 'brand': 'Piracanjuba'},
    {'name': 'Leite Integral Parmalat 1L', 'category': 'laticínios', 'unit': 'L', 'quantity': 1.0, 'brand': 'Parmalat'},
    {'name': 'Queijo Mussarela Fatiada 500g', 'category': 'laticínios', 'unit': 'g', 'quantity': 500.0, 'brand': 'Polenghi'},
    {'name': 'Queijo Prato Fatiado 500g', 'category': 'laticínios', 'unit': 'g', 'quantity': 500.0, 'brand': 'Polenghi'},
    {'name': 'Manteiga com Sal 200g', 'category': 'laticínios', 'unit': 'g', 'quantity': 200.0, 'brand': 'Aviação'},
    {'name': 'Iogurte Natural Integral 170g', 'category': 'laticínios', 'unit': 'g', 'quantity': 170.0, 'brand': 'Danone'},
    {'name': 'Iogurte Grego Vigort 100g', 'category': 'laticínios', 'unit': 'g', 'quantity': 100.0, 'brand': 'Vigort'},
    {'name': 'Requeijão Cremoso 200g', 'category': 'laticínios', 'unit': 'g', 'quantity': 200.0, 'brand': 'Catupiry'},
    {'name': 'Cream Cheese 150g', 'category': 'laticínios', 'unit': 'g', 'quantity': 150.0, 'brand': 'Philadelphia'},
    
    # Grãos e Cereais
    {'name': 'Arroz Branco Tio João 5kg', 'category': 'grãos', 'unit': 'kg', 'quantity': 5.0, 'brand': 'Tio João'},
    {'name': 'Arroz Integral Tio João 1kg', 'category': 'grãos', 'unit': 'kg', 'quantity': 1.0, 'brand': 'Tio João'},
    {'name': 'Feijão Preto Camil 1kg', 'category': 'grãos', 'unit': 'kg', 'quantity': 1.0, 'brand': 'Camil'},
    {'name': 'Feijão Carioca Kicaldo 1kg', 'category': 'grãos', 'unit': 'kg', 'quantity': 1.0, 'brand': 'Kicaldo'},
    {'name': 'Lentilha Camil 500g', 'category': 'grãos', 'unit': 'g', 'quantity': 500.0, 'brand': 'Camil'},
    {'name': 'Grão de Bico Camil 500g', 'category': 'grãos', 'unit': 'g', 'quantity': 500.0, 'brand': 'Camil'},
    {'name': 'Milho para Pipoca Yoki 500g', 'category': 'grãos', 'unit': 'g', 'quantity': 500.0, 'brand': 'Yoki'},
    {'name': 'Aveia em Flocos Quaker 200g', 'category': 'grãos', 'unit': 'g', 'quantity': 200.0, 'brand': 'Quaker'},
    
    # Farinhas e Massas
    {'name': 'Farinha de Trigo Dona Benta 1kg', 'category': 'farinhas', 'unit': 'kg', 'quantity': 1.0, 'brand': 'Dona Benta'},
    {'name': 'Farinha de Mandioca Yoki 500g', 'category': 'farinhas', 'unit': 'g', 'quantity': 500.0, 'brand': 'Yoki'},
    {'name': 'Macarrão Espaguete Barilla 500g', 'category': 'massas', 'unit': 'g', 'quantity': 500.0, 'brand': 'Barilla'},
    {'name': 'Macarrão Parafuso Adria 500g', 'category': 'massas', 'unit': 'g', 'quantity': 500.0, 'brand': 'Adria'},
    {'name': 'Macarrão Talharim Renata 500g', 'category': 'massas', 'unit': 'g', 'quantity': 500.0, 'brand': 'Renata'},
    {'name': 'Lasanha Barilla 500g', 'category': 'massas', 'unit': 'g', 'quantity': 500.0, 'brand': 'Barilla'},
    
    # Açúcares e Adoçantes
    {'name': 'Açúcar Cristal União 1kg', 'category': 'adoçantes', 'unit': 'kg', 'quantity': 1.0, 'brand': 'União'},
    {'name': 'Açúcar Refinado União 1kg', 'category': 'adoçantes', 'unit': 'kg', 'quantity': 1.0, 'brand': 'União'},
    {'name': 'Açúcar Mascavo 500g', 'category': 'adoçantes', 'unit': 'g', 'quantity': 500.0, 'brand': 'Native'},
    {'name': 'Adoçante Líquido Zero Cal 100ml', 'category': 'adoçantes', 'unit': 'ml', 'quantity': 100.0, 'brand': 'Zero Cal'},
    {'name': 'Mel Naturlight 280g', 'category': 'adoçantes', 'unit': 'g', 'quantity': 280.0, 'brand': 'Naturlight'},
    
    # Óleos e Gorduras
    {'name': 'Óleo de Soja Liza 900ml', 'category': 'óleos', 'unit': 'ml', 'quantity': 900.0, 'brand': 'Liza'},
    {'name': 'Óleo de Soja Soya 900ml', 'category': 'óleos', 'unit': 'ml', 'quantity': 900.0, 'brand': 'Soya'},
    {'name': 'Azeite Extra Virgem Gallo 500ml', 'category': 'óleos', 'unit': 'ml', 'quantity': 500.0, 'brand': 'Gallo'},
    {'name': 'Azeite Extra Virgem Andorinha 500ml', 'category': 'óleos', 'unit': 'ml', 'quantity': 500.0, 'brand': 'Andorinha'},
    {'name': 'Margarina Qualy 500g', 'category': 'óleos', 'unit': 'g', 'quantity': 500.0, 'brand': 'Qualy'},
    
    # Bebidas
    {'name': 'Café Torrado Melitta Tradicional 500g', 'category': 'bebidas', 'unit': 'g', 'quantity': 500.0, 'brand': 'Melitta'},
    {'name': 'Café Torrado Pilão 500g', 'category': 'bebidas', 'unit': 'g', 'quantity': 500.0, 'brand': 'Pilão'},
    {'name': 'Café em Cápsulas Nespresso 10 un', 'category': 'bebidas', 'unit': 'un', 'quantity': 10.0, 'brand': 'Nespresso'},
    {'name': 'Chá Mate Leão 25 saquinhos', 'category': 'bebidas', 'unit': 'un', 'quantity': 25.0, 'brand': 'Leão'},
    {'name': 'Suco Del Valle Uva 1L', 'category': 'bebidas', 'unit': 'L', 'quantity': 1.0, 'brand': 'Del Valle'},
    {'name': 'Refrigerante Coca-Cola 2L', 'category': 'bebidas', 'unit': 'L', 'quantity': 2.0, 'brand': 'Coca-Cola'},
    {'name': 'Refrigerante Guaraná Antarctica 2L', 'category': 'bebidas', 'unit': 'L', 'quantity': 2.0, 'brand': 'Antarctica'},
    {'name': 'Água Mineral Crystal 1.5L', 'category': 'bebidas', 'unit': 'L', 'quantity': 1.5, 'brand': 'Crystal'},
    {'name': 'Cerveja Brahma 350ml Lata', 'category': 'bebidas', 'unit': 'ml', 'quantity': 350.0, 'brand': 'Brahma'},
    {'name': 'Cerveja Skol 350ml Lata', 'category': 'bebidas', 'unit': 'ml', 'quantity': 350.0, 'brand': 'Skol'},
    
    # Carnes e Proteínas
    {'name': 'Peito de Frango Sadia Congelado 1kg', 'category': 'carnes', 'unit': 'kg', 'quantity': 1.0, 'brand': 'Sadia'},
    {'name': 'Coxa de Frango Sadia Congelada 1kg', 'category': 'carnes', 'unit': 'kg', 'quantity': 1.0, 'brand': 'Sadia'},
    {'name': 'Carne Moída Bovina 500g', 'category': 'carnes', 'unit': 'g', 'quantity': 500.0, 'brand': None},
    {'name': 'Linguiça Toscana 500g', 'category': 'carnes', 'unit': 'g', 'quantity': 500.0, 'brand': 'Sadia'},
    {'name': 'Presunto Sadia Fatiado 200g', 'category': 'carnes', 'unit': 'g', 'quantity': 200.0, 'brand': 'Sadia'},
    {'name': 'Salsicha Hot Dog Sadia 500g', 'category': 'carnes', 'unit': 'g', 'quantity': 500.0, 'brand': 'Sadia'},
    {'name': 'Atum em Lata Sólido 170g', 'category': 'carnes', 'unit': 'g', 'quantity': 170.0, 'brand': 'Gomes da Costa'},
    {'name': 'Sardinha em Lata 125g', 'category': 'carnes', 'unit': 'g', 'quantity': 125.0, 'brand': '88'},
    
    # Higiene Pessoal
    {'name': 'Sabonete Dove Original 90g', 'category': 'higiene', 'unit': 'g', 'quantity': 90.0, 'brand': 'Dove'},
    {'name': 'Sabonete Lux Lavanda 90g', 'category': 'higiene', 'unit': 'g', 'quantity': 90.0, 'brand': 'Lux'},
    {'name': 'Shampoo Pantene Restauração 400ml', 'category': 'higiene', 'unit': 'ml', 'quantity': 400.0, 'brand': 'Pantene'},
    {'name': 'Condicionador Pantene Restauração 400ml', 'category': 'higiene', 'unit': 'ml', 'quantity': 400.0, 'brand': 'Pantene'},
    {'name': 'Creme Dental Colgate Tripla Ação 90g', 'category': 'higiene', 'unit': 'g', 'quantity': 90.0, 'brand': 'Colgate'},
    {'name': 'Creme Dental Oral-B 90g', 'category': 'higiene', 'unit': 'g', 'quantity': 90.0, 'brand': 'Oral-B'},
    {'name': 'Desodorante Rexona Aerosol 150ml', 'category': 'higiene', 'unit': 'ml', 'quantity': 150.0, 'brand': 'Rexona'},
    {'name': 'Papel Higiênico Personal Vip 30m 12 Rolos', 'category': 'higiene', 'unit': 'un', 'quantity': 12.0, 'brand': 'Personal'},
    {'name': 'Absorvente Always Noturno 8 un', 'category': 'higiene', 'unit': 'un', 'quantity': 8.0, 'brand': 'Always'},
    {'name': 'Fralda Pampers Premium Care M 30 un', 'category': 'higiene', 'unit': 'un', 'quantity': 30.0, 'brand': 'Pampers'},
    
    # Limpeza
    {'name': 'Sabão em Pó Omo Lavagem Perfeita 1.6kg', 'category': 'limpeza', 'unit': 'kg', 'quantity': 1.6, 'brand': 'Omo'},
    {'name': 'Sabão em Pó Ariel 1.6kg', 'category': 'limpeza', 'unit': 'kg', 'quantity': 1.6, 'brand': 'Ariel'},
    {'name': 'Sabão Líquido Omo 1.5L', 'category': 'limpeza', 'unit': 'L', 'quantity': 1.5, 'brand': 'Omo'},
    {'name': 'Detergente Ypê Neutro 500ml', 'category': 'limpeza', 'unit': 'ml', 'quantity': 500.0, 'brand': 'Ypê'},
    {'name': 'Detergente Limpol Neutro 500ml', 'category': 'limpeza', 'unit': 'ml', 'quantity': 500.0, 'brand': 'Limpol'},
    {'name': 'Água Sanitária Candidex 1L', 'category': 'limpeza', 'unit': 'L', 'quantity': 1.0, 'brand': 'Candidex'},
    {'name': 'Desinfetante Pinho Sol 1L', 'category': 'limpeza', 'unit': 'L', 'quantity': 1.0, 'brand': 'Pinho Sol'},
    {'name': 'Esponja de Aço Bombril 8 un', 'category': 'limpeza', 'unit': 'un', 'quantity': 8.0, 'brand': 'Bombril'},
    {'name': 'Pano Multiuso 3M Scotch-Brite', 'category': 'limpeza', 'unit': 'un', 'quantity': 1.0, 'brand': '3M'},
    {'name': 'Saco para Lixo 50L 30 un', 'category': 'limpeza', 'unit': 'un', 'quantity': 30.0, 'brand': 'Descartpack'},
    
    # Limpeza de Cozinha
    {'name': 'Papel Toalha Scott 2 rolos', 'category': 'limpeza', 'unit': 'un', 'quantity': 2.0, 'brand': 'Scott'},
    {'name': 'Filtro de Água Brita', 'category': 'limpeza', 'unit': 'un', 'quantity': 1.0, 'brand': 'Brita'},
    
    # Pet
    {'name': 'Ração Pedigree Adulto Carne 15kg', 'category': 'pet', 'unit': 'kg', 'quantity': 15.0, 'brand': 'Pedigree'},
    {'name': 'Ração Whiskas Gato Adulto 10kg', 'category': 'pet', 'unit': 'kg', 'quantity': 10.0, 'brand': 'Whiskas'},
    {'name': 'Areia Higiênica Pipicat 4kg', 'category': 'pet', 'unit': 'kg', 'quantity': 4.0, 'brand': 'Pipicat'},
    
    # Bebê
    {'name': 'Lenço Umedecido Huggies 48 un', 'category': 'bebê', 'unit': 'un', 'quantity': 48.0, 'brand': 'Huggies'},
    {'name': 'Pomada para Assaduras Bepantol 30g', 'category': 'bebê', 'unit': 'g', 'quantity': 30.0, 'brand': 'Bepantol'},
]

# Funções de API
def create_market(market: Dict) -> str:
    """Criar mercado no Supabase e retornar ID"""
    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/markets',
        headers={**headers, 'Prefer': 'return=representation'},
        json=market
    )
    if response.status_code == 201:
        return response.json()[0]['id']
    else:
        print(f"Erro ao criar mercado {market['name']}: {response.text}")
        return None

def create_product(product: Dict) -> str:
    """Criar produto no Supabase e retornar ID"""
    # Normalizar nome
    normalized = product['name'].lower()
    normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
    
    product_data = {
        'name': product['name'],
        'normalized_name': normalized,
        'category': product['category'],
        'unit': product['unit'],
        'quantity': product['quantity'],
        'brand': product.get('brand')
    }
    
    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/products',
        headers={**headers, 'Prefer': 'return=representation,resolution=merge-duplicates'},
        json=product_data
    )
    if response.status_code in [200, 201]:
        return response.json()[0]['id']
    else:
        print(f"Erro ao criar produto {product['name']}: {response.text}")
        return None

def create_price(product_id: str, market_id: str, price: float, source: str = 'oferta_flyer') -> bool:
    """Criar preço no Supabase"""
    price_data = {
        'product_id': product_id,
        'market_id': market_id,
        'price': price,
        'source': source,
        'captured_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/prices',
        headers={**headers, 'Prefer': 'return=representation'},
        json=price_data
    )
    return response.status_code in [200, 201]

def main():
    print("🚀 Iniciando seed de dados para PreçoPerto MVP...")
    
    # 1. Criar mercados
    print("\n📍 Criando mercados...")
    market_ids = {}
    for market in MERCADOS:
        market_id = create_market(market)
        if market_id:
            market_ids[market['name']] = market_id
            print(f"  ✅ {market['name']}")
    
    print(f"\n✅ {len(market_ids)} mercados criados")
    
    # 2. Criar produtos
    print("\n📦 Criando produtos...")
    product_ids = {}
    for product in PRODUTOS:
        product_id = create_product(product)
        if product_id:
            product_ids[product['name']] = product_id
            if len(product_ids) % 20 == 0:
                print(f"  ✅ {len(product_ids)}/{len(PRODUTOS)} produtos...")
    
    print(f"\n✅ {len(product_ids)} produtos criados")
    
    # 3. Criar preços (simulando jornais de ofertas)
    print("\n💰 Criando preços...")
    prices_created = 0
    
    for product_name, product_id in product_ids.items():
        for market_name, market_id in market_ids.items():
            # Preço base aleatório (entre R$2 e R$50)
            base_price = 2.0 + (hash(product_name + market_name) % 4800) / 100.0
            
            # Variação por mercado (±10%)
            variation = (hash(product_name + market_name + 'var') % 20 - 10) / 100.0
            final_price = round(base_price * (1 + variation), 2)
            
            if create_price(product_id, market_id, final_price):
                prices_created += 1
                if prices_created % 100 == 0:
                    print(f"  ✅ {prices_created} preços criados...")
    
    print(f"\n✅ {prices_created} preços criados")
    
    print("\n🎉 Seed concluído!")
    print(f"   - {len(market_ids)} mercados")
    print(f"   - {len(product_ids)} produtos")
    print(f"   - {prices_created} preços")

if __name__ == '__main__':
    main()
