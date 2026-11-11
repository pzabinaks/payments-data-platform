#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="payments-data-platform-pz01126"
DATASET="raw"
BUCKET_NAME="gs://payments-data-platform-pz01126-raw"

for FILE_PATH in $(gcloud storage objects list "$BUCKET_NAME/domain/**" --format="value(name)") 
do
     
     if [ -z "$FILE_PATH" ] || [[ "$FILE_PATH" == */ ]]; then
          continue
     fi

     FILE_BASE=$(basename "$FILE_PATH")
     TABLE_NAME="${FILE_BASE%.*}"

   
     echo "Loading $FILE_PATH into table: $DATASET.$TABLE_NAME"

     bq load \
       --source_format=PARQUET \
       --replace \
       "$PROJECT_ID:$DATASET.$TABLE_NAME" \
       "$BUCKET_NAME/$FILE_PATH"

     TOTAL_COUNT=$(bq query \
      --use_legacy_sql=false \
      --format=csv \
      "SELECT COUNT(*) FROM \`$PROJECT_ID.$DATASET.$TABLE_NAME\`" | tail -n +2)   

     echo "$TOTAL_COUNT records loaded for: $DATASET.$TABLE_NAME"
done