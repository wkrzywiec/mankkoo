export interface InvetsmentsIndicatorsResponse {
    totalInvestments: number;
    lastYearTotalResultsValue: number;
    lastYearTotalResultsPercentage: number;
    resultsVsInflation: number;
}

export interface InvestmentTypeDistributionItem {
    percentage: number;
    total: number;
    type: string;
}

export interface InvestmentTypesDistributionResponse {
    data: InvestmentTypeDistributionItem[];
    viewName: string;
}

export interface WalletDistributionItem {
    percentage: number;
    total: number;
    wallet: string;
}

export interface WalletsDistributionResponse {
    data: WalletDistributionItem[];
    viewName: string;
}