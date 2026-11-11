import type { Metadata } from "next";
import { cookies } from "next/headers";
import { CantonWalletProvider } from "../components/canton-wallet-provider";
import { Appearance } from "../components/appearance";
import { Brand } from "../components/brand";
import "./theme.css";
import "./globals.css";
export const metadata: Metadata = {
  title: "Outcomia | Every Outcome Has a Market.",
  description: "Limit-order prediction markets on Canton Network.",
};
export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const preferences = await cookies();
  const theme =
    preferences.get("outcomia_canton_theme")?.value === "dark"
      ? "dark"
      : "light";
  return (
    <html lang="en" data-theme={theme}>
      <body>
        <CantonWalletProvider>
          <header className="site-header">
            <Brand />
            <div className="header-actions">
              <span className="network-pill">
                <i />
                Canton
              </span>
              <Appearance initial={theme} />
            </div>
          </header>
          {children}
        </CantonWalletProvider>
      </body>
    </html>
  );
}
