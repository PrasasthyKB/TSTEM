# global vars
cluster_name   = "thor-dev"
default_region = "eu-central-1"
default_tags   = { "Project" : "thor" }

# vpc vars
vpc_cidr_block_main = "11.0.0.0/16"
cidr_subnets_main   = ["11.0.0.0/24"]

# ec2 instances
ec2_default_ami = "ami-015c25ad8763b2f11"
ssh_user        = "ubuntu"

# elk host
elk_num  = 1
elk_size = "c6i.xlarge"
#
# elasticsearch data nodes
es_data_num     = 2
es_data_size    = "i3.large"
es_data_storage = 400

# elasticsearch node names
es_master_node_name = "thor-dev-es-master"
es_data_node_name   = "thor-dev-es-data"

# kafka host
kafka_num  = 0
kafka_size = "t3.medium"

# web crawler host
web_crawler_num     = 0
web_crawler_size    = "r6i.large"
web_crawler_storage = 120

# web classifier host
web_classifier_num     = 0
web_classifier_size    = "c5.2xlarge"
web_classifier_storage = 120

# twitter crawler host
twitter_crawler_num     = 0
twitter_crawler_size    = "t3.2xlarge"
twitter_crawler_storage = 120

# community feed crawler host
communityfeed_crawler_num  = 0
communityfeed_crawler_size = "t2.small"

# web crawler host
search_engine_num  = 1
search_engine_size = "t3.small"

# wikijs host
wikijs_num  = 0
wikijs_size = "t2.small"

# misp host
misp_num  = 0
misp_size = "t2.large"

cyrus_instance_hive_num  = 0
cyrus_instance_hive_size = "t3.xlarge"

cyrus_instance_sensor_num  = 0
cyrus_instance_sensor_size = "t3.xlarge"

# access-related
aws_ssh_key_name = "thor-dev-infrastructure"
private_key_path = "../thor-dev-infrastructure.pem"
