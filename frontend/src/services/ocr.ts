import { createWorker } from 'tesseract.js';
import type { ParsedReceipt, ParsedReceiptItem } from '../types';

const CNPJ_REGEX = /(\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2})/;
const DATE_REGEX = /(\d{2}\/\d{2}\/\d{4})/;
const PRICE_AT_END_REGEX = /(?:R\$\s?)?(\d{1,3}(?:\.\d{3})*,\d{2})\s*$/;
const LEADING_CODE_REGEX = /^\d+\s+/;
const QUANTITY_MARKER_REGEX = /\b(UN|KG|X\s?\d+)\b/gi;

function parsePriceToken(token: string): number {
  return parseFloat(token.replace(/\./g, '').replace(',', '.'));
}

export async function extractText(imageDataUrl: string): Promise<string> {
  const worker = await createWorker('por');
  try {
    const { data } = await worker.recognize(imageDataUrl);
    return data.text;
  } finally {
    await worker.terminate();
  }
}

export function parseReceiptText(text: string): ParsedReceipt {
  const lines = text.split('\n').map((line) => line.trim()).filter(Boolean);

  let cnpj: string | null = null;
  let total: number | null = null;
  let date: string | null = null;
  const items: ParsedReceiptItem[] = [];

  for (const line of lines) {
    if (!cnpj) {
      const cnpjMatch = line.match(CNPJ_REGEX);
      if (cnpjMatch) cnpj = cnpjMatch[1];
    }

    if (!date) {
      const dateMatch = line.match(DATE_REGEX);
      if (dateMatch) date = dateMatch[1];
    }

    if (/total/i.test(line)) {
      const totalMatch = line.match(PRICE_AT_END_REGEX);
      if (totalMatch) {
        total = parsePriceToken(totalMatch[1]);
        continue;
      }
    }

    const priceMatch = line.match(PRICE_AT_END_REGEX);
    if (priceMatch && typeof priceMatch.index === 'number') {
      let description = line.slice(0, priceMatch.index).trim();
      description = description.replace(LEADING_CODE_REGEX, '');
      description = description.replace(QUANTITY_MARKER_REGEX, '');
      description = description.replace(/\s+/g, ' ').trim();

      if (description.length > 0) {
        items.push({
          description,
          price: parsePriceToken(priceMatch[1]),
          include: true,
        });
      }
    }
  }

  return { cnpj, total, date, items };
}
