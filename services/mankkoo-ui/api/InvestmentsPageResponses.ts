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