
export interface MainIndicators {
    savings: number;
    debt: number;
    lastMonthProfit: number;
    investments: number;
}

export interface SavingsDistributionCategory {
    type: string;
    total: number;
    percentage: number;
}

export interface TotalMoneyHistory {
    date: string[];
    total: number[]
}

export interface TotalMonthlyProfit {
    date: string[];
    total: number[]
}