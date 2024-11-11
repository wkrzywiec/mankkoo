export interface MainIndicatorsResponse {
    savings: number;
    debt: number;
    lastMonthProfit: number;
    investments: number;
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