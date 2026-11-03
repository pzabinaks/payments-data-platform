terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.0"
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
  name          = "${var.project_id}-raw" # Globally unique bucket name
  location      = var.location            # Multi-region or single region (e.g., US-CENTRAL1)
  storage_class = "STANDARD"

  # Force delete of bucket and contents
  force_destroy = true

  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true
}

# 3. Grant Read Rights using an IAM Member resource
resource "google_storage_bucket_iam_member" "pdp_loader_read" {

  bucket = google_storage_bucket.my_bucket.name

  role = "roles/storage.objectViewer"

  member = "serviceAccount:${var.loader_sa_email}"
}


# Create a BigQuery Dataset for raw data
resource "google_bigquery_dataset" "raw" {
  dataset_id                 = "raw"
  location                   = var.location
  delete_contents_on_destroy = true
}


# 4. Grant BigQuery Data Editor Rights to pdp-loader
resource "google_bigquery_dataset_iam_member" "pdp_loader_editor" {
  # References the local name of your dataset resource
  dataset_id = google_bigquery_dataset.raw.dataset_id

  # The exact role for editing dataset data (tables, views, etc.)
  role = "roles/bigquery.dataEditor"

  member = "serviceAccount:${var.loader_sa_email}"
}

# There will be separate grant on following datasets later (transforming job)

# Create a BigQuery Dataset for staging data
resource "google_bigquery_dataset" "staging" {
  dataset_id                 = "staging"
  location                   = var.location
  delete_contents_on_destroy = true
}

# Create a BigQuery Dataset for marts data
resource "google_bigquery_dataset" "marts" {
  dataset_id                 = "marts"
  location                   = var.location
  delete_contents_on_destroy = true
}

