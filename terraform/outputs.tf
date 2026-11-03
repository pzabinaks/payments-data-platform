output "gcs_bucket_name" {
  value       = google_storage_bucket.my_bucket.name
  description = "The globally unique name of the created Cloud Storage bucket."
}

output "bigquery_dataset_id" {
  value       = google_bigquery_dataset.minimal_dataset.dataset_id
  description = "The unique ID of the created BigQuery dataset."
}