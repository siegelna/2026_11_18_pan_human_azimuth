"""Summarize label counts and the labels that differ between v0 and v1."""


def summarize_versions(inventory, hierarchies, paths):
    import pandas as pd

    rows = []
    for version, hierarchy in hierarchies.items():
        rows.append(
            {
                "record_type": "unique_labels",
                "model_version": version,
                "label": "all_levels",
                "count": int((inventory["model_version"] == version).sum()),
            }
        )
        for level in hierarchy["levels"]:
            rows.append(
                {
                    "record_type": "head_classes",
                    "model_version": version,
                    "label": f"level_{level['level'] + 1}",
                    "count": len(level["labels"]),
                }
            )
        part = inventory[inventory["model_version"] == version]
        for column, record_type in (
            ("azimuth_broad", "azimuth_broad"),
            ("azimuth_medium", "azimuth_medium"),
            ("azimuth_fine", "azimuth_fine"),
        ):
            counts = part.loc[part[column] != "", column].value_counts()
            for label, count in counts.items():
                rows.append(
                    {
                        "record_type": record_type,
                        "model_version": version,
                        "label": label,
                        "count": int(count),
                    }
                )
    v0 = set(inventory.loc[inventory["model_version"] == "v0", "full_hierarchical_label"])
    v1 = set(inventory.loc[inventory["model_version"] == "v1", "full_hierarchical_label"])
    for label in sorted(v1 - v0):
        rows.append(
            {"record_type": "added_in_v1", "model_version": "v1", "label": label, "count": 1}
        )
    for label in sorted(v0 - v1):
        rows.append(
            {"record_type": "removed_in_v1", "model_version": "v0", "label": label, "count": 1}
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(paths["tables"] / "azimuth_label_summary.tsv", sep="\t", index=False)
    return summary
