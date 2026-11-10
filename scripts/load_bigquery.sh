set -euo pipefail

PROJECT_ID="payments-data-platform-pz01126"
DATASET="raw"
BUCKET_NAME="gs://payments-data-platform-pz01126-raw"

gcloud storage objects list "$BUCKET_NAME/domain/**" --format="value(name)" | while read -r FILE_PATH;  do
     
     if [ -z "$FILE_PATH" ] || [[ "$FILE_PATH" == */ ]]; then
          continue
     fi

     FILE_BASE=$(basename "$FILE_PATH")
     TABLE_NAME="${FILE_BASE%.*}"

   
     echo "Loading $FILE_PATH into table: $DATASET.$TABLE_NAME"

     bq load \
       --source_format=PARQUET \
       --replace \
       --autodetect \
       "$PROJECT_ID:$DATASET.$TABLE_NAME" \
       "$BUCKET_NAME/$FILE_PATH"

     TOTAL_COUNT=$(bq query \
      --use_legacy_sql=false \
      'SELECT COUNT(*) FROM `payments-data-platform-pz01126.$TABLE_NAME`' | tail -n +2)   

     echo "$TOTAL_COUNT records loaded for: $DATASET.$TABLE_NAME"
done