

def _collect_schedule(val):
    res = {p: [val.X[i][p].value() for i in val.N] for p in val.P}
    return pd.DataFrame(res, index=val.N)
