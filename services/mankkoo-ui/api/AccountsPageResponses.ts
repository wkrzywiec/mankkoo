export interface AccountInfoResponse {
    id: string;
    name: string;
    number: string;
    alias?: string;
    type: string;
    importer: string;
    active: boolean;
    bankName: string;
    bankUrl: string;
    hidden: boolean;
    openedAt: string;
}

export interface AccountTransactionResponse {
    balance: number;
    comment?: string;
    currency: string;
    date: string;
    details?: string;
    id: string;
    operation: number;
    title: string;
}