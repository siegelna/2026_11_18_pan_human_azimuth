"""Build one row per hierarchical cell type each model can assign."""


def build_label_inventory(hierarchies, paths):
    import pandas as pd

    rows = []
    for version, hierarchy in hierarchies.items():
        seen = set()
        broad = dict(
            zip(
                hierarchy["postprocessing"]["broad"]["Orig_Label"],
                hierarchy["postprocessing"]["broad"]["Annotate_broad"],
            )
        )
        medium = dict(
            zip(
                hierarchy["postprocessing"]["medium"]["Orig_Label"],
                hierarchy["postprocessing"]["medium"]["Annotate_medium"],
            )
        )
        fine = dict(
            zip(
                hierarchy["postprocessing"]["fine"]["Orig_Label"],
                hierarchy["postprocessing"]["fine"]["Annotate_fine"],
            )
        )
        for level in hierarchy["levels"]:
            for raw_label in level["labels"]:
                parts = raw_label.split("|")
                while parts and parts[-1] == "":
                    parts.pop()
                full_label = "|".join(parts)
                if full_label in seen:
                    continue
                if len(parts) != level["level"] + 1:
                    continue
                seen.add(full_label)
                row = {
                    "model_version": version,
                    "hierarchy_level": level["level"] + 1,
                    "full_hierarchical_label": full_label,
                    "final_level_label": parts[-1],
                }
                for column, lookup in (
                    ("azimuth_broad", broad),
                    ("azimuth_medium", medium),
                    ("azimuth_fine", fine),
                ):
                    value = lookup.get(full_label, "")
                    if not isinstance(value, str) or value == "":
                        prefix = full_label + "|"
                        child_values = []
                        for key, child in lookup.items():
                            if (
                                isinstance(key, str)
                                and key.startswith(prefix)
                                and isinstance(child, str)
                                and child != ""
                                and child not in child_values
                            ):
                                child_values.append(child)
                        value = child_values[0] if len(child_values) == 1 else ""
                    row[column] = value
                for index in range(hierarchy["max_depth"]):
                    row[f"level_{index}"] = parts[index] if index < len(parts) else ""
                rows.append(row)
    columns = (
        ["model_version", "hierarchy_level", "full_hierarchical_label"]
        + [f"level_{index}" for index in range(8)]
        + ["final_level_label", "azimuth_broad", "azimuth_medium", "azimuth_fine"]
    )
    inventory = pd.DataFrame(rows)[columns]
    inventory = inventory.sort_values(
        ["model_version", "azimuth_broad", "full_hierarchical_label"]
    ).reset_index(drop=True)
    inventory.to_csv(paths["tables"] / "azimuth_label_inventory.tsv", sep="\t", index=False)
    return inventory
