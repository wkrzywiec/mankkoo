export const createStreamPossibleSubtypes: Record<string, string[]> = {
    "account": ["checking", "savings", "cash"],
    "investment": ["treasury_bonds", "deposit"],
    "stocks": ["ETF"],
    "retirement": ["retirement"],
    "real-estate": [ "" ]
}

export const createStreamRequiredMetadata: Record<string, string[]> = {
    "account": ["alias", "bankUrl", "importer", "accountNumber"],
    "investment": ["details"],
    "stocks": ["etfUrl", "ike", "ikze"],
    "retirement": ["alias", "bankUrl", "importer", "accountNumber"],
    "real-estate": [ "" ]
}

export const addEventRequiredProps: Record<string,  Record<string, string[]>> = {
    "account": {
        "MoneyWithdrawn": ["amount", "currency", "title"],
        "MoneyDeposited": ["amount", "currency", "title"],
    },
    "investment": {
        "TreasuryBondsBought": ["balance", "totalValue", "currency", "units", "pricePerUnit"],
        "TreasuryBondsMatured": ["balance", "totalValue", "currency", "units", "pricePerUnit"],
        "TermDepositOpened": ["balance", "amount", "currency"],
        "TermDepositFinished": ["balance", "amount", "currency"],
        "InvestmentFundBought": ["balance", "totalValue", "currency"],
        "InvestmentFundSold": ["balance", "totalValue", "currency"],
    },
    "stocks": {
        "ETFBought": ["averagePrice" ,"balance", "currency", "totalValue", "units"],
        "ETFSold": ["averagePrice" ,"balance", "comment", "currency", "totalValue", "units"],
        "ETFPriced": ["averagePrice" ,"balance", "currency", "totalValue", "units"],
    },
    "retirement": {
        "MoneyWithdrawn": ["amount", "currency", "title"],
        "MoneyDeposited": ["amount", "currency", "title"],
    },
    "real-estate": {}
}

