"""Load label encoders, refinement tables, and the Cell Ontology map."""


def load_label_hierarchy():
    import importlib
    import pickle

    import pandas as pd
    from importlib.resources import files

    hierarchies = {}
    for version in ("v0", "v1"):
        version_module = importlib.import_module(f"panhumanpy._tools.{version}")
        version_path = files(version_module)
        encoder_path = version_path / "inference_encoders" / "inference_encoders.pkl"
        with encoder_path.open("rb") as handle:
            encoders = pickle.load(handle)
        levels = []
        for index, encoder in enumerate(encoders):
            levels.append(
                {
                    "level": index,
                    "labels": [str(label) for label in encoder.classes_],
                }
            )
        postprocessing = {}
        for name in ("broad", "medium", "fine"):
            csv_path = version_path / "postprocessing" / f"panhuman_annotate_{name}.csv"
            with csv_path.open("rb") as handle:
                postprocessing[name] = pd.read_csv(handle)
        ontology_path = version_path / "cell_ontology_map" / "cell_ontology_map.csv"
        with ontology_path.open("rb") as handle:
            ontology = pd.read_csv(handle)
        hierarchies[version] = {
            "version": version,
            "max_depth": int(version_module.model_meta["max_depth"]),
            "levels": levels,
            "postprocessing": postprocessing,
            "ontology": ontology,
        }
    return hierarchies
