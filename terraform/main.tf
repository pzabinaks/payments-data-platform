terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# 1. Access variables inside a provider block
provider "google" {
  project = var.project_id
  region  = var.region
}

# 2. Create a Cloud Storage Bucket
resource "google_storage_bucket" "my_bucket" {
  name          =  ${var.project_id}-raw             # Globally unique bucket name
  location      =  ${var.location}                   # Multi-region or single region (e.g., US-CENTRAL1)
  storage_class = "STANDARD"

  # Force delete of bucket and contents
  force_destroy = true

  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true
}

# 2. Grant Read Rights using an IAM Member resource
resource "google_storage_bucket_iam_member" "pdp_loader_read" {

  bucket = google_storage_bucket.${var.project_id}-raw

  role   = "roles/storage.objectViewer"

  member = "serviceAccount:${google_service_account.pdp_loader.email}"
}


# Create a BigQuery Dataset for raw data
resource "google_bigquery_dataset" "minimal_dataset_raw" {
  dataset_id = ${var.project_id}-ds-raw 
  delete_contents_on_destroy = true
}

# Create a BigQuery Dataset for raw data
resource "google_bigquery_dataset" "minimal_dataset_staging" {
  dataset_id = ${var.project_id}-ds-staging 
  delete_contents_on_destroy = true
}

# Create a BigQuery Dataset for raw data
resource "google_bigquery_dataset" "minimal_dataset_marts" {
  dataset_id = ${var.project_id}-ds-marts 
  delete_contents_on_destroy = true
}