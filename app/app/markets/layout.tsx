import { WalletRequired } from "../../components/wallet-required";
export default function MarketLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <WalletRequired>{children}</WalletRequired>;
}
