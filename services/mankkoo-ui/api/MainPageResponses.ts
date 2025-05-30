export interface MainIndicatorsResponse {
    savings: number;
    netWorth: number;
    lastMonthProfit: number;
    lastMonthSpending: number;
}

export interface SavingsDistribution {
    type: string;
    total: number;
    percentage: number;
}

export interface TotalHistory {
    date: string[];
    total: number[];
}