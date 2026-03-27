import zipfile
import os


def zip_files(list_of_files: list[str]) -> str:
    with zipfile.ZipFile("output.zip", mode="w") as zipf:
        for file in list_of_files:
            zipf.write(file)

def unzip_files(zip_file: str, extraction_path: str) -> list[str]:
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extraction_path)

zip_files(["data/clientes.csv", "data/contratos.csv", "data/leituras.csv"])
# unzip_files("output.zip", "data_output")