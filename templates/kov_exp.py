import os
import sys
import xlwings as xw
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def main():

        workbook_path = sys.argv[1]

        workbook_dir = os.path.dirname(workbook_path)

        output_path = os.path.join(workbook_dir, "fit_plot.png")
        error_path = os.path.join(workbook_dir, "kov_error.txt")

        app = xw.apps.active
        wb = app.books[os.path.basename(workbook_path)] 
        datasheet = wb.sheets[0]

        # ---------------------------
        # read in data
        # ---------------------------

        exp_data = datasheet.range("A1:E14").options(
                pd.DataFrame,
                header=1,
                index=False
                ).value

        data_table = exp_data.copy()

        m = datasheet.range("D16").value
        active_area_cm2 = datasheet.range("D19").value
        rho_organic = datasheet.range("D20").value
        rho_aqueous = datasheet.range("D21").value

        active_area_m2 = active_area_cm2 / 10000

        data_table["driving_force_gm3"] = m * data_table["conc_bulk_aq_gm3"].to_numpy() - data_table["conc_bulk_org_gm3"].to_numpy()

        data_table["conc_bulk_org_gg"] = data_table["conc_bulk_org_gm3"] / (797.222 * 1000)
        data_table["conc_bulk_aq_gg"] = data_table["conc_bulk_aq_gm3"] / (998 * 1000)

        data_table["system_mass_g"] = data_table["system_vol_mL"] * (797.222 / 1000) # g

        t = data_table["time_hr"].to_numpy()
        conc_bulk_org_arr = data_table["conc_bulk_org_gg"].to_numpy()
        conc_bulk_aq_arr = data_table["conc_bulk_aq_gg"].to_numpy()
        sys_mass_arr = data_table["system_mass_g"].to_numpy()
        driving_force = data_table["driving_force_gm3"].to_numpy()
        
        # ---------------------------
        # model
        # ---------------------------

        def model(t, Cinf, C0, k):
                return Cinf + (C0 - Cinf) * np.exp(-k * t)

        popt, pcov = curve_fit(model, t, conc_bulk_org_arr, maxfev=10000)

        Cinf, C0, k = popt

        b = C0 - Cinf
        c = -k
        d = Cinf

        C_model = model(t, Cinf, C0, k)

        data_table["C_model_gg"] = C_model

        dCdt = -k * (C_model - Cinf)

        data_table["dCdt_gg_per_h"] = dCdt
        data_table["J_g_m2_h"] = (sys_mass_arr / active_area_m2) * dCdt

        J_exp = data_table["J_g_m2_h"].to_numpy()

        def flux_model(x, K):
                return K * x

        Kov_exp, _ = curve_fit(flux_model, driving_force, J_exp)
        Kov_exp = Kov_exp[0] / 3600

        # write parameters back to Excel
        vals = [Kov_exp, b, c, d]
        datasheet.range("D23").options(transpose=True).value = vals

        cols_to_write = [
        "driving_force_gm3",
        "conc_bulk_org_gg",
        "conc_bulk_aq_gg",
        "system_mass_g",
        "C_model_gg",
        "dCdt_gg_per_h",
        "J_g_m2_h"
        ]

        output = [cols_to_write] + data_table[cols_to_write].values.tolist()
        datasheet.range("F1").value = output
        
        # ---------------------------
        # make plots
        # ---------------------------

        t_fit = np.linspace(np.min(t), np.max(t), 200)
        c_fit = model(t_fit, Cinf, C0, k)

        fig, ax = plt.subplots(1, 2, figsize=(10, 4))

        # raw data
        ax[0].plot(t, conc_bulk_org_arr, "o-", label="phi=20%")
        ax[0].set_xlabel("Time (h)")
        ax[0].set_ylabel("Concentration in organic phase (g/g)")
        ax[0].set_ylim(0, 0.0125)
        ax[0].set_yticks(np.arange(0, 0.0125 + 0.0025, 0.0025))
        ax[0].legend(loc="upper left")
        ax[0].grid(axis="y", linestyle="-", color="lightgray", alpha=0.7)

        # fit
        ax[1].plot(
            t_fit, c_fit,
            label="model fit",
            linestyle="--",
            color="orange"
        )
        ax[1].scatter(t, conc_bulk_org_arr, label="exp. data")
        ax[1].set_xlabel("Time (h)")
        ax[1].set_ylabel("Concentration in organic phase (g/g)")
        ax[1].set_ylim(0, 0.0125)
        ax[1].set_yticks(np.arange(0, 0.0125 + 0.0025, 0.0025))
        ax[1].legend(loc="upper left")
        ax[1].grid(axis="y", linestyle="-", color="lightgray", alpha=0.7)

        # ---------------------------
        # save plot
        # ---------------------------

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()

        wb.save() # wb.close()

        print("DONE")

# ---------------------------
# error logging wrapper
# ---------------------------

if __name__ == "__main__":
    try:
        main()
    except Exception as e:

        # fallback if workbook_path missing
        workbook_path = sys.argv[1] if len(sys.argv) > 1 else ""
        workbook_dir = os.path.dirname(workbook_path) if workbook_path else os.getcwd()
        error_path = os.path.join(workbook_dir, "kov_error.txt")

        with open(error_path, "w") as f:
            import traceback
            f.write("ERROR:\n")
            f.write(str(e) + "\n\n")
            f.write(traceback.format_exc())

        raise