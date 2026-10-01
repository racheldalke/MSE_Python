import numpy as np
import math
import pandas as pd

def calculate_kvals(params, df, constants):

    A = params["A"]
    B = params["B"]
    alpha = params["alpha"]
    beta = params["beta"]

    mu_a = constants["mu_a"]
    mu_o = constants["mu_o"]
    rho_a = constants["rho_a"]
    rho_o = constants["rho_o"]
    D_a = constants["D_a"]
    D_o = constants["D_o"]
    d_si = constants["d_si"]
    d_i = constants["d_i"]
    d_o = constants["d_o"]
    L = constants["L"]
    epsilon = constants["epsilon"]
    tau = constants["tau"]
    l = constants["l"]

    Q_a = df["Q_a_m3s"].to_numpy()
    Q_o = df["Q_o_m3s"].to_numpy()
    NF = df["NF"].to_numpy()
    m = df["m"].to_numpy()

    # geometry
    phi = NF * (d_o / d_si)**2

    d_hs = (d_si**2 - NF * d_o**2) / (d_si + NF * d_o)
    a_s = (np.pi / 4) * (d_si**2 - NF * d_o**2)

    v_s = Q_a / a_s
    v_l = Q_o / (np.pi * d_i**2 / 4 * NF)

    # shell side
    Sc_s = mu_a / (rho_a * D_a)
    Re_s = (rho_a * v_s * d_hs) / mu_a

    Sh_s = A * (1 - phi)**B * (d_hs / L)**alpha * (Re_s**beta) * (Sc_s**0.33) 

    ks = Sh_s * D_a / d_hs
    R_s = m / ks

    # lumen side
    Sc_l = mu_o / (rho_o * D_o)
    Re_l = (rho_o * v_l * d_i) / mu_o

    Gz = Sc_l * Re_l * (d_i / L)

    Sh_l = np.where(
        Gz > 6,
        1.62 * Sc_l**(1/3) * Re_l**(1/3) * (d_i / L)**(1/3),
        0.5 * Sc_l * Re_l * (d_i / L)
    )

    kl = Sh_l * D_o / d_i
    R_l = d_o / (d_i * kl)

    # membrane
    dln = (d_o - d_i) / np.log(d_o / d_i)
    km = (epsilon * D_o) / (tau * l)
    R_m = d_o / (dln * km)

    Kov = 1 / (R_s + R_l + R_m)

    return {
        "Kov": Kov,
        "ks": ks,
        "kl": kl,
        "km": km,
        "phi": phi,
        "d_hs": d_hs,
        "Re_s": Re_s,
        "Sh_s": Sh_s,
        "Re_l": Re_l,
        "Sh_l": Sh_l,
        "R_s": R_s,
        "R_l": R_l,
        "R_m": R_m,
    }

def predict_kov(params, df, constants):
    return calculate_kvals(params, df, constants)["Kov"]