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
}