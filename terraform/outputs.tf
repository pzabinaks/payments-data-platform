output "gcs_bucket_name" {
  value       = google_storage_bucket.my_bucket
  description = "The globally unique name of the created Cloud Storage bucket."
}

output "bigquery_dataset_raw" {
  value       = google_bigquery_dataset.raw.dataset_id
  description = "The unique ID of the created BigQuery dataset"
}


output "bigquery_dataset_staging" {
  value       = google_bigquery_dataset.staging.dataset_id
  description = "The unique ID of the created BigQuery dataset"
}

output "bigquery_dataset_marts" {
  value       = google_bigquery_dataset.marts.dataset_id
  description = "The unique ID of the created BigQuery dataset"
}