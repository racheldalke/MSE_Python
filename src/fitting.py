from scipy.optimize import minimize
from model import predict_kov
import numpy as np

def get_dataset_split(datasets, experiment):

    regression_sets = [
        datasets[name]
        for name in experiment.get("regression", [])
    ]

    evaluation_sets = [
        datasets[name]
        for name in experiment.get("evaluation", [])
    ]

    return regression_sets, evaluation_sets

def compile_params(fixed, param_names):

    free_names = [n for n in param_names if fixed[n] is None]
    fixed_values = {n: fixed[n] for n in param_names if fixed[n] is not None}

    def unpack(params):

        p = {}
        k = 0

        for name in param_names:
            if name in fixed_values:
                p[name] = fixed_values[name]
            else:
                p[name] = params[k]
                k += 1

        return p

    return unpack, len(free_names)

def least_squares(free_params, datasets, constants, unpack):

    if not isinstance(datasets, (list, tuple)):
        datasets = [datasets]

    params = unpack(free_params)

    total = 0.0

    for df in datasets:
        Kov_pred = predict_kov(params, df, constants)
        Kov_exp = df["Kov_exp"].to_numpy()

        Kov_exp_mean = Kov_exp.mean()
        total += np.sum(((Kov_exp - Kov_pred)/Kov_exp_mean)**2)

    return total

def fit_model(regression_sets, fixed, constants, x0=None):

    param_names = [
        "A",
        "B",
        "alpha",
        "beta"
    ]

    unpack, n_free = compile_params(
        fixed,
        param_names
    )

    if x0 is None:
        x0 = np.ones(n_free)
    else:
        x0 = np.asarray(x0, dtype=float)

        if len(x0) != n_free:
            raise ValueError(
                f"x0 must contain {n_free} values, but got {len(x0)}"
            )
  
    result = minimize(
        least_squares,
        x0,
        args=(
            regression_sets,
            constants,
            unpack
        )
    )

    params = unpack(result.x)
    
    return params, result

def modify_case(base_params, **changes):

    new_case = base_params.copy()

    for key, value in changes.items():
        new_case[key] = value

    return new_case