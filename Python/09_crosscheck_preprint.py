"""Compare model label counts with the Pan-human Azimuth preprint."""

PREPRINT_URL = "https://www.biorxiv.org/content/10.64898/2026.07.16.738997v1.full.pdf"
PREPRINT_NAME = "2026.07.16.738997v1.full.pdf"


def crosscheck_preprint(inventory, hierarchies, model_outputs, paths):
    import re

    import pandas as pd
    import requests
    from pypdf import PdfReader

    pdf_path = paths["paper"] / PREPRINT_NAME
    if not pdf_path.is_file():
        with requests.get(PREPRINT_URL, stream=True, timeout=300) as response:
            response.raise_for_status()
            with pdf_path.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1 << 20):
                    if chunk:
                        handle.write(chunk)
    reader = PdfReader(str(pdf_path))
    text = re.sub(r"\s+", " ", "\n".join((page.extract_text() or "") for page in reader.pages))
    head_counts = {
        int(level): int(count)
        for level, count in re.findall(
            r"Level (\d) classification head \((\d+) classes\)", text
        )
    }
    softmax_counts = {
        int(level): int(count)
        for level, count in re.findall(r"L(\d)_out Dense \(softmax\) (\d+)", text)
    }
    preprint_counts = head_counts or softmax_counts
    rows = []
    depth_mentioned = "eight levels" in text.lower()
    rows.append(
        {
            "claim": "hierarchy_levels",
            "preprint_value": "8" if depth_mentioned else "",
            "v0_value": hierarchies["v0"]["max_depth"],
            "v1_value": hierarchies["v1"]["max_depth"],
            "v0_match": depth_mentioned and hierarchies["v0"]["max_depth"] == 8,
            "v1_match": depth_mentioned and hierarchies["v1"]["max_depth"] == 8,
            "note": "Preprint: annotations at eight levels of resolution.",
        }
    )
    for level_number in range(1, 9):
        preprint_value = preprint_counts.get(level_number)
        v0_encoder = len(hierarchies["v0"]["levels"][level_number - 1]["labels"])
        v1_encoder = len(hierarchies["v1"]["levels"][level_number - 1]["labels"])
        v0_units = model_outputs.loc[
            (model_outputs["model_version"] == "v0")
            & (model_outputs["level_number"] == level_number),
            "units",
        ]
        v1_units = model_outputs.loc[
            (model_outputs["model_version"] == "v1")
            & (model_outputs["level_number"] == level_number),
            "units",
        ]
        v0_units = int(v0_units.iloc[0]) if len(v0_units) else None
        v1_units = int(v1_units.iloc[0]) if len(v1_units) else None
        rows.append(
            {
                "claim": f"level_{level_number}_classes",
                "preprint_value": preprint_value,
                "v0_value": v0_encoder,
                "v1_value": v1_encoder,
                "v0_match": preprint_value == v0_encoder == v0_units,
                "v1_match": preprint_value == v1_encoder == v1_units,
                "note": "Preprint architecture table versus encoder size and L*_out units.",
            }
        )
    tissue_match = re.search(r"(\d+) tissues", text)
    organs = sorted(hierarchies["v1"]["ontology"]["Organ_Level"].dropna().unique())
    rows.append(
        {
            "claim": "training_tissues",
            "preprint_value": tissue_match.group(1) if tissue_match else "",
            "v0_value": "",
            "v1_value": ", ".join(organs),
            "v0_match": False,
            "v1_match": False,
            "note": (
                "23 tissues describes the training corpus. "
                "The released Cell Ontology map is organism-wide and uses Organ_Level only."
            ),
        }
    )
    n_v1 = int((inventory["model_version"] == "v1").sum())
    rows.append(
        {
            "claim": "unique_hierarchical_labels",
            "preprint_value": "",
            "v0_value": int((inventory["model_version"] == "v0").sum()),
            "v1_value": n_v1,
            "v0_match": False,
            "v1_match": False,
            "note": (
                "Not a single preprint total. Head sizes count padded coarser labels "
                "again at deeper levels; this row is the count of distinct hierarchy nodes."
            ),
        }
    )
    crosscheck = pd.DataFrame(rows)
    crosscheck.to_csv(paths["tables"] / "preprint_crosscheck.tsv", sep="\t", index=False)
    return crosscheck
