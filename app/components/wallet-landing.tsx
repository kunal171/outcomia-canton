"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useCantonWallet } from "./canton-wallet-provider";

export function WalletLanding() {
  const { state, connect } = useCantonWallet();
  const router = useRouter();
  useEffect(() => {
    if (state.session) router.replace("/markets");
  }, [state.session, router]);
  const busy = ["checking", "connecting", "disconnecting"].includes(state.kind);
  return (
    <main className="landing">
      <div className="landing-copy">
        <p className="eyebrow">Prediction markets on Canton</p>
        <h1>
          Every Outcome
          <br />
          <span>Has a Market.</span>
        </h1>
        <p className="landing-description">Your view. Your price.</p>
        <button
          className="primary-button connect-button"
          disabled={busy || !!state.session}
          onClick={() => void connect()}
        >
          <svg
            className="wallet-symbol"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            aria-hidden="true"
          >
            <path
              d="M20 8V5H5a2 2 0 0 0 0 4h15v11H5a2 2 0 0 1-2-2V7M16 12h5v5h-5z"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          {state.kind === "connecting"
            ? "Approve in Console Wallet…"
            : state.kind === "checking"
              ? "Checking wallet…"
              : state.kind === "disconnecting"
                ? "Disconnecting…"
                : "Connect Console Wallet"}
          <span aria-hidden="true">↗</span>
        </button>
        <a
          className="wallet-install"
          href="https://consolewallet.io/"
          target="_blank"
          rel="noreferrer"
        >
          Get Console Wallet ↗
        </a>
        {state.error && (
          <p role="alert" className="error-message">
            {state.error}
          </p>
        )}
      </div>
      <div className="landing-art" aria-hidden="true">
        <div className="art-orbit orbit-outer" />
        <div className="art-orbit orbit-inner" />
        <div className="outcome outcome-yes">
          <span>YES</span>
          <strong>↗</strong>
        </div>
        <div className="art-center">⇄</div>
        <div className="outcome outcome-no">
          <span>NO</span>
          <strong>↘</strong>
        </div>
        <svg viewBox="0 0 520 420" fill="none">
          <path
            d="M120 130H200Q260 130 260 210M400 290H320Q260 290 260 210"
            stroke="currentColor"
            strokeWidth="1.4"
          />
          <path
            className="moving-thread"
            d="M120 130H200Q260 130 260 210M400 290H320Q260 290 260 210"
            stroke="var(--accent)"
            strokeWidth="3"
            strokeDasharray="8 200"
          />
        </svg>
      </div>
      <footer className="landing-footer">
        <span>Limit orders · Collateral-backed outcomes</span>
        <a
          href="https://github.com/kunal171/outcomia-canton"
          target="_blank"
          rel="noreferrer"
        >
          GitHub ↗
        </a>
      </footer>
    </main>
  );
}
