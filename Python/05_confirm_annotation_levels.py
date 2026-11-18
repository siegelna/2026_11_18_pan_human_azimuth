"""Confirm each softmax head matches the label encoder at that level."""


def confirm_annotation_levels(model_outputs, hierarchies):
    import pandas as pd

    rows = []
    for version, hierarchy in hierarchies.items():
        heads = model_outputs[model_outputs["model_version"] == version]
        rows.append(
            {
                "model_version": version,
                "check": "eight_hierarchy_levels",
                "expected": 8,
                "observed": hierarchy["max_depth"],
                "passed": hierarchy["max_depth"] == 8 and len(hierarchy["levels"]) == 8,
            }
        )
        rows.append(
            {
                "model_version": version,
                "check": "softmax_head_count",
                "expected": hierarchy["max_depth"],
                "observed": int(len(heads)),
                "passed": len(heads) == hierarchy["max_depth"],
            }
        )
        for level in hierarchy["levels"]:
            level_number = level["level"] + 1
            head = heads[heads["level_number"] == level_number]
            units = int(head["units"].iloc[0]) if len(head) else None
            n_labels = len(level["labels"])
            rows.append(
                {
                    "model_version": version,
                    "check": f"L{level_number}_out_matches_encoder",
                    "expected": n_labels,
                    "observed": units,
                    "passed": units == n_labels,
                }
            )
        for name, column in (
            ("broad", "Annotate_broad"),
            ("medium", "Annotate_medium"),
            ("fine", "Annotate_fine"),
        ):
            present = column in hierarchy["postprocessing"][name].columns
            rows.append(
                {
                    "model_version": version,
                    "check": f"azimuth_{name}",
                    "expected": column,
                    "observed": column if present else "missing",
                    "passed": present,
                }
            )
        required = {"Annotation_Label", "CL_Label", "CL_ID"}
        missing = required.difference(hierarchy["ontology"].columns)
        rows.append(
            {
                "model_version": version,
                "check": "cell_ontology_map",
                "expected": "Annotation_Label, CL_Label, CL_ID",
                "observed": "present" if not missing else "missing " + ", ".join(sorted(missing)),
                "passed": not missing,
            }
        )
    return pd.DataFrame(rows)
