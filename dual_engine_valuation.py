"""
Dual-Engine Used Vehicle Valuation System (ICE + EV)
Outputs JSON with: status, engine_used, vehicle_metrics, pricing, breakdown_log

Tune CONFIG constants to calibrate against real market comps.
"""

from datetime import datetime, date
from math import floor
import json

# ----------------------------
# CONFIG: TUNABLE PARAMETERS
# ----------------------------
CONFIG = {
    # defaults
    "default_avg_annual_km": 10000,     # conservative average India annual km
    "estimated_monthly_km_if_missing": 1000,  # fallback (12k/year)
    # ICE depreciation grid (year -> cumulative depreciation % of original on-road)
    "ice_depr_grid": {
        0.5: 0.05,
        1: 0.10,
        2: 0.18,
        3: 0.25,
        4: 0.30,
        5: 0.35,
        6: 0.40,
        7: 0.45,
        8: 0.50,
    },
    "ice_depr_floor_after_8y": 0.60,
    # mileage sensitivity scaling
    "ice_expected_annual_km": 12000,
    "ice_mileage_penalty_per_1000km_over": 0.006,  # 0.6% extra depreciation per 1k km over expected
    "ice_mileage_bonus_per_1000km_under": 0.004,   # 0.4% bonus per 1k km under expected
    # market blending caps
    "market_weight_age_under_3": 0.7,
    "market_weight_age_3_to_6": 0.6,
    "market_weight_age_over_6": 0.5,
    "negotiation_buffer_default": 0.94,  # final retail multiplier to allow for negotiation
    # regional settings
    "south_multiplier": 1.08,  # smaller than 1.12; tuneable
    "ncr_diesel_panic_age_years": 8.0,
    "ncr_diesel_scrap_age_years": 9.5,
    "ncr_diesel_panic_penalty": 0.25,  # reduce to 75% remaining
    # EV settings
    "ev_degradation_rate_nmc": 0.025,   # 2.5% per year baseline for NMC
    "ev_degradation_rate_lfp": 0.015,   # LFP typically degrades slower
    "ev_high_usage_threshold_km": 20000,
    "ev_high_usage_rate_increase": 0.01, # +1% per year if high usage
    "ev_min_soh": 0.55,  # never assume SoH below this without diagnostics
    "ev_battery_replacement_cost_per_kwh": 30000,  # default ₹/kWh estimate (tune to market)
    "ev_min_market_blend": 0.3,
    # penalties
    "discontinued_penalty": 0.12,
    "new_gen_penalty": 0.07,
    # dealer economics
    "dealer_margin": {"Hatchback": 0.10, "Sedan": 0.12, "SUV": 0.12, "Luxury": 0.15},
    "refurbishment_cost": {
        "ICE": {"Hatchback": 8000, "Sedan": 15000, "SUV": 25000, "Luxury": 60000},
        "EV": {"any": 10000},
    },
    # scrap table default
    "scrap_values": {'Hatchback': 18000, 'Sedan': 30000, 'SUV': 45000, 'Luxury': 60000},
    # databases
    "DISCONTINUED_DB": ['Ford Ecosport', 'Honda Civic', 'VW Polo', 'Maruti Alto 800', 'Renault Duster'],
    "NEW_GEN_DB": ['Maruti Swift', 'Hyundai Creta', 'Tata Nexon', 'Mahindra XUV300'],
}

# ----------------------------------------
# Helper functions
# ----------------------------------------
def parse_date_safe(datestr):
    try:
        return datetime.strptime(datestr, "%Y-%m-%d").date()
    except Exception:
        return None

def age_from_reg_date(reg_date):
    today = date.today()
    reg = parse_date_safe(reg_date)
    if not reg:
        return None, None
    delta_months = (today.year - reg.year) * 12 + (today.month - reg.month)
    age_years = delta_months / 12.0
    return round(age_years, 3), delta_months

def choose_depr_from_grid(age_years):
    grid = CONFIG["ice_depr_grid"]
    # if within a specified breakpoint, return nearest
    keys = sorted(grid.keys())
    for k in keys:
        if age_years <= k:
            return grid[k]
    return CONFIG["ice_depr_floor_after_8y"]

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ----------------------------------------
# Engine: ICE valuation
# ----------------------------------------
def ice_engine(data, metrics, log):
    # Required inputs (with fallbacks)
    current_ex = data.get("current_ex_showroom")
    hist_onroad = data.get("historical_onroad_price")
    age_years = metrics["age_years"]
    avg_annual = metrics["avg_annual_running"]

    # Step A: Estimate historical_onroad if missing (less aggressive than original)
    if hist_onroad is None and current_ex is not None:
        # assume historical_onroad approx current_ex adjusted by a mild inflation factor based on years
        # (If a car is older, its original trim may have been cheaper.)
        hist_onroad = current_ex * (1 - 0.02 * clamp(age_years, 0, 10))
        log.append(f"Estimated historical_onroad_price from current_ex_showroom: {hist_onroad:.0f}")

    if hist_onroad is None:
        raise ValueError("Insufficient price inputs for ICE valuation: historical_onroad or current_ex required.")

    # Step 1: Base depreciation (book value)
    base_depr_pct = choose_depr_from_grid(age_years)
    book_value = hist_onroad * (1 - base_depr_pct)
    log.append(f"Book value after grid depreciation ({base_depr_pct*100:.1f}%): {book_value:.0f}")

    # Step 2: Mileage adjustment (proportional)
    expected = CONFIG["ice_expected_annual_km"]
    km_diff = avg_annual - expected
    if km_diff > 0:
        extra_pct = (km_diff / 1000.0) * CONFIG["ice_mileage_penalty_per_1000km_over"]
        log.append(f"High usage adjustment: +{extra_pct*100:.2f}% due to avg annual {avg_annual} km (expected {expected})")
        book_value *= (1 - extra_pct)
    else:
        bonus_pct = (abs(km_diff) / 1000.0) * CONFIG["ice_mileage_bonus_per_1000km_under"]
        log.append(f"Low usage adjustment: -{bonus_pct*100:.2f}% (value increases) due to avg annual {avg_annual} km")
        book_value *= (1 + bonus_pct)

    # Step 3: Market lifecycle penalties
    mm = f"{data.get('make','').strip()} {data.get('model','').strip()}".strip()
    if mm in CONFIG["DISCONTINUED_DB"]:
        log.append(f"Discontinued model penalty applied: -{CONFIG['discontinued_penalty']*100:.1f}%")
        book_value *= (1 - CONFIG["discontinued_penalty"])
    if mm in CONFIG["NEW_GEN_DB"]:
        log.append(f"Newer generation penalty applied: -{CONFIG['new_gen_penalty']*100:.1f}%")
        book_value *= (1 - CONFIG["new_gen_penalty"])

    # Step 4: Regional legislation (RTO trap)
    city = data.get("city","").lower()
    rto = data.get("rto_code","").upper()
    # NCR Diesel ban logic
    if data.get("fuel_type","").lower() == "diesel" and ("delhi" in city or city.startswith("ncr") or rto.startswith("DL")):
        if age_years >= CONFIG["ncr_diesel_scrap_age_years"]:
            scrap = CONFIG["scrap_values"].get(data.get("body_type","Hatchback"), 18000)
            log.append(f"NCR diesel — older than scrap threshold ({CONFIG['ncr_diesel_scrap_age_years']}y). Set to scrap value: {scrap}")
            return {"fair_market_retail_value": scrap, "reason": "NCR diesel scrap threshold"}
        elif age_years >= CONFIG["ncr_diesel_panic_age_years"]:
            log.append(f"NCR diesel panic penalty applied: -{CONFIG['ncr_diesel_panic_penalty']*100:.1f}% (age {age_years:.2f}y)")
            book_value *= (1 - CONFIG["ncr_diesel_panic_penalty"])

    if rto and rto[:2] in ("KA","TS","TN","KL","AP"):
        log.append(f"South India regional premium applied: x{CONFIG['south_multiplier']}")
        book_value *= CONFIG["south_multiplier"]

    # Step 5: Convergence with market listings
    market_mean = data.get("market_listings_mean")
    if market_mean is not None and market_mean > 0:
        if age_years < 3:
            m_w = CONFIG["market_weight_age_under_3"]
        elif age_years <= 6:
            m_w = CONFIG["market_weight_age_3_to_6"]
        else:
            m_w = CONFIG["market_weight_age_over_6"]
        # Bound market weight based on plausibility (if market diverges too much trust intrinsic more)
        divergence = abs(market_mean - book_value) / (book_value + 1e-6)
        if divergence > 0.35:
            # if market deviates a lot, reduce market influence
            m_w = max(CONFIG["ev_min_market_blend"], m_w - 0.15)
            log.append(f"Market listings diverge {divergence*100:.1f}%, reducing market weight to {m_w:.2f}")
        blended = market_mean * m_w + book_value * (1 - m_w)
        log.append(f"Blended market ({m_w*100:.0f}% market, {100-m_w*100:.0f}% book): {blended:.0f}")
    else:
        blended = book_value
        log.append("No market_listings_mean provided — using book value.")

    # Final negotiation buffer
    retail = blended * CONFIG["negotiation_buffer_default"]
    log.append(f"Negotiation buffer applied: x{CONFIG['negotiation_buffer_default']}. Retail = {retail:.0f}")

    return {"fair_market_retail_value": round(retail), "reason": "ICE computed", "book_value": round(book_value)}

# ----------------------------------------
# Engine: EV valuation
# ----------------------------------------
def ev_engine(data, metrics, log):
    # Inputs
    benchmark_price = data.get("current_benchmark_ev_price")
    benchmark_kwh = data.get("current_benchmark_ev_kwh")
    battery_kwh = data.get("battery_capacity_kwh")
    chemistry = (data.get("battery_chemistry") or "NMC").upper()
    age_years = metrics["age_years"]
    avg_annual = metrics["avg_annual_running"]
    market_mean = data.get("market_listings_mean")

    # Validate necessary fields
    if battery_kwh is None:
        raise ValueError("battery_capacity_kwh required for EV valuation")

    # Step 1: Compute cost-per-kWh anchor (use benchmark if valid, else fall back to configured estimate)
    if benchmark_price and benchmark_kwh:
        cost_per_kwh = benchmark_price / benchmark_kwh
        log.append(f"Derived market cost_per_kWh from benchmark: ₹{cost_per_kwh:.0f}/kWh")
    else:
        cost_per_kwh = CONFIG["ev_battery_replacement_cost_per_kwh"]
        log.append(f"No benchmark provided. Using configured cost_per_kWh estimate: ₹{cost_per_kwh:.0f}/kWh")

    # Adjusted base price = cost of equivalent battery capacity in current market
    adjusted_base_price = cost_per_kwh * battery_kwh
    # Also include a small chassis premium factor so small-battery cars have some car body value
    chassis_premium = 0.12  # 12% onboard for chassis/interior baseline
    adjusted_base_price *= (1 + chassis_premium)
    log.append(f"Adjusted base price (battery+k): {adjusted_base_price:.0f}")

    # Step 2: Battery state-of-health (SoH) estimate
    if chemistry == "LFP":
        annual_deg = CONFIG["ev_degradation_rate_lfp"]
    else:
        annual_deg = CONFIG["ev_degradation_rate_nmc"]
    # increase if high usage
    if avg_annual and avg_annual > CONFIG["ev_high_usage_threshold_km"]:
        annual_deg += CONFIG["ev_high_usage_rate_increase"]
        log.append("High annual km detected; increased battery degradation rate.")

    soh = 1.0 - (annual_deg * clamp(age_years, 0, 20))
    soh = clamp(soh, CONFIG["ev_min_soh"], 1.0)
    log.append(f"Estimated battery SoH after {age_years:.2f} years: {soh*100:.1f}%")

    # Battery running value = proportion of adjusted_base_price
    battery_running_value = adjusted_base_price * soh
    log.append(f"Battery running value (Adjusted_Base * SoH): {battery_running_value:.0f}")

    # Step 3: Replacement risk (warranty cliff)
    # Use proportional replacement cost instead of flat amount.
    expected_replacement_cost = cost_per_kwh * battery_kwh
    # If outside typical warranty window (>7y) or very high odo → add risk reserve equal to portion of replacement cost
    warranty_risk = 0.0
    if age_years >= 7 or (metrics.get("odometer", 0) > 140000):
        # risk reserve = 30% of replacement cost (tunable)
        warranty_risk = 0.30 * expected_replacement_cost
        log.append(f"Warranty cliff: reserving ₹{warranty_risk:.0f} (~30% of replacement cost).")
        battery_running_value -= warranty_risk

    # Step 4: Range/tech penalty (relative)
    # If battery is small relative to modern equivalents, penalize proportionally
    if benchmark_kwh and benchmark_kwh > 0:
        kwh_ratio = battery_kwh / benchmark_kwh
        if kwh_ratio < 0.85:
            penalty_pct = (0.85 - kwh_ratio) * 0.25  # up to ~25% if substantially smaller
            log.append(f"Range/tech penalty: -{penalty_pct*100:.1f}% due to smaller battery vs modern benchmark.")
            battery_running_value *= (1 - penalty_pct)

    # chemistry penalty: NMC slightly worse in calendar fade — but treat gently
    if chemistry == "NMC":
        chem_pen = 0.03
        log.append(f"Chemistry ({chemistry}) penalty applied: -{chem_pen*100:.1f}%")
        battery_running_value *= (1 - chem_pen)

    # Step 5: Add chassis/interior wear reserve (flat %) and ensure not negative
    wear_reserve_pct = 0.10
    battery_running_value *= (1 - wear_reserve_pct)
    battery_running_value = max(battery_running_value, 0.0)
    log.append(f"Applied wear reserve of {wear_reserve_pct*100:.0f}%. Value now {battery_running_value:.0f}")

    # Step 6: Converge with market listings (if available)
    if market_mean and market_mean > 0:
        # If market_mean is far higher than battery_running_value (unrealistic), favor intrinsic more.
        divergence = abs(market_mean - battery_running_value) / (battery_running_value + 1e-6)
        market_weight = 0.5
        if age_years < 3:
            market_weight = 0.6
        if divergence > 0.40:
            market_weight = max(CONFIG["ev_min_market_blend"], market_weight - 0.2)
            log.append(f"Market divergence {divergence*100:.1f}%, reducing market weight to {market_weight:.2f}")
        blended = market_mean * market_weight + battery_running_value * (1 - market_weight)
        log.append(f"Blended EV value (market_weight {market_weight:.2f}): {blended:.0f}")
    else:
        blended = battery_running_value
        log.append("No market_listings_mean for EV — using battery-driven intrinsic value.")

    retail = round(blended)
    return {"fair_market_retail_value": int(retail), "reason": "EV computed", "battery_soh": round(soh,3),
            "cost_per_kwh": round(cost_per_kwh,2), "battery_running_value": round(battery_running_value)}

# ----------------------------------------
# Dealer economics / final wrapper
# ----------------------------------------
def compute_dealer_offer(retail_value, body_type, is_ev=False):
    margin_pct = CONFIG["dealer_margin"].get(body_type, 0.12)
    refurb = CONFIG["refurbishment_cost"]["EV" if is_ev else "ICE"].get(body_type, CONFIG["refurbishment_cost"]["EV"]["any"] if is_ev else 0)
    # Dealer purchase price = retail - margin - refurb
    dealer_offer = retail_value * (1 - margin_pct) - refurb
    dealer_offer = max(dealer_offer, 0)
    return round(dealer_offer), {"margin_pct": margin_pct, "refurbishment": refurb}

# ----------------------------------------
# Main entry
# ----------------------------------------
def value_vehicle(payload):
    log = []
    # Input normalization / validation
    make = payload.get("make", "")
    model = payload.get("model", "")
    fuel = payload.get("fuel_type", "").strip().title()
    reg_date = payload.get("reg_date")
    body_type = payload.get("body_type", "Hatchback")
    odometer = payload.get("odometer")
    owner_count = payload.get("owner_count", 1)
    market_mean = payload.get("market_listings_mean")

    # Age and odometer estimation
    age_years, age_months = age_from_reg_date(reg_date)
    if age_years is None:
        age_years = 0.0
        age_months = 0
        log.append("reg_date missing or invalid; assuming age 0.")
    if odometer is None:
        # fallback estimate
        odometer = int(age_years * CONFIG["default_avg_annual_km"])
        log.append(f"Estimated odometer = {odometer} km (age-based fallback).")

    avg_annual_running = (odometer / max(1.0, max(age_years, 1e-6))) if age_years > 0 else CONFIG["default_avg_annual_km"]
    avg_annual_running = int(round(avg_annual_running))

    metrics = {
        "age_years": age_years,
        "age_months": age_months,
        "odometer": odometer,
        "avg_annual_running": avg_annual_running
    }

    # Decide engine
    if fuel.lower() == "electric":
        engine_used = "EV"
        ev_result = ev_engine(payload, metrics, log)
        fair_value = ev_result["fair_market_retail_value"]
        breakdown = ev_result
        is_ev = True
    else:
        engine_used = "ICE"
        ice_result = ice_engine(payload, metrics, log)
        # if ice_engine returns scrap reason quickly, handle
        if isinstance(ice_result.get("fair_market_retail_value"), (int,float)):
            fair_value = int(ice_result["fair_market_retail_value"])
        else:
            fair_value = int(ice_result.get("fair_market_retail_value"))
        breakdown = ice_result
        is_ev = False

    # Dealer purchase price
    dealer_price, dealer_meta = compute_dealer_offer(fair_value, body_type, is_ev=is_ev)
    log.append(f"Dealer purchase price computed: {dealer_price} (margin {dealer_meta['margin_pct']*100:.0f}%, refurb {dealer_meta['refurbishment']})")

    # Final JSON
    out = {
        "status": "success",
        "engine_used": engine_used,
        "vehicle_metrics": {
            "age_years": age_years,
            "age_months": age_months,
            "estimated_odometer": odometer,
            "avg_annual_running": avg_annual_running,
        },
        "pricing": {
            "fair_market_retail_value": int(fair_value),
            "dealer_purchase_offer": int(dealer_price),
        },
        "breakdown_log": {
            "steps": log,
            "internal_breakdown": breakdown,
            "dealer_meta": dealer_meta
        }
    }
    return out
