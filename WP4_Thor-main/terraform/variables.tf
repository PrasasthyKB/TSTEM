### general ###

variable "cluster_name" {}

variable "default_region" {}

variable "default_tags" {
  description = "Default tags for all resources"
  type        = map(string)
}

### vpc ###

variable "vpc_cidr_block_main" {
  description = "CIDR blocks for main VPC"
}

variable "cidr_subnets_main" {
  description = "CIDR blocks for main subnets"
  type        = list(string)
}

### credentials ###

variable "aws_ssh_key_name" {
  description = "name of the ssh keypair to use in AWS"
}

### ec2 ###

variable "elk_size" {
  description = "instance size for elk nodes"
}

variable "elk_num" {
  description = "number of elk nodes"
}

variable "es_master_node_name" {
  description = "prefix for master es node name"
}

variable "es_data_node_name" {
  description = "prefix for data es node names"
}

variable "es_data_size" {
  description = "instance size for es data nodes"
}

variable "es_data_storage" {
  description = "instance storage size for es data nodes"
}

variable "es_data_num" {
  description = "number of es data nodes"
}

variable "kafka_size" {
  description = "instance size for kafka nodes"
}

variable "kafka_num" {
  description = "number of kafka nodes"
}

variable "web_crawler_size" {
  description = "instance size for web crawler nodes"
}

variable "web_crawler_num" {
  description = "number of web crawler nodes"
}

variable "web_crawler_storage" {
  description = "instance storage size for web classifier nodes"
}
variable "search_engine_size" {
  description = "instance size for search engine nodes"
}

variable "search_engine_num" {
  description = "number of search engine nodes"
}

variable "web_classifier_size" {
  description = "instance size for web classifier nodes"
}

variable "web_classifier_num" {
  description = "number of web classifier nodes"
}

variable "web_classifier_storage" {
  description = "instance storage size for web classifier nodes"
}

variable "twitter_crawler_size" {
  description = "instance size for twitter crawler nodes"
}

variable "twitter_crawler_num" {
  description = "number of twitter crawler nodes"
}

variable "twitter_crawler_storage" {
  description = "instance storage size for twitter crawler nodes"
}

variable "wikijs_size" {
  description = "instance size for wikijs node"
}

variable "wikijs_num" {
  description = "number of wikijs nodes"
}

variable "misp_size" {
  description = "instance size for misp nodes"
}

variable "misp_num" {
  description = "number of misp nodes"
}

variable "communityfeed_crawler_size" {
  description = "instance size for communityfeed crawler nodes"
}

variable "communityfeed_crawler_num" {
  description = "number of communityfeed crawler nodes"
}

variable "ec2_default_ami" {}

# see https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connection-prereqs.html#connection-prereqs-get-info-about-instance
variable "ssh_user" {
  description = "ssh username for the AMI"
}

variable "private_key_path" {}



########## T-Pot Section ##########

variable "cyrus_instance_hive_size" {
  description = "instance size for cyrus_instance_hive node"
}

variable "cyrus_instance_hive_num" {
  description = "number of cyrus_instance_hive nodes"
}

variable "cyrus_instance_sensor_size" {
  description = "instance size for cyrus_instance_sensor node"
}

variable "cyrus_instance_sensor_num" {
  description = "number of cyrus_instance_sensor nodes"
}
