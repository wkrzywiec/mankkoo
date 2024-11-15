export function currencyFormat(value?: number | string): string {
  
  let number: number;
  
  if (typeof value === 'string') {
    number = value === undefined ? 0 : parseFloat(value);
  } else {
    number = value === undefined ? 0 : value;
  }

  
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(number);
}

export function percentage(value?: number): string {
  const per = value === undefined ? 0 : value;
  return per.toLocaleString("pl-PL", {style: "percent", maximumFractionDigits: 2});
}

export function iban(value?: string): string {
  const iban = value === undefined ? '' : value;
  return iban.replace(/[^\dA-Z]/g, '').replace(/(.{4})/g, '$1 ').trim();
}