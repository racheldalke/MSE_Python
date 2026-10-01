from model import predict_kov
import numpy as np

def evaluate_model(params, evaluation_sets, constants):

    all_results = []

    total_ss_res = 0.0
    total_ss_tot = 0.0

    for i, dataset in enumerate(evaluation_sets):

        dataset = dataset.copy()

        dataset["Kov_pred"] = predict_kov(params, dataset, constants)

        Kov_exp = dataset["Kov_exp"].to_numpy()
        Kov_pred = dataset["Kov_pred"].to_numpy()
        
        ss_res = np.sum((Kov_exp - Kov_pred)**2)
        ss_tot = np.sum((Kov_exp - np.mean(Kov_exp))**2)

        r2 = 1 - ss_res / ss_tot

        total_ss_res += ss_res
        total_ss_tot += ss_tot

        all_results.append(dataset)

    r2 = 1 - total_ss_res / total_ss_tot

    return r2, all_results

def diagnose_model(params, datasets, constants):

    all_results = []

    total_error = 0.0
    total_ss_res = 0.0
    total_ss_tot = 0.0
    
    for df in datasets:

        results = calculate_kvals(params, df, constants)

        Kov_pred = results["Kov"]
        Kov_exp = df["Kov_exp"].to_numpy()
    
        relative_error = np.abs((Kov_pred - Kov_exp) / Kov_exp) * 100
        SSE = (Kov_exp - Kov_pred) ** 2
        SST = (Kov_exp - Kov_exp.mean()) ** 2
        norm_global_E = ((Kov_exp - Kov_pred) / Kov_exp.mean()) ** 2
        minimized_error = np.sum(norm_global_E)
        
        sumSSE = np.sum(SSE)
        sumSST = np.sum(SST)
        
        r2 = 1 - (sumSSE/sumSST)

        total_error += minimized_error
        total_ss_res += sumSSE
        total_ss_tot += sumSST
    
        output_table = pd.DataFrame({
            "Ks, m/s": results["ks"],
            "km, m/s": results["km"],
            "kl, m/s": results["kl"],
            "1/Kov, pred": 1 / Kov_pred,
            "Kov_pred": Kov_pred,
            "Kov_exp": Kov_exp,
            "Rel_E": relative_error,
            "Kov_pred (scaled)": Kov_pred*1000000,
            "Kov_exp (scaled)": Kov_exp*1000000,
            "SSE": SSE,
            "SST": SST,
            "Normalized Global E2": norm_global_E
        })

        all_results.append({
            "r2": r2,
            "error": minimized_error,
            "table": output_table
            })
    
        pd.set_option("display.float_format", lambda x: f"{x:.3e}")
        
        combined_r2 = 1 - (total_ss_res / total_ss_tot)
        combined_error = total_error

    return {
        "datasets": all_results,
        "combined_r2": combined_r2,
        "combined_error": combined_error
        }