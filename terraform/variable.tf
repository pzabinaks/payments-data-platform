variable "project_id" {
  type        = string
  description = "The ID of the Google Cloud project"
}

variable "region" {
  type        = string
  description = "Name of the region"
}

variable "location" {
  type        = string
  description = "Location"
}


variable "loader_sa_email" {
  type        = string
  description = "Loader email"
}
