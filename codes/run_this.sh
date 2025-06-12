#!/bin/bash


# Set this to your root directory
ROOT_DIR="/Users/lyn/Documents/research/BH_N25_Case2/6_10"
OUTPUT_DIR="$ROOT_DIR/Output"
SPIN_DIR="$ROOT_DIR/Spin"
generate_spin=y

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

#---------------Size & Position---------------#
# Run the Python script
rm -f merger_events.txt
python find_BH_mergers.py "$ROOT_DIR"

# Define input and output files
INPUT1="BH_N25_all_BHs_punctures.dat"
INPUT2="BH_N25_merger_info.dat"

# Convert .dat to .csv 
cut -d' ' -f2- "$INPUT1" | tr -s ' ' ',' | sed 's/^,//;s/,$//' > "$OUTPUT_DIR/Position.csv"
cut -d' ' -f2- "$INPUT2" | tr -s ' ' ',' | sed 's/^,//;s/,$//' > "$OUTPUT_DIR/Size.csv"


echo "Convert to csv files. Files saved in $OUTPUT_DIR"

#---------------Spin---------------#
if [ ${generate_spin} == y ]; then

    #SOURCE_DIR="$SPIN_DIR/AH_data"
    #DEST_DIR="$SPIN_DIR/data_txt"
    SOURCE_DIR="AH_data"
    DEST_DIR="data_txt"

    mkdir -p "$DEST_DIR"

    for file in "$SOURCE_DIR"/*.dat; do
        if [[ -f "$file" ]]; then
            filename=$(basename "$file" .dat)
            cp "$file" "$DEST_DIR/$filename.txt"
        fi
    done

    #cd $SPIN_DIR
    python get_spin.py
    #cd -
    mv Spin.csv "$OUTPUT_DIR"

fi
#rm -f merger_events.txt
echo "All .dat files have been copied and renamed to .txt in $DEST_DIR"


