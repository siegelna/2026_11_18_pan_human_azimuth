"""List the hierarchical softmax heads stored in each Zenodo model."""


def list_model_outputs(paths):
    import os
    import re

    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
    import pandas as pd

    stderr_fd = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    try:
        from tensorflow.keras.models import load_model
    finally:
        os.dup2(stderr_fd, 2)
        os.close(devnull)
        os.close(stderr_fd)

    rows = []
    for version in ("v0", "v1"):
        model_path = paths["models"] / f"panhumanpy_inference_model_{version}.keras"
        stderr_fd = os.dup(2)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 2)
        try:
            model = load_model(model_path, compile=False)
        finally:
            os.dup2(stderr_fd, 2)
            os.close(devnull)
            os.close(stderr_fd)
        for layer in model.layers:
            if not re.fullmatch(r"L\d+_out", layer.name):
                continue
            units = getattr(layer, "units", None)
            if units is None:
                shape = layer.output_shape
                if isinstance(shape, list):
                    shape = shape[0]
                units = int(shape[-1])
            rows.append(
                {
                    "model_version": version,
                    "output_name": layer.name,
                    "level_number": int(re.search(r"\d+", layer.name).group(0)),
                    "units": int(units),
                }
            )
        del model
    return (
        pd.DataFrame(rows)
        .sort_values(["model_version", "level_number"])
        .reset_index(drop=True)
    )
