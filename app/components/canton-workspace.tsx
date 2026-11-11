"use client";
import { useCantonWallet } from "./canton-wallet-provider";
export function CantonWorkspace() {
  const { state, disconnect } = useCantonWallet();
  if (!state.session) return null;
  const { partyId, networkId } = state.session;
  return (
    <main className="workspace">
      <div className="workspace-heading">
        <div>
          <p className="eyebrow">Canton · {networkId.replace("canton:", "")}</p>
          <h1>Prediction markets</h1>
        </div>
        <button className="secondary-button" onClick={() => void disconnect()}>
          Disconnect
        </button>
      </div>
      <section className="connected-party" aria-label="Connected wallet">
        <div className="party-avatar" aria-hidden="true">
          C
        </div>
        <div>
          <strong>Console Wallet</strong>
          <p className="party-id">{partyId}</p>
        </div>
        <span className="connection-label">
          <i />
          Connected
        </span>
      </section>
      <section className="deployment-state" aria-labelledby="deployment-title">
        <svg viewBox="0 0 48 48" fill="none" aria-hidden="true">
          <path
            d="m24 5 19 19-19 19L5 24 24 5Z"
            stroke="currentColor"
            strokeWidth="1.5"
          />
          <path d="M16 24h16m-8-8v16" stroke="currentColor" strokeWidth="1.5" />
        </svg>
        <h2 id="deployment-title">Market deployment pending</h2>
        <p>
          Your wallet is connected. Canton market contracts are the next
          release.
        </p>
        <a
          href="https://github.com/kunal171/outcomia-canton"
          target="_blank"
          rel="noreferrer"
        >
          View development ↗
        </a>
      </section>
    </main>
  );
}
