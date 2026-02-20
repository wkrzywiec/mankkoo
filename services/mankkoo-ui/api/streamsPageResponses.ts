export interface StreamResponse {
    id: string;
    type: string;
    subtype: string;
    bank: string;
    name: string;
    wallet: string;
}

export interface StreamDetailsResponse {
    id: string;
    type: string;
    name: string;
    version: number;
    metadata: { [key: string]: string};
    labels?: { [key: string]: string };
}

export interface EventResponse {
    type: string;
    occuredAt: string;
    data: { [key: string]: string}
}