"""Check Zenodo md5 sums for the downloaded Pan-human Azimuth weights."""

EXPECTED_MD5 = {
    "v0": "767643b3e6cd65c24f64fbd355c13f27",
    "v1": "e640b6031aa9a7ff7499df724f4abee0",
}


def verify_checksums(paths):
    import hashlib

    import pandas as pd

    rows = []
    for version, expected in EXPECTED_MD5.items():
        model_path = paths["models"] / f"panhumanpy_inference_model_{version}.keras"
        digest = hashlib.md5(model_path.read_bytes()).hexdigest()
        rows.append(
            {
                "model_version": version,
                "path": str(model_path),
                "expected_md5": expected,
                "observed_md5": digest,
                "match": digest == expected,
            }
        )
    return pd.DataFrame(rows)
