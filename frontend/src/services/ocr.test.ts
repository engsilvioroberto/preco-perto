import { describe, it, expect } from 'vitest';
import { parseReceiptText } from './ocr';

describe('parseReceiptText', () => {
  it('extracts cnpj, date, total and items from a typical cupom fiscal', () => {
    const text = [
      'SUPERMERCADO EXEMPLO LTDA',
      'CNPJ: 45.543.915/0001-81',
      'AV PRESIDENTE VARGAS 2001',
      'CUPOM FISCAL ELETRONICO - SAT',
      '------------------------------',
      '001 LEITE INTEGRAL PIRACANJUBA 1L UN 4,99',
      '002 ARROZ TIO JOAO 5KG UN 25,90',
      '003 FEIJAO PRETO CAMIL 1KG UN 9,50',
      '------------------------------',
      'TOTAL R$ 40,39',
      'FORMA PAGAMENTO: DINHEIRO',
      'DATA: 05/07/2026 14:32:10',
    ].join('\n');

    const result = parseReceiptText(text);

    expect(result.cnpj).toBe('45.543.915/0001-81');
    expect(result.date).toBe('05/07/2026');
    expect(result.total).toBe(40.39);
    expect(result.items).toEqual([
      { description: 'LEITE INTEGRAL PIRACANJUBA 1L', price: 4.99, include: true },
      { description: 'ARROZ TIO JOAO 5KG', price: 25.90, include: true },
      { description: 'FEIJAO PRETO CAMIL 1KG', price: 9.50, include: true },
    ]);
  });

  it('matches a CNPJ with no punctuation and a price prefixed with R$', () => {
    const text = [
      'FARMACIA TESTE',
      'CNPJ 12345678000199',
      'SHAMPOO PANTENE 400ML R$ 15,90',
      'TOTAL 15,90',
    ].join('\n');

    const result = parseReceiptText(text);

    expect(result.cnpj).toBe('12345678000199');
    expect(result.total).toBe(15.90);
    expect(result.items).toEqual([
      { description: 'SHAMPOO PANTENE 400ML', price: 15.90, include: true },
    ]);
  });

  it('parses a total with a thousands separator', () => {
    const text = 'TOTAL R$ 1.234,56';

    const result = parseReceiptText(text);

    expect(result.total).toBe(1234.56);
  });

  it('returns empty items and null fields for text with no recognizable lines', () => {
    const text = 'ALGUM TEXTO SEM ITENS\nOUTRA LINHA QUALQUER';

    const result = parseReceiptText(text);

    expect(result.cnpj).toBeNull();
    expect(result.total).toBeNull();
    expect(result.date).toBeNull();
    expect(result.items).toEqual([]);
  });
});
