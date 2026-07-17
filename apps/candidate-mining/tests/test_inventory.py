from candidate_mining.inventory import sha256_file


def test_sha256_file_is_stable(tmp_path) -> None:
    source = tmp_path / "sample.bin"
    source.write_bytes(b"vsf")

    assert sha256_file(source) == "02cdc5daeafbc4ddc3eb948c1ee8bc6c874e326e6795be8849a24f9b4d97c700"
