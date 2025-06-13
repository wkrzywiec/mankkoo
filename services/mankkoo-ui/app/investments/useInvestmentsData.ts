import { useGetHttp } from "@/hooks/useHttp";
import { InvetsmentsIndicatorsResponse, InvestmentTypesDistributionResponse, WalletsDistributionResponse, WalletsResponse, InvestmentStreamResponse, InvestmentTypesDistributionPerWalletsResponse, InvestmentTransaction } from "@/api/InvestmentsPageResponses";

export function useInvestmentsData(selectedWallet: string, selectedInvestmentId: string | undefined) {
  const {
    isFetching: isFetchingInvIndicators,
    fetchedData: indicators,
  } = useGetHttp<InvetsmentsIndicatorsResponse>("/investments/indicators");

  const {
    isFetching: isFetchingInvTypeDistribution,
    fetchedData: invTypeDistribution,
  } = useGetHttp<InvestmentTypesDistributionResponse>('/admin/views/investment-types-distribution');

  const {
    isFetching: isFetchingWalletsDistribution,
    fetchedData: walletsDistribution,
  } = useGetHttp<WalletsDistributionResponse>('/admin/views/investment-wallets-distribution');

  const {
    fetchedData: wallets
  } = useGetHttp<WalletsResponse>(`/investments/wallets`);

  const {
    fetchedData: investmentsInWallet,
    isFetching: isFetchingInvestmentsInWallet,
  } = useGetHttp<InvestmentStreamResponse[]>(`/investments?wallet=${selectedWallet}&active=true`, !!selectedWallet);

  const {
    fetchedData: investmentTypeDistributionPerWallet,
  } = useGetHttp<InvestmentTypesDistributionPerWalletsResponse>('/admin/views/investment-types-distribution-per-wallet');

  const {
    fetchedData: investmentTransactions,
    isFetching: isFetchingInvestmentTransactions
  } = useGetHttp<InvestmentTransaction[]>(
    `/investments/transactions/${selectedInvestmentId ?? ""}`,
    !!selectedInvestmentId
  );

  return {
    isFetchingInvIndicators,
    indicators,
    isFetchingInvTypeDistribution,
    invTypeDistribution,
    isFetchingWalletsDistribution,
    walletsDistribution,
    wallets,
    investmentsInWallet,
    isFetchingInvestmentsInWallet,
    investmentTypeDistributionPerWallet,
    investmentTransactions,
    isFetchingInvestmentTransactions
  };
}
