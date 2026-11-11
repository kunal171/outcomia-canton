"use client";
import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useCantonWallet } from "./canton-wallet-provider";
/** Render children only after live party/network verification; no market reads leak through. */
export function WalletRequired({ children }: { children: ReactNode }) {
  const { state } = useCantonWallet();
  const router = useRouter();
  useEffect(() => {
    if (["idle", "error"].includes(state.kind)) router.replace("/");
  }, [state.kind, router]);
  if (!state.session)
    return (
      <main className="workspace">
        <p role="status">
          {state.kind === "disconnecting"
            ? "Disconnecting…"
            : "Checking wallet…"}
        </p>
      </main>
    );
  return <>{children}</>;
}
