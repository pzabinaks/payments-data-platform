#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="payments-data-platform-pz01126"
DATASET="raw"
BUCKET_NAME="gs://payments-data-platform-pz01126-raw"


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd "${SCRIPT_DIR}/../data/raw" && pwd)"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Error: Source directory '$SOURCE_DIR' does not exist." >&2
  exit 1
fi

# Collect local .parquet files to verify before uploading
mapfile -d '' PARQUET_FILES < <(find "$SOURCE_DIR" -type f -name "*.parquet" -print0 | sort -z)

if [[ ${#PARQUET_FILES[@]} -eq 0 ]]; then
  echo "No .parquet files found in '$SOURCE_DIR'."
  exit 0
fi

echo "Uploading ${#PARQUET_FILES[@]} Parquet file(s) from ${SOURCE_DIR} to ${BUCKET_NAME}/..."

gcloud storage cp --recursive "${SOURCE_DIR}/"* "${BUCKET_NAME}/"

echo ""
echo "Copied files (${#PARQUET_FILES[@]}):"
for file in "${PARQUET_FILES[@]}"; do
  rel_path="${file#"$SOURCE_DIR"/}"
  echo " - ${BUCKET_NAME}/${rel_path}"
done