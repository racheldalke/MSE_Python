conversion_dict = {
    "C2":  lambda x: x * 1e-3,        # cP → kg/(m·s)
    "C3":  lambda x: x * 1e-3,        # cP → kg/(m·s)
    "C4":  lambda x: x * 1000,        # g/cm3 → kg/m3
    "C5":  lambda x: x * 1000,        # g/cm3 → kg/m3
    "C6":  lambda x: x * 1e-4,        # cm2/s → m2/s
    "C7":  lambda x: x * 1e-4,        # cm2/s → m2/s
    "C8":  lambda x: x * 1e-3,        # mm → m
    "C9":  lambda x: x * 1e-6,        # um → m
    "C10": lambda x: x * 1e-6,        # um → m
    "C11": lambda x: x * 1e-3,        # mm → m
    "C12": lambda x: x,               # dimensionless
    "C13": lambda x: x,               # dimensionless
    "C14": lambda x: x * 1e-6,        # um → m
}
