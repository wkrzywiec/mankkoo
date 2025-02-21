export interface StreamResponse {
    id: string;
    type: string;
    name: string;
}

export interface StreamDetailsResponse {
    id: string;
    type: string;
    version: number;
    metadata: { [key: string]: string}
}