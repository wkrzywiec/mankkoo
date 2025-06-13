import { useGetHttp } from "@/hooks/useHttp";
import { WalletsResponse } from "@/api/InvestmentsPageResponses";

export function useWallets() {
  const { fetchedData: wallets, isFetching } = useGetHttp<WalletsResponse>("/investments/wallets");
  return { wallets, isFetching };
}
