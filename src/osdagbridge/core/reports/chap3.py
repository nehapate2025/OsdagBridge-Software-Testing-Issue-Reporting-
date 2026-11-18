# =============================================================================
# Chapter 3: Loads and Load Combinations
# Extracted from report_generator.py — DO NOT add business logic here.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_BL_IRC_CLASS_SV,
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_ECCENTRICITY,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from .table_utils import make_repeated_header

def ch3_loads(input_dict):
    def _is_checked(val):
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        return str(val).strip().lower() in ("true", "yes", "1", "checked", "selected")

    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    # ── Live Load: Vehicle Definitions & Selection ───────────────────────────
    standard_vehicle_defs = [
        {
            "key": KEY_LL_IRC_CLASS_A,
            "name": "Class A",
            "category": "Standard Wheeled Vehicle (IRC 6 Cl. 204.1)",
            "summary": "8 axles; Train load: 554.0 kN (approx. 56.5 t); Spacing: 18.5 m",
            "fn": IRC6_2017.cl_204_1_ClassA_vehicle,
        },
        {
            "key": KEY_LL_IRC_70R_WHEELED,
            "name": "Class 70R (Wheeled)",
            "category": "Heavy Wheeled Vehicle (IRC 6 Cl. 204.1)",
            "summary": "7 axles; Total load: 981.0 kN (100 t); Spacing: 30.0 m; Kerb clearance: 1.2 m",
            "fn": IRC6_2017.cl_204_1_Class70R_vehicle_wheel,
        },
        {
            "key": KEY_LL_IRC_70R_TRACKED,
            "name": "Class 70R (Tracked)",
            "category": "Heavy Tracked Vehicle (IRC 6 Cl. 204.1)",
            "summary": "2 tracks; Total load: 700.0 kN (70 t); Contact length: 4.57 m; Spacing: 90.0 m",
            "fn": IRC6_2017.cl_204_1_Class70R_vehicle_track,
        },
        {
            "key": KEY_LL_IRC_AA_WHEELED,
            "name": "Class AA (Wheeled)",
            "category": "Heavy Wheeled Vehicle (IRC 6 Cl. 204.1)",
            "summary": "2 axles; Total load: 400.0 kN (40 t); Spacing: 1.2 m",
            "fn": None,
        },
        {
            "key": KEY_LL_IRC_AA_TRACKED,
            "name": "Class AA (Tracked)",
            "category": "Heavy Tracked Vehicle (IRC 6 Cl. 204.1)",
            "summary": "2 tracks; Total load: 700.0 kN (70 t); Track contact length: 3.6 m",
            "fn": None,
        },
        {
            "key": KEY_LL_IRC_70R_BOGIE,
            "name": "Class 70R (Bogie)",
            "category": "Heavy Bogie Axle Vehicle (IRC 6 Cl. 204.1)",
            "summary": "2 bogie axles; Total load: 400.0 kN (40 t); Spacing: 1.37 m",
            "fn": None,
        },
        {
            "key": KEY_LL_IRC_CLASS_SV,
            "name": "Class SV",
            "category": "Special Vehicle / Hydraulic Trailer (IRC 6 Cl. 204.5)",
            "summary": "23 axles (1 steering + 2 bogie + 20 trailer); Total load: 3776.85 kN (385.0 t)",
            "fn": IRC6_2017.cl_204_5_1_special_vehicle,
        },
        {
            "key": KEY_LL_IRC_CLASS_FATIGUE,
            "name": "Class Fatigue",
            "category": "Fatigue Vehicle (IRC 6 Cl. 204.6 / Annex G)",
            "summary": "3 axles (12 t, 14 t, 14 t); Total load: 392.4 kN (40 t); 10,000,000 cycles",
            "fn": IRC6_2017.cl_204_6_fatigue_load,
        },
    ]

    selected_standards = []
    for sdef in standard_vehicle_defs:
        if _is_checked(input_dict.get(sdef["key"])):
            summary = sdef["summary"]
            if sdef["fn"]:
                try:
                    res = sdef["fn"]()
                    if sdef["name"] == "Class A" and "wheel_loads" in res:
                        tot = sum(res["wheel_loads"]) / 1000.0
                        sp = res.get("spacing_ClassA", 18.5)
                        summary = f"8 axles; Train load: {tot:.1f} kN; Spacing: {sp:.1f} m"
                    elif sdef["name"] == "Class 70R (Wheeled)" and "wheel_loads" in res:
                        tot = sum(res["wheel_loads"]) / 1000.0
                        sp = res.get("spacing_Class70R", 30.0)
                        cl = res.get("min_clearance", 1.2)
                        summary = f"7 axles; Total load: {tot:.1f} kN (100 t); Spacing: {sp:.1f} m; Kerb clearance: {cl:.1f} m"
                    elif sdef["name"] == "Class 70R (Tracked)" and "wheel_loads_udl" in res:
                        sp = res.get("spacing_Class70R(T)", 90.0)
                        summary = f"2 tracks; Total load: 700.0 kN (70 t); Contact length: 4.57 m; Spacing: {sp:.1f} m"
                    elif sdef["name"] == "Class SV" and "total_load_kN" in res:
                        tot = res.get("total_load_kN")
                        tot_t = res.get("total_load_tonne", 385.0)
                        summary = f"23 axles (1 steering + 2 bogie + 20 trailer); Total load: {tot:.2f} kN ({tot_t:.1f} t)"
                    elif sdef["name"] == "Class Fatigue" and "wheel_loads" in res:
                        cyc = res.get("fatigue_cycles", 10000000)
                        summary = f"3 axles (12 t, 14 t, 14 t); Total load: 392.4 kN (40 t); Design cycles: {cyc:,}"
                except Exception:
                    pass
            selected_standards.append({
                "name": sdef["name"],
                "category": sdef["category"],
                "summary": summary,
            })

    custom_raw = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    selected_customs = []
    if custom_raw and isinstance(custom_raw, list):
        for c in custom_raw:
            if isinstance(c, dict):
                c_name = str(c.get("name", "")).strip() or "Custom Vehicle"
                c_type = str(c.get("vehicle_type", "Wheeled")).strip()
                axles = c.get("axles") or []
                axle_loads = c.get("axle_loads") or [a.get("load_kN") for a in axles if isinstance(a, dict) and "load_kN" in a]
                axle_spacings = c.get("axle_spacings") or [a.get("spacing_m") for a in axles if isinstance(a, dict) and "spacing_m" in a]

                details_list = [f"Category: Custom Vehicle ({c_type})"]
                if axle_loads:
                    details_list.append(f"{len(axle_loads)} axles (Loads: {', '.join(str(l) for l in axle_loads)} kN)")
                if axle_spacings:
                    details_list.append(f"Spacings: {', '.join(str(s) for s in axle_spacings)} m")
                if c.get("minimum_nose_to_tail_distance_m") not in (None, ""):
                    details_list.append(f"Min Spacing: {c.get('minimum_nose_to_tail_distance_m')} m")
                if c.get("wheel_width_mm") not in (None, ""):
                    details_list.append(f"Wheel Width: {c.get('wheel_width_mm')} mm")
                if c.get("wheel_spacing_transverse_m") not in (None, ""):
                    details_list.append(f"Transverse Spacing: {c.get('wheel_spacing_transverse_m')} m")
                if c.get("impact_factor") not in (None, ""):
                    details_list.append(f"Impact Factor: {c.get('impact_factor')}")

                selected_customs.append({
                    "name": f"Custom: {c_name}",
                    "category": f"Custom Vehicle ({c_type})",
                    "summary": "; ".join(details_list),
                    "raw": c,
                })
            elif isinstance(c, str) and c.strip():
                selected_customs.append({
                    "name": f"Custom: {c.strip()}",
                    "category": "Custom Vehicle",
                    "summary": "Custom Vehicle per User Definition",
                    "raw": {},
                })

    all_selected = selected_standards + selected_customs

    # ── Impact Factor Calculation (IRC 6) ────────────────────────────────────
    span = input_dict.get(KEY_SPAN)
    impact_factor_str = ""
    if span not in (None, ""):
        try:
            span_m = float(span)
            factors = []
            if _is_checked(input_dict.get(KEY_LL_IRC_CLASS_A)):
                im_a = IRC6_2017.cl_208_2_impact_factor(span_m)
                factors.append(f"Class A: {1.0 + im_a:.3f}")
            is_wheeled_heavy = (
                _is_checked(input_dict.get(KEY_LL_IRC_70R_WHEELED)) or 
                _is_checked(input_dict.get(KEY_LL_IRC_AA_WHEELED)) or 
                _is_checked(input_dict.get(KEY_LL_IRC_70R_BOGIE))
            )
            is_tracked_heavy = (
                _is_checked(input_dict.get(KEY_LL_IRC_70R_TRACKED)) or 
                _is_checked(input_dict.get(KEY_LL_IRC_AA_TRACKED))
            )
            if is_wheeled_heavy or is_tracked_heavy:
                im_aa = IRC6_2017.cl_208_3_impact_factor(span_m)
                factors.append(f"Class AA/70R: {1.0 + im_aa:.3f}")

            for cv in selected_customs:
                c_im = cv.get("raw", {}).get("impact_factor")
                if c_im not in (None, ""):
                    try:
                        factors.append(f"{cv['name']}: {float(c_im):.3f}")
                    except ValueError:
                        factors.append(f"{cv['name']}: {c_im}")

            if factors:
                impact_factor_str = ", ".join(factors)
            else:
                impact_factor_str = "N/A"
        except Exception:
            impact_factor_str = "N/A"
    else:
        impact_factor_str = "N/A"

    # ── Braking Force Calculation (IRC 6 Cl. 211.2) ───────────────────────────
    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    braking_force_str = ""
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
            try:
                braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int)
            except UnboundLocalError:
                wheel_load = IRC6_2017.cl_204_1_ClassA_vehicle()['wheel_loads']
                wl_sum = sum(wheel_load)
                w_tonnes = wl_sum / 9810.0 if wl_sum > 1000 else wl_sum
                braking_force_t = 0.20 * w_tonnes
            braking_force_kN = braking_force_t * 9.81
            braking_force_str = f"{braking_force_kN:.2f} kN ({braking_force_t:.2f} tonnes)"
        except Exception:
            braking_force_str = "N/A"
    else:
        braking_force_str = "N/A"

    ecc = input_dict.get(KEY_LL_ECCENTRICITY)
    if ecc not in (None, ""):
        try:
            ecc_str = f"{float(ecc):.2f} m (above deck level)"
        except ValueError:
            ecc_str = f"{ecc} m (above deck level)"
    else:
        ecc_str = "1.20 m (IRC 6 default above deck level)"

    # Build Vehicle Live Loads rows
    if len(all_selected) == 0:
        vll_rows = (
            r"\textnormal{Selected Vehicle Classes} & None Selected \\[6pt]" + "\n"
            + r"\hline" + "\n"
            + r"\textnormal{Vehicle Category} & N/A \\[6pt]" + "\n"
            + r"\hline" + "\n"
            + r"\textnormal{Impact Factor (IRC 6)} & N/A \\[6pt]" + "\n"
            + r"\hline" + "\n"
            + r"\textnormal{Braking Load (IRC 6)} & " + _tex(braking_force_str) + r" \\[6pt]" + "\n"
            + r"\hline" + "\n"
            + r"\textnormal{Braking Load Eccentricity} & " + _tex(ecc_str) + r" \\[6pt]" + "\n"
            + r"\hline"
        )
    elif len(all_selected) == 1:
        v = all_selected[0]
        if v in selected_customs:
            c_raw = v.get("raw", {})
            c_detail_rows = [
                r"\textnormal{Selected Vehicle Class} & " + _tex(v["name"]) + r" \\[6pt]" + "\n" + r"\hline",
                r"\textnormal{Vehicle Category} & " + _tex(v["category"]) + r" \\[6pt]" + "\n" + r"\hline",
            ]
            axle_loads = c_raw.get("axle_loads") or [a.get("load_kN") for a in (c_raw.get("axles") or []) if isinstance(a, dict) and "load_kN" in a]
            axle_spacings = c_raw.get("axle_spacings") or [a.get("spacing_m") for a in (c_raw.get("axles") or []) if isinstance(a, dict) and "spacing_m" in a]
            if axle_loads:
                c_detail_rows.append(r"\textnormal{Number of Axles} & " + str(len(axle_loads)) + r" \\[6pt]" + "\n" + r"\hline")
                c_detail_rows.append(r"\textnormal{Axle Loads} & " + _tex(", ".join(f"{float(x):.1f} kN" for x in axle_loads)) + r" \\[6pt]" + "\n" + r"\hline")
            if axle_spacings:
                c_detail_rows.append(r"\textnormal{Axle Spacings} & " + _tex(", ".join(f"{float(x):.2f} m" for x in axle_spacings)) + r" \\[6pt]" + "\n" + r"\hline")
            if c_raw.get("minimum_nose_to_tail_distance_m") not in (None, ""):
                c_detail_rows.append(r"\textnormal{Min. Nose-to-Tail Spacing} & " + _tex(f"{float(c_raw['minimum_nose_to_tail_distance_m']):.2f} m") + r" \\[6pt]" + "\n" + r"\hline")
            if c_raw.get("wheel_width_mm") not in (None, ""):
                c_detail_rows.append(r"\textnormal{Wheel Width} & " + _tex(f"{float(c_raw['wheel_width_mm']):.1f} mm") + r" \\[6pt]" + "\n" + r"\hline")
            if c_raw.get("wheel_spacing_transverse_m") not in (None, ""):
                c_detail_rows.append(r"\textnormal{Transverse Wheel Spacing} & " + _tex(f"{float(c_raw['wheel_spacing_transverse_m']):.2f} m") + r" \\[6pt]" + "\n" + r"\hline")
            if c_raw.get("minimum_clearance_carriageway_edge_mm") not in (None, ""):
                c_detail_rows.append(r"\textnormal{Clearance to Kerb Edge} & " + _tex(f"{float(c_raw['minimum_clearance_carriageway_edge_mm']):.1f} mm") + r" \\[6pt]" + "\n" + r"\hline")
            if c_raw.get("minimum_clearance_crossing_vehicles_mm") not in (None, ""):
                c_detail_rows.append(r"\textnormal{Clearance to Crossing Vehicles} & " + _tex(f"{float(c_raw['minimum_clearance_crossing_vehicles_mm']):.1f} mm") + r" \\[6pt]" + "\n" + r"\hline")
            c_detail_rows.append(r"\textnormal{Impact Factor (IRC 6)} & " + _tex(impact_factor_str) + r" \\[6pt]" + "\n" + r"\hline")
            c_detail_rows.append(r"\textnormal{Braking Load (IRC 6)} & " + _tex(braking_force_str) + r" \\[6pt]" + "\n" + r"\hline")
            c_detail_rows.append(r"\textnormal{Braking Load Eccentricity} & " + _tex(ecc_str) + r" \\[6pt]" + "\n" + r"\hline")
            vll_rows = "\n".join(c_detail_rows)
        else:
            std_rows = [
                r"\textnormal{Selected Vehicle Class} & " + _tex(v["name"]) + r" \\[6pt]" + "\n" + r"\hline",
                r"\textnormal{Vehicle Category} & " + _tex(v["category"]) + r" \\[6pt]" + "\n" + r"\hline",
                r"\textnormal{Configuration \& Loading} & " + _tex(v["summary"]) + r" \\[6pt]" + "\n" + r"\hline",
                r"\textnormal{Impact Factor (IRC 6)} & " + _tex(impact_factor_str) + r" \\[6pt]" + "\n" + r"\hline",
                r"\textnormal{Braking Load (IRC 6)} & " + _tex(braking_force_str) + r" \\[6pt]" + "\n" + r"\hline",
                r"\textnormal{Braking Load Eccentricity} & " + _tex(ecc_str) + r" \\[6pt]" + "\n" + r"\hline",
            ]
            if v["name"] == "Class SV":
                sv_bl = "Included per Cl. 211.2" if _is_checked(input_dict.get(KEY_BL_IRC_CLASS_SV, True)) else "Excluded"
                std_rows.append(r"\textnormal{Class SV Braking Force} & " + _tex(sv_bl) + r" \\[6pt]" + "\n" + r"\hline")
            vll_rows = "\n".join(std_rows)
    else:
        multi_rows = [
            r"\textnormal{Selected Vehicle Classes} & " + _tex(", ".join(v["name"] for v in all_selected)) + r" \\[6pt]" + "\n" + r"\hline"
        ]
        for v in all_selected:
            multi_rows.append(
                r"\textnormal{Vehicle: " + _tex(v["name"]) + r"} & " + _tex(v["category"] + " --- " + v["summary"]) + r" \\[6pt]" + "\n" + r"\hline"
            )
        multi_rows.append(r"\textnormal{Impact Factor (IRC 6)} & " + _tex(impact_factor_str) + r" \\[6pt]" + "\n" + r"\hline")
        multi_rows.append(r"\textnormal{Braking Load (IRC 6)} & " + _tex(braking_force_str) + r" \\[6pt]" + "\n" + r"\hline")
        multi_rows.append(r"\textnormal{Braking Load Eccentricity} & " + _tex(ecc_str) + r" \\[6pt]" + "\n" + r"\hline")
        if any(v["name"] == "Class SV" for v in all_selected):
            sv_bl = "Included per Cl. 211.2" if _is_checked(input_dict.get(KEY_BL_IRC_CLASS_SV, True)) else "Excluded"
            multi_rows.append(r"\textnormal{Class SV Braking Force} & " + _tex(sv_bl) + r" \\[6pt]" + "\n" + r"\hline")
        vll_rows = "\n".join(multi_rows)

    # ── Footway Live Load Calculation ─────────────────────────────────────────
    fp_mode = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE)
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE)

    if fp_mode is not None and str(fp_mode).strip():
        mode_cleaned = str(fp_mode).strip()
        mode_lower = mode_cleaned.lower()
        if mode_lower in ("as per irc 6", "as per irc6", "automatic", "auto"):
            fp_mode_str = "As per IRC 6"
            fp_method = "Automatically determined per IRC 6"
            fp_ref = "IRC:6-2017 Clause 206.1"
            try:
                auto_val = IRC6_2017.cl_206_1_footway_load()
                fp_val_str = f"{auto_val:.3f} kN/m\\textsuperscript{{2}}"
            except Exception:
                fp_val_str = "N/A"
        elif mode_lower in ("custom", "user-defined", "manual"):
            fp_mode_str = "Custom"
            fp_method = "Manually entered by user"
            fp_ref = "User Specification"
            if fp_value not in (None, ""):
                try:
                    fp_val_str = f"{float(fp_value):.3f} kN/m\\textsuperscript{{2}}"
                except ValueError:
                    fp_val_str = f"{fp_value} kN/m\\textsuperscript{{2}}"
            else:
                fp_val_str = "N/A"
        else:
            fp_mode_str = mode_cleaned
            if fp_value not in (None, ""):
                try:
                    fp_val_str = f"{float(fp_value):.3f} kN/m\\textsuperscript{{2}}"
                except ValueError:
                    fp_val_str = f"{fp_value} kN/m\\textsuperscript{{2}}"
                fp_method = "Manually entered by user"
            else:
                fp_val_str = "N/A"
                fp_method = "N/A"
            fp_ref = "---"
    elif fp_value not in (None, ""):
        fp_mode_str = "Custom"
        fp_method = "Manually entered by user"
        fp_ref = "User Specification"
        try:
            fp_val_str = f"{float(fp_value):.3f} kN/m\\textsuperscript{{2}}"
        except ValueError:
            fp_val_str = f"{fp_value} kN/m\\textsuperscript{{2}}"
    else:
        fp_mode_str = "N/A"
        fp_method = "N/A"
        fp_ref = "---"
        fp_val_str = "N/A"

    fp_width = input_dict.get(KEY_TS_FOOTPATH_WIDTH)
    if fp_width not in (None, ""):
        fp_width_row = r"\textnormal{Footpath Width} & " + (_render_value(input_dict, KEY_TS_FOOTPATH_WIDTH, ' m')) + r""" (IRC 5 Cl. 104.3.6) \\[6pt]
\hline
"""
    else:
        fp_width_row = ""

    # Vz / Pz — prefer stored computed values; fall back to IRC6 Table 12
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb  = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h   = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m²" if pz_val not in (None, "") else "N/A"

    # Table 3.5 — Seismic: prefer stored computed values; fall back to IRC6 cl_218_5_1
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral    = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah          = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av          = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z    = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st   = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp   = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res  = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral    = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah          = _res.get("Ah")
            if not sl_av:
                sl_av          = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _sl(v, unit=""):
        return f"{float(v):.4f}{unit}" if v not in (None, "") else "N/A"

    # Table 3.6 — Temperature: compute effective bridge temp range from shade temps
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP)  or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res    = IRC6_2017.cl_215_2_effective_bridge_temperature(
                          float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean   = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise     = f"{_bt_max - _mean:.2f}"
            tl_fall     = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # --- Table 3.7: Load Combinations (dynamically generated from IRC 6) ---
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        """Format a factors dict into a compact load-case string for the table."""
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):  # permanent load with adding/relieving
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue  # skip N/A factors
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"ULS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"SLS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )

    lc_rows_str = "\n".join(lc_rows)

    hdr_param_val = r"\textbf{parameter} & \textbf{value} \\[6pt]"
    hdr_31 = make_repeated_header(hdr_param_val, 2, r"\textbf{Dead Load -- Self Weight}")
    hdr_32 = make_repeated_header(hdr_param_val, 2, r"\textbf{Dead Load for Surfacing (DW)}")
    hdr_33 = make_repeated_header(hdr_param_val, 2, r"\textbf{Vehicle Live Loads}")
    hdr_34_fp = make_repeated_header(hdr_param_val, 2, r"\textbf{Footway Live Loads}")
    hdr_34 = make_repeated_header(hdr_param_val, 2, r"\textbf{Wind Load (WL) --- per IRC 6}")
    hdr_35 = make_repeated_header(hdr_param_val, 2, r"\textbf{Earthquake Load (EL) --- per IRC 6}")
    hdr_36 = make_repeated_header(hdr_param_val, 2, r"\textbf{Temperature Load (TL) --- per IRC 6}")
    hdr_37 = make_repeated_header(r"\textbf{Combination ID} & \textbf{Load Cases} \\[6pt]", 2, r"\textbf{Load Combinations}")

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + hdr_31 + r"""
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + hdr_32 + r"""
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[6pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[6pt]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + hdr_33 + r"""
""" + vll_rows + r"""
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + hdr_34_fp + r"""
\textnormal{Footway Loading Mode} & """ + _tex(fp_mode_str) + r""" \\[6pt]
\hline
\textnormal{Determination Method} & """ + _tex(fp_method) + r""" \\[6pt]
\hline
\textnormal{Footway Live Load} & """ + fp_val_str + r""" \\[6pt]
\hline
\textnormal{Applicable Reference} & """ + _tex(fp_ref) + r""" \\[6pt]
\hline
""" + fp_width_row + r"""\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + hdr_34 + r"""
\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[6pt]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\[6pt]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\[6pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + hdr_35 + r"""
\textnormal{Seismic Zone} & """ + (_render_value(input_dict,'seismic_zone')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (longitudinal)} & """ + '' + r""" kN \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (transverse)} & """ + '' + r""" kN \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + hdr_36 + r"""
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_max')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_min')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|C{4.0cm}|p{11.5cm}|}
""" + hdr_37 + r"""
""" + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""


