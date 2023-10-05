terraform {
  backend "s3" {
    bucket = "thor-infra"
    key    = "cluster-state"
    region = "eu-central-1"
  }
}
