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

export interface CreateInvestmentEventRequest {
    streamId: string;
    eventType: "buy" | "sell" | "price_update";
    occuredAt: string;        // ISO 8601 date string (YYYY-MM-DD)
    units?: number;           // Required for buy/sell
    totalValue: number;       // Required for all events (price_update uses it to derive unit price)
    comment?: string;
}

export interface CreateInvestmentEventResponse {
    result: "Success" | "Failure";
    eventId?: string;
    streamVersion?: number;
    details?: string;         // Error message if result === "Failure"
}

export interface DepositedVsValueItem {
    type: string;
    deposited: number;
    value: number;
}

export interface DepositedVsValuePerWalletItem {
    wallet: string;
    deposited: number;
    value: number;
}

export interface DepositedVsValueSeries {
    deposited: number[];
    value: number[];
}

export interface DepositedVsValueHistory {
    dates: string[];
    types: Record<string, DepositedVsValueSeries>;
}

export interface DepositedVsValueHistoryPerWallet {
    dates: string[];
    wallets: Record<string, DepositedVsValueSeries>;
}
