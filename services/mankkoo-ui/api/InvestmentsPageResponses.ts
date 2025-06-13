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

export interface InvestmentTypesDistributionPerWalletItem {
    percentage: number;
    total: number;
    wallet: string;
    type: string;
}

export interface InvestmentTypesDistributionPerWalletsResponse {
    data: InvestmentTypesDistributionPerWalletItem[];
    viewName: string;
}

export interface WalletsResponse {
    wallets: string[];
}

export interface InvestmentStreamResponse {
    id: string;
    name: string;
    investmentType: string;
    subtype: string;
    balance: number;
}

export interface InvestmentTransaction {
    occuredAt: string;
    eventType: string;
    unitsCount: number | null;
    pricePerUnit: number | null;
    totalValue: number | null;
    balance: number | null;
    comment?: string | null;
}