import sqlite3
conn = sqlite3.connect('preco_perto.db')
cur = conn.cursor()
print('Receipts:', cur.execute('SELECT status, cnpj_extracted, image_url FROM receipts ORDER BY created_at DESC LIMIT 1').fetchall())
print('New product:', cur.execute("SELECT name FROM products WHERE name LIKE '%Iogurte%'").fetchall())
print('New prices:', cur.execute("SELECT price, source, source_id IS NOT NULL as has_source_id FROM prices WHERE source='receipt'").fetchall())
conn.close()
