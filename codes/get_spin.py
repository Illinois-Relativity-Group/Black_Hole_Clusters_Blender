import os
import pandas as pd
import numpy as np

# ========== STEP 1: COMBINE SPIN DATA FILES ==========
def combine_spin_data(data_dir, output_csv):
    # Time range
    start_time = 0
    end_time = 6000
    step = 9.6
    required_times = np.arange(start_time, end_time + step, step)
    output_data = pd.DataFrame({"time": required_times})

    for file_num in range(1, 47):
        file_name = f"stats_AH{file_num}.txt"
        file_path = os.path.join(data_dir, file_name)

        if not os.path.exists(file_path):
            print(f"File {file_name} not found, skipping.")
            continue

        try:
            data = pd.read_csv(file_path, delim_whitespace=True, comment="#", header=None)
            columns = [
                "time", "file", "area", "mass", "irreducible mass", "spin",
                "dimless spin-x", "dimless spin-y", "dimless spin-z", "dimless spin-z-alt",
                "linear mom. |P|", "linear mom. Px", "linear mom. Py", "linear mom. Pz",
                "origin_x", "origin_y", "origin_z", "center_x", "center_y", "center_z"
            ]
            data.columns = columns
            filtered_data = data[["time", "spin", "dimless spin-x", "dimless spin-y", "dimless spin-z"]]

            merged_data = pd.merge(
                output_data[["time"]],
                filtered_data,
                on="time",
                how="left"
            ).fillna(0)

            output_data[f"spin{file_num}"] = merged_data["spin"]
            output_data[f"spinx{file_num}"] = merged_data["dimless spin-x"]
            output_data[f"spiny{file_num}"] = merged_data["dimless spin-y"]
            output_data[f"spinz{file_num}"] = merged_data["dimless spin-z"]

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

    output_data.to_csv(output_csv, index=False)
    print(f"Step 1 complete: Raw spin data saved to {output_csv}")

# ========== STEP 2: FILL ZEROES ==========
def fill_zeros(csv_file, output_file):
    df = pd.read_csv(csv_file)

    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            df[column].replace(0, pd.NA, inplace=True)
            #df[column] = df[column].fillna(method='ffill')
            #df[column] = df[column].fillna(method='bfill')
            #df[column] = df[column].fillna(df[column].mean())
            df[column] = df[column].ffill()
            df[column] = df[column].bfill()
            df[column] = df[column].fillna(df[column].mean())

    df.to_csv(output_file, index=False)
    print(f"Step 2 complete: Zero-filled data saved to {output_file}")

# ========== STEP 3: SET SPINS TO ZERO AFTER MERGER EVENTS ==========
def modify_csv_from_mergers(file_path, merger_file):
    df = pd.read_csv(file_path)

    if 'time' not in df.columns:
        raise ValueError("The CSV file must contain a 'time' column.")

    if not os.path.exists(merger_file):
        raise FileNotFoundError(f"{merger_file} not found.")

    with open(merger_file, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) != 3:
                continue
            idx1, idx2, t = int(parts[0]), int(parts[1]), float(parts[2])

            for idx in [idx1, idx2]:
                col_name = f"spin{idx}"
                if col_name in df.columns:
                    df.loc[df["time"] > t, col_name] = 0
                else:
                    print(f"Warning: Column {col_name} not found in CSV.")

    df.to_csv(file_path, index=False)
    print(f"Step 3 complete: Spins updated based on merger events from {merger_file}")


# ========== MAIN WORKFLOW ==========
if __name__ == "__main__":
    raw_output = "output.csv"
    cleaned_output = "Spin.csv"

    # Step 1: Combine spin data
    combine_spin_data("data_txt", raw_output)

    # Step 2: Fill zero values
    fill_zeros(raw_output, cleaned_output)

    # Step 3: Zero specific spins after a time threshold
    modify_csv_from_mergers(cleaned_output, "merger_events.txt")

