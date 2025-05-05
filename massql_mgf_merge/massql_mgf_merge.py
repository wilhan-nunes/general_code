import glob
import os
from urllib.parse import quote

import pandas as pd
import requests
from tqdm import tqdm


def download_task_zip(task_id, output_dir="./downloaded_content"):
    """
    Download the task zip file from a task id.
    :param task_id: Task ID for the GNPS2 job.
    :param output_dir: Directory to save the downloaded file.
    :return: None
    """
    from tqdm import tqdm

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{task_id}.tar")
    if os.path.exists(file_path):
        print(f"File {file_path} already exists. Skipping download.")
        return

    url = "https://gnps2.org/taskzip?task=" + task_id
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get("content-length", 0))
        print(f"Starting download for task {task_id}...")
        with open(file_path, "wb") as f, tqdm(
            desc=f"Downloading {task_id}.tar",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress_bar.update(len(chunk))
        print(f"Task {task_id} downloaded successfully.")
    else:
        print(f"Error: {response.status_code}")


def extract_results(tar_file, subfolder):
    """
    Extract the contents of a specific subfolder from a tar file.
    :param tar_file: Path to the tar file.
    :param subfolder: Subfolder to extract from the tar file.
    """
    import tarfile
    import os

    print(f"Extracting results from {tar_file}...")
    with tarfile.open(tar_file, "r") as tar_ref:
        # Filter members belonging to the specified subfolder
        members = [m for m in tar_ref.getmembers() if m.name.startswith(subfolder)]
        if not members:
            print(f"No contents found for subfolder: {subfolder}")
            return

        # Extract only the filtered members
        extract_path = os.path.splitext(tar_file)[0]
        tar_ref.extractall(path=extract_path, members=members)
        print(
            f"Extracted contents of subfolder '{subfolder}' successfully to '{extract_path}'."
        )


def download_tsv_summary(task, output_dir="./downloaded_content"):
    """
    Download the TSV summary file generated for a given MassQL task.
    :param task: GNPS2 MassQL job task ID.
    :param output_dir: Directory to save the downloaded TSV file.
    :return:
    """
    print(f"Downloading TSV summary for task {task}...")
    os.makedirs(output_dir, exist_ok=True)
    url = f"https://gnps2.org/resultfile?task={task}&file={quote('nf_output/extracted/extracted.tsv')}"
    response = requests.get(url)
    response.raise_for_status()
    if response.status_code == 200:
        file_path = os.path.join(output_dir, f"extracted_{task}.tsv")
        open(file_path, "wb").write(response.content)
        print(f"Task {task} TSV summary downloaded successfully.")
        return file_path
    else:
        print(f"Error: {response.status_code}")
        return None


def insert_mgf_info(task: str, name: str, tsv_file_path: str, base_folder: str = "./downloaded_content"):
    """
    Insert MGF info into the MGF files based on the TSV summary.
    :param task: task ID for the GNPS2 job. This will be used to construct the MGF file path associated with the task.
    :param name:
    :param tsv_file_path: TSV file generated during the MASSQL job. This file contains the information needed to insert the metadata into the MGF files.
    :param base_folder: Folder under which the MGF files are stored. This is usually the same folder where the task zip file was downloaded and extracted.
    :return: None
    """
    print(f"Inserting MGF info for task {task}...")
    df = pd.read_csv(tsv_file_path, sep="\t")
    files_to_process = df["new_filename"].unique()
    for file in tqdm(files_to_process, desc="Processing MGF files"):
        subset = df[df["new_filename"] == file]
        mgf_file_path = os.path.join(base_folder, task, "nf_output", "extracted", "extracted_mgf", f"{file.split('.')[0]}.mgf")
        output_mgf_file_path = os.path.join(base_folder, task, f"processed_{file.split('.')[0]}.mgf")

        with open(mgf_file_path, "r") as f, open(output_mgf_file_path, "w") as out_f:
            for line in f:
                if line.startswith("SCANS"):
                    scan_number = line.split("=")[1].strip()
                    row = subset[subset["new_scan"] == int(scan_number)].iloc[0]
                    insert_string = (
                        f"MASSQL_ORIGIN={name}\n"
                        f"MASSQL_PEPMASS={row.precmz}\n"
                        f"MASSQL_ORIGINAL_PATH={row.original_path}\n"
                        f"MASSQL_SCAN={row.scan}\n"
                        f"MASSQL_NEW_SCAN={row.new_scan}\n"
                        f"MASSQL_NEW_FILENAME={row.new_filename}\n"
                        f"MASSQL_I={row.i}\n"
                    )
                    out_f.write(insert_string)
                out_f.write(line)

        print(f"Processed {mgf_file_path}")


def concatenate_mgf_files(input_folder, output_file):
    """
    Concatenate all .mgf files in subfolders of the input folder into a single .mgf file.
    :param input_folder: The folder containing the .mgf files to concatenate.
    :param output_file: The output file path for the concatenated .mgf file.
    :return: None
    """
    print(f"Concatenating .mgf files from {input_folder} into {output_file}...")
    with open(output_file, "w") as outfile:
        all_files = glob.glob(f"{input_folder}/**/*.mgf", recursive=True)
        processed_files = [f for f in all_files if "processed" in f]
        for mgf_file in processed_files:
            print(f"Adding {mgf_file} to {output_file}...")
            with open(mgf_file, "r") as infile:
                outfile.write(infile.read())
                outfile.write("\n")  # Ensure separation between files
    print(f"Concatenation complete. Output written to {output_file}.")


def renumber_mgf_file(input_mgf, output_mgf):
    """
    Renumber the SCANS in the input MGF file and save to output MGF file.
    :param input_mgf: Path to the input MGF file.
    :param output_mgf: Path to the output renumbered MGF file.
    :return: None
    """
    print(f"Renumbering SCANS in {input_mgf} and saving to {output_mgf}...")
    with open(input_mgf, "r") as infile, open(output_mgf, "w") as outfile:
        scan_number = 1
        for line in infile:
            if line.startswith("SCANS"):
                line = f"SCANS={scan_number}\n"
                scan_number += 1
            outfile.write(line)
    print(f"Renumbering complete. Output written to {output_mgf}.")


if __name__ == "__main__":
    print("Starting GNPS2 task processing...")

    # Example task IDs and names, change this to yor names and task IDs
    tasks = {
        "name_1": "2e50af7f1cfc42r391a5fe2eb7b06de7",
        "name_2": "9980bbf19ae54657b2d3d881475745fe",
        "name_3": "1a998a6fa2c2475195f0111039c09515",
    }

    # Folder to store downloaded content
    output_dir = "./downloaded_content"

    for name, task in tasks.items():
        print(f"Downloading task files: {name} ({task})")
        download_task_zip(task, output_dir=output_dir)

    for name, task in tqdm(tasks.items(), desc="Processing tasks"):
        print(f"Processing task: {name} ({task})")
        extract_results(
            f"./downloaded_content/{task}.tar",
            subfolder="nf_output/extracted/extracted_mgf",
        )

        # optional cleanup step, uncomment the lines below to remove the tar file after extraction
        # os.remove(f"./downloaded_content/{task}.tar")
        # print(f"Removed {task}.tar")

        tsv_file_path = download_tsv_summary(task, output_dir=output_dir)

        insert_mgf_info(task, name, tsv_file_path, base_folder=output_dir)

        os.makedirs("./final_mgf", exist_ok=True)
        concatenate_mgf_files(
            "./downloaded_content", "./final_mgf/all_concatenated.mgf"
        )
        renumber_mgf_file(
            "./final_mgf/all_concatenated.mgf",
            "./final_mgf/renumbered_all_concatenated.mgf",
        )

    print("All tasks processed successfully.")
