
import streamlit as st

# Intervention data
interventions = [
    {"name": "Smoking cessation", "arr_lifetime": 17, "arr_5yr": 5},
    {"name": "Statin (atorvastatin 80 mg)", "arr_lifetime": 9, "arr_5yr": 3},
    {"name": "Ezetimibe", "arr_lifetime": 2, "arr_5yr": 1},
    {"name": "PCSK9 inhibitor", "arr_lifetime": 5, "arr_5yr": 2},
    {"name": "Antiplatelet (ASA or clopidogrel)", "arr_lifetime": 6, "arr_5yr": 2},
    {"name": "BP control (ACEi/ARB ± CCB)", "arr_lifetime": 12, "arr_5yr": 4},
    {"name": "Semaglutide 2.4 mg", "arr_lifetime": 4, "arr_5yr": 1},
    {"name": "Weight loss to ideal BMI", "arr_lifetime": 10, "arr_5yr": 3},
    {"name": "Empagliflozin", "arr_lifetime": 6, "arr_5yr": 2},
    {"name": "Icosapent ethyl (TG ≥1.5)", "arr_lifetime": 5, "arr_5yr": 2},
    {"name": "Mediterranean diet", "arr_lifetime": 9, "arr_5yr": 3},
    {"name": "Physical activity", "arr_lifetime": 9, "arr_5yr": 3},
    {"name": "Alcohol moderation", "arr_lifetime": 5, "arr_5yr": 2},
    {"name": "Stress reduction", "arr_lifetime": 3, "arr_5yr": 1}
]

def scale_arr_by_age(base_arr, age):
    if age <= 50:
        return base_arr * 1.1
    elif age <= 60:
        return base_arr * 1.0
    elif age <= 70:
        return base_arr * 0.8
    else:
        return base_arr * 0.6

def calculate_arr(selected, age, ldl_current=None, ldl_target=None,
                  hba1c_current=None, hba1c_target=None,
                  sbp_current=None, sbp_target=None,
                  horizon="lifetime"):
    remaining_risk = 100.0
    cumulative_arr = 0.0

    for i, selected_flag in enumerate(selected):
        if selected_flag:
            base_arr = interventions[i][f"arr_{horizon}"]
            adj_arr = scale_arr_by_age(base_arr, age)
            reduced = remaining_risk * (adj_arr / 100)
            cumulative_arr += reduced
            remaining_risk -= reduced

    if ldl_current is not None and ldl_target is not None:
        ldl_drop = max(ldl_current - ldl_target, 0)
        ldl_rrr = 22 * ldl_drop
        ldl_arr = remaining_risk * (ldl_rrr / 100)
        cumulative_arr += ldl_arr
        remaining_risk -= ldl_arr

    if hba1c_current is not None and hba1c_target is not None:
        hba1c_drop = max(hba1c_current - hba1c_target, 0)
        hba1c_rrr = 14 * hba1c_drop
        hba1c_arr = remaining_risk * (hba1c_rrr / 100)
        cumulative_arr += hba1c_arr
        remaining_risk -= hba1c_arr

    if sbp_current is not None and sbp_target is not None:
        sbp_drop = max(sbp_current - sbp_target, 0)
        sbp_rrr = 20 * (sbp_drop / 10)
        sbp_arr = remaining_risk * (sbp_rrr / 100)
        cumulative_arr += sbp_arr
        remaining_risk -= sbp_arr

    return round(cumulative_arr, 1), round(remaining_risk, 1)

# Streamlit UI
st.title("CVD Risk Reduction Estimator")

age = st.slider("Age", 30, 90, 60)
horizon = st.radio("Select time horizon", ["5yr", "lifetime"], index=1)

ldl_current = st.number_input("Current LDL-C (mmol/L)", min_value=0.5, max_value=6.0, value=2.5, step=0.1)
ldl_target = st.number_input("Target LDL-C (mmol/L)", min_value=0.5, max_value=6.0, value=1.4, step=0.1)
hba1c_current = st.number_input("Current HbA1c (%)", min_value=4.5, max_value=12.0, value=8.0, step=0.1)
hba1c_target = st.number_input("Target HbA1c (%)", min_value=4.5, max_value=12.0, value=7.0, step=0.1)
sbp_current = st.number_input("Current SBP (mmHg)", min_value=80, max_value=220, value=145, step=1)
sbp_target = st.number_input("Target SBP (mmHg)", min_value=80, max_value=220, value=120, step=1)

st.markdown("### Select Interventions")
selection = [st.checkbox(intervention["name"], value=False) for intervention in interventions]

if st.button("Calculate Risk Reduction"):
    cumulative, remaining = calculate_arr(selection, age,
                                          ldl_current=ldl_current, ldl_target=ldl_target,
                                          hba1c_current=hba1c_current, hba1c_target=hba1c_target,
                                          sbp_current=sbp_current, sbp_target=sbp_target,
                                          horizon=horizon)
    st.success(f"Estimated Cumulative ARR ({horizon}): {cumulative}%")
    st.info(f"Estimated Remaining CVD Risk: {remaining}%")
