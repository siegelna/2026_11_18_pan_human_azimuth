"""Add Cell Ontology ids and names to the label inventory."""


def map_cell_ontology(inventory, hierarchies, paths):
    import pandas as pd

    mapped = []
    for version, hierarchy in hierarchies.items():
        part = inventory[inventory["model_version"] == version].copy()
        ontology = hierarchy["ontology"].drop_duplicates("Annotation_Label")
        lookup = ontology.set_index("Annotation_Label")
        part["cl_id"] = part["final_level_label"].map(lookup["CL_ID"]).fillna("unmapped")
        part["cl_name"] = part["final_level_label"].map(lookup["CL_Label"]).fillna("unmapped")
        mapped.append(part)
    inventory = pd.concat(mapped, ignore_index=True)
    inventory = inventory.sort_values(
        ["model_version", "azimuth_broad", "full_hierarchical_label"]
    ).reset_index(drop=True)
    inventory.to_csv(paths["tables"] / "azimuth_label_inventory.tsv", sep="\t", index=False)
    return inventory
