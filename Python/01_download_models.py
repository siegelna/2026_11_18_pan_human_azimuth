"""Download Pan-human Azimuth weights from Zenodo record 20401417."""

ZENODO_URLS = {
    "v0": (
        "https://zenodo.org/records/20401417/files/"
        "panhumanpy_inference_model_v0.keras?download=1"
    ),
    "v1": (
        "https://zenodo.org/records/20401417/files/"
        "panhumanpy_inference_model_v1.keras?download=1"
    ),
}


def download_models(paths):
    import requests

    saved = {}
    for version, url in ZENODO_URLS.items():
        dest = paths["models"] / f"panhumanpy_inference_model_{version}.keras"
        if dest.is_file() and dest.stat().st_size > 0:
            saved[version] = dest
            continue
        with requests.get(url, stream=True, timeout=300) as response:
            response.raise_for_status()
            with dest.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1 << 20):
                    if chunk:
                        handle.write(chunk)
        saved[version] = dest
    return saved
