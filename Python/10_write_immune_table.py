"""Save the immune-cell rows of the label inventory as their own table."""


def write_immune_table(paths):
    import pandas as pd

    inventory = pd.read_csv(paths["tables"] / "azimuth_label_inventory.tsv", sep="\t")
    immune = inventory.loc[inventory["azimuth_broad"].eq("Immune cell")]
    immune = immune.sort_values(
        ["model_version", "azimuth_medium", "full_hierarchical_label"]
    ).reset_index(drop=True)
    immune.to_csv(paths["tables"] / "azimuth_immune_cell_table.tsv", sep="\t", index=False)
    return immune
