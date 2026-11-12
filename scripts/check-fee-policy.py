"""Exact-rational checks for the fee design, not a contract integration test."""

from fractions import Fraction
from random import Random

MAX_INT = 2**63 - 1


def fee(notional: Fraction, bps: int, quantum: Fraction) -> Fraction:
    """Round cumulative nonnegative taker fees down to the asset quantum."""
    raw = notional * bps / 10_000
    return (raw // quantum) * quantum


def reserve(taker_notional, limit, remaining, bps, quantum):
    """Maximum future fee delta, including past cumulative rounding."""
    return fee(taker_notional + limit * remaining, bps, quantum) - fee(
        taker_notional, bps, quantum
    )


def main():
    rng = Random(7317)
    checks = orders = 0
    for decimals in range(11):
        quantum = Fraction(1, 10**decimals)
        # Coarse assets need larger lots so every price*quantity is transferable.
        scale = 10 ** max(2, decimals)
        lot = 10 ** max(0, 2 - decimals)
        for bps in [0, 1, 25, 1000]:
            for _ in range(100):
                initial = rng.randint(1, 30) * lot
                left = initial
                limit_raw = rng.randint(1, scale - 1)
                limit = Fraction(limit_raw, scale)
                taker = charged = paid = refunded = Fraction(0)
                original = limit * initial + reserve(taker, limit, left, bps, quantum)
                while left:
                    quantity = rng.randint(1, left // lot) * lot
                    is_taker = bool(rng.getrandbits(1))
                    price = (
                        Fraction(rng.randint(1, limit_raw), scale) if is_taker else limit
                    )
                    gross = price * quantity
                    assert gross % quantum == 0
                    old_reserve = reserve(taker, limit, left, bps, quantum)
                    next_taker = taker + gross if is_taker else taker
                    fill_fee = fee(next_taker, bps, quantum) - fee(taker, bps, quantum)
                    next_reserve = reserve(
                        next_taker, limit, left - quantity, bps, quantum
                    )
                    released = old_reserve - fill_fee - next_reserve
                    refund = (limit - price) * quantity + released
                    assert released >= 0 and refund >= 0
                    assert limit * left + old_reserve == (
                        gross + fill_fee + refund + limit * (left - quantity) + next_reserve
                    )
                    assert 0 <= fill_fee <= gross
                    paid += gross
                    charged += fill_fee
                    refunded += refund
                    taker = next_taker
                    left -= quantity
                    assert charged == fee(taker, bps, quantum)
                    # Cancelling here returns exactly the remaining escrow.
                    assert paid + charged + refunded + limit * left + reserve(
                        taker, limit, left, bps, quantum
                    ) == original
                    checks += 1
                assert paid + charged + refunded == original
                assert reserve(taker, limit, 0, bps, quantum) == 0
                orders += 1

                # Rounding catch-up must never exceed a sell fill's proceeds.
                taker = charged = Fraction(0)
                for _ in range(10):
                    gross = Fraction(rng.randint(limit_raw, scale - 1), scale) * (
                        rng.randint(1, 10) * lot
                    )
                    next_taker = taker + gross
                    delta = fee(next_taker, bps, quantum) - fee(taker, bps, quantum)
                    assert 0 <= delta <= gross and delta % quantum == 0
                    charged += delta
                    taker = next_taker
                    assert charged == fee(taker, bps, quantum)
                    checks += 1
                assert 0 <= taker * bps / 10_000 - charged < quantum

    quantum = Fraction(1, 10**6)
    limit, taker = Fraction("0.60"), Fraction("1.20")
    old = reserve(Fraction(0), limit, 5, 25, quantum)
    new = reserve(taker, limit, 2, 25, quantum)
    actual_fee = fee(taker, 25, quantum)
    refund = Fraction("0.60") + old - actual_fee - new
    assert (old, actual_fee, new, refund) == tuple(
        map(Fraction, ["0.0075", "0.003", "0.003", "0.6015"])
    )
    # Splitting a single execution into fills must retain cumulative rounding.
    first = fee(Fraction("0.0002"), 25, quantum)
    combined = fee(Fraction("0.0004"), 25, quantum)
    assert first == 0 and combined == quantum

    for bps in [0, 1, 25, 1000]:
        notional = Fraction("0.9999999999") * MAX_INT
        assert notional * bps < 10**24  # Numeric 14 integer capacity
        raw = notional * bps / 10_000
        whole = raw // 1
        fraction = raw - whole
        assert 0 <= whole <= MAX_INT
        for decimals in range(11):
            scale = 10**decimals
            ticks = (fraction * scale) // 1
            assert 0 <= ticks < scale <= 10**10 < MAX_INT
            assert Fraction(whole) + Fraction(ticks, scale) == fee(
                notional, bps, Fraction(1, scale)
            )
    print(
        f"PASS: {orders} buy-order lifecycles; {checks} buy/sell fill invariants; "
        "precisions 0..10; rates 0/1/25/1000 bps; maximum-Int bounds and worked example."
    )


if __name__ == "__main__":
    main()
