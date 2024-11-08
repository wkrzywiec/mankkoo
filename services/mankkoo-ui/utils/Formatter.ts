export function currencyFormat(value: number | undefined): string {
    const number = value === undefined ? 0 : value;
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(number);
}