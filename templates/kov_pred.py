import sys
import os
import xlwings as xw
import math
from dataclasses import dataclass
import numpy as np

def main():

    workbook_path = sys.argv[1]
    
    app = xw.apps.active
    wb = app.books[os.path.basename(workbook_path)]

    workbook_dir = os.path.dirname(workbook_path)
    
    ws = wb.sheets[0]
    
    conversions = {
        "C2":  lambda x: x * 1e-3,        # cP → kg/(m·s)
        "C3":  lambda x: x * 1e-3,        # cP → kg/(m·s)
        "C4":  lambda x: x * 1000,        # g/cm3 → kg/m3
        "C5":  lambda x: x * 1000,        # g/cm3 → kg/m3
        "C6":  lambda x: x * 1e-4,        # cm2/s → m2/s
        "C7":  lambda x: x * 1e-4,        # cm2/s → m2/s
        "C8":  lambda x: x * 1e-3,        # mm → m
        "C9":  lambda x: x * 1e-6,        # um → m
        "C10": lambda x: x * 1e-6,        # um → m
        "C11": lambda x: x,               # dimensionless
        "C12": lambda x: x * 1e-3,        # mm → m
        "C13": lambda x: x * 1e-6 / 60,   # mL/min → m3/s
        "C14": lambda x: x * 1e-6 / 60,   # mL/min → m3/s
        "C15": lambda x: x,               # dimensionless
        "C16": lambda x: x,               # dimensionless
        "C17": lambda x: x * 1e-6,        # um → m
        "C18": lambda x: x,               # dimensionless
    }

    # ---------------------------
    # calculate conversions
    # ---------------------------
    
    for cell, func in conversions.items():
        raw = ws.range(cell).value
        ws.range(cell).offset(0, 2).value = func(raw)  

    # ---------------------------
    # define experimental parameters
    # ---------------------------
    
    values = ws.range("E2:E18").value
    (mu_a, mu_o, rho_a, rho_o, D_a, D_o, dsi, di, do, n, L, Qa, Qo, epsilon, tau, l, m) = values
    
    A, B, alpha, beta, gamma = ws.range("C20:C24").value 

    # ---------------------------
    # calculations
    # ---------------------------
    
    phi = n * (do / dsi)**2
    a_eff = n * math.pi * do * L # m2
    
    # shell side 
    d_hs = (dsi**2 - n * do**2) / (dsi + n * do)
    a_s = (math.pi / 4) * (dsi**2 - n * do**2)
    v_s = Qa / a_s
    Sc_s = mu_a / (rho_a * D_a)
    Re_s = (rho_a * v_s * d_hs) / mu_a
    Sh_s = A * (1 - phi)**B * (d_hs / L)**alpha * (Re_s**beta) * (Sc_s**gamma)
    ks = Sh_s * D_a / d_hs
    R_s = m / ks
    
    # lumen side
    d_hl = di
    a_l = (math.pi * di**2 / 4) * n
    v_l = Qo / a_l
    Sc_l = mu_o / (rho_o * D_o)
    Re_l = (rho_o * v_l * di) / mu_o
    
    Gz = Sc_l * Re_l * (di / L)
    
    if Gz > 6:
        Sh_l = 1.62 * (Sc_l**(1/3)) * (Re_l**(1/3)) * (di / L)**(1/3)
    elif Gz < 6:
        Sh_l = 0.5 * Sc_l * Re_l * (di / L)
    
    kl = Sh_l * D_o / di
    R_l = do / (di * kl)
    
    # membrane
    d_ln = (do - di) / math.log(do / di)
    chi = epsilon / tau
    km = (epsilon * D_o) / (tau * l)
    R_m = do / (d_ln * km)
    
    # overall
    Kov_model = 1 / (R_l + R_m + R_s) 
    R_ov = 1 / Kov_model

    # ---------------------------
    # send results back to excel
    # ---------------------------
    
    ws.range("C28").options(transpose=True).value = [phi, d_hs, a_s, v_s, Sc_s, Re_s, Sh_s, ks, R_s]
    ws.range("C38").options(transpose=True).value = [d_hl, a_l, v_l, Sc_l, Re_l, Gz, Sh_l, kl, R_l]
    ws.range("C48").options(transpose=True).value = [d_ln, chi, km, R_m]
    ws.range("C53").options(transpose=True).value = [Kov_model, R_ov]

    wb.save()

# ---------------------------
# error logging wrapper
# ---------------------------

if __name__ == "__main__":
    try:
        main()
        print("Finished successfully.")
    
    except Exception as e:
    
        workbook_path = sys.argv[1] if len(sys.argv) > 1 else ""
        workbook_dir = os.path.dirname(workbook_path) if workbook_path else os.getcwd()
        error_path = os.path.join(workbook_dir, "kov_pred_error.txt")
    
        with open(error_path, "w") as f:
            import traceback
            f.write("ERROR:\n")
            f.write(str(e) + "\n\n")
            f.write(traceback.format_exc())
        
        raise