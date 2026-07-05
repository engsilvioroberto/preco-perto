#!/usr/bin/env python3
"""Inicializa o banco SQLite criando as tabelas"""
import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.core.database import engine, Base
from app.models import User, Market, Product, Price, Receipt, ReceiptItem

def init_db():
    """Cria todas as tabelas no banco"""
    print("🚀 Criando tabelas no banco SQLite...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init_db()
