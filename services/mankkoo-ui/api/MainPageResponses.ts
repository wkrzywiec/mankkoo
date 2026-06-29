export interface MainIndicatorsResponse {
    savings: number;
    netWorth: number;
    lastMonthIncome: number;
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

export interface MonthlyIncome {
    date: string[];
    total: number[];
}