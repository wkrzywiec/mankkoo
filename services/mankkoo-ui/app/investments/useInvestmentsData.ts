import { useGetHttp } from "@/hooks/useHttp";
import { InvetsmentsIndicatorsResponse, InvestmentTypesDistributionResponse, WalletsDistributionResponse, WalletsResponse, InvestmentStreamResponse, InvestmentTypesDistributionPerWalletsResponse, InvestmentTransaction, DepositedVsValueHistory, DepositedVsValueHistoryPerWallet, DepositedVsValueItem, DepositedVsValuePerWalletItem } from "@/api/InvestmentsPageResponses";

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

  const {
    isFetching: isFetchingDepositedVsValue,
    fetchedData: depositedVsValue,
  } = useGetHttp<DepositedVsValueItem[]>('/investments/deposited-vs-value');

  const {
    isFetching: isFetchingDepositedVsValuePerWallet,
    fetchedData: depositedVsValuePerWallet,
  } = useGetHttp<DepositedVsValuePerWalletItem[]>('/investments/deposited-vs-value/per-wallet');

  const {
    isFetching: isFetchingDepositedVsValueHistory,
    fetchedData: depositedVsValueHistory,
  } = useGetHttp<DepositedVsValueHistory>('/investments/deposited-vs-value/history');

  const {
    isFetching: isFetchingDepositedVsValueHistoryPerWallet,
    fetchedData: depositedVsValueHistoryPerWallet,
  } = useGetHttp<DepositedVsValueHistoryPerWallet>('/investments/deposited-vs-value/history/per-wallet');

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
    isFetchingInvestmentTransactions,
    isFetchingDepositedVsValue,
    depositedVsValue,
    isFetchingDepositedVsValuePerWallet,
    depositedVsValuePerWallet,
    isFetchingDepositedVsValueHistory,
    depositedVsValueHistory,
    isFetchingDepositedVsValueHistoryPerWallet,
    depositedVsValueHistoryPerWallet,
  };
}
