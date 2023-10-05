terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.16.0"
    }
  }

  required_version = ">= 1.1.3"
}

provider "aws" {
  region = var.default_region

  default_tags {
    tags = var.default_tags
  }
}

# https://registry.terraform.io/providers/hashicorp/aws/4.16.0/docs/resources/instance

resource "aws_instance" "elk" {
  ami                    = var.ec2_default_ami
  instance_type          = var.elk_size
  count                  = var.elk_num
  subnet_id              = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids = aws_security_group.elk.*.id
  key_name               = var.aws_ssh_key_name

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 100
    delete_on_termination = false
  }

  tags = {
    Name          = "${var.cluster_name}-elk-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

#Allocate an Elastic IP to ELK stack
resource "aws_eip" "eip_elk" {
  count      = var.elk_num
  vpc        = true
  instance   = element(aws_instance.elk.*.id, count.index)
  depends_on = [aws_internet_gateway.main]
}

resource "aws_instance" "es_data" {
  ami                         = var.ec2_default_ami
  instance_type               = var.es_data_size
  count                       = var.es_data_num
  subnet_id                   = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids      = aws_security_group.elk.*.id
  key_name                    = var.aws_ssh_key_name
  associate_public_ip_address = true

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.es_data_storage
    delete_on_termination = false
  }

  tags = {
    Name          = "${var.cluster_name}-es-data-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

resource "aws_instance" "kafka" {
  ami                         = var.ec2_default_ami
  instance_type               = var.kafka_size
  count                       = var.kafka_num
  associate_public_ip_address = true
  subnet_id                   = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids      = aws_security_group.kafka.*.id
  key_name                    = var.aws_ssh_key_name

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 80
    delete_on_termination = false
  }

  tags = {
    Name          = "${var.cluster_name}-kafka-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

resource "aws_instance" "web_crawler" {
  ami                         = var.ec2_default_ami
  instance_type               = var.web_crawler_size
  count                       = var.web_crawler_num
  associate_public_ip_address = true
  subnet_id                   = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids      = aws_security_group.web_crawler.*.id
  key_name                    = var.aws_ssh_key_name

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.web_crawler_storage
    delete_on_termination = true
  }

  tags = {
    Name          = "${var.cluster_name}-web-crawler-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

resource "aws_instance" "search_engine" {
  ami                         = var.ec2_default_ami
  instance_type               = var.search_engine_size
  count                       = var.search_engine_num
  associate_public_ip_address = true
  subnet_id                   = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids      = aws_security_group.web_crawler.*.id
  key_name                    = var.aws_ssh_key_name

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 10
    delete_on_termination = true
  }

  tags = {
    Name          = "${var.cluster_name}-search-engine-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

resource "aws_instance" "web_classifier" {
  ami                         = var.ec2_default_ami
  instance_type               = var.web_classifier_size
  count                       = var.web_classifier_num
  associate_public_ip_address = true
  subnet_id                   = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids      = aws_security_group.web_classifier.*.id
  key_name                    = var.aws_ssh_key_name

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.web_classifier_storage
    delete_on_termination = true
  }

  tags = {
    Name          = "${var.cluster_name}-web-classifier-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

resource "aws_instance" "twitter_crawler" {
  ami                         = var.ec2_default_ami
  instance_type               = var.twitter_crawler_size
  count                       = var.twitter_crawler_num
  associate_public_ip_address = true
  subnet_id                   = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids      = aws_security_group.twitter_crawler.*.id
  key_name                    = var.aws_ssh_key_name

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.twitter_crawler_storage
    delete_on_termination = true
  }

  tags = {
    Name          = "${var.cluster_name}-twitter-crawler-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

resource "aws_instance" "wikijs" {
  ami                         = var.ec2_default_ami
  instance_type               = var.wikijs_size
  count                       = var.wikijs_num
  associate_public_ip_address = true
  subnet_id                   = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids      = aws_security_group.wikijs.*.id
  key_name                    = var.aws_ssh_key_name

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 40
    delete_on_termination = true
  }

  tags = {
    Name          = "${var.cluster_name}-wikijs-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

resource "aws_instance" "communityfeed_crawler" {
  ami                         = var.ec2_default_ami
  instance_type               = var.communityfeed_crawler_size
  count                       = var.communityfeed_crawler_num
  associate_public_ip_address = true
  subnet_id                   = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids      = aws_security_group.communityfeed_crawler.*.id
  key_name                    = var.aws_ssh_key_name

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 80
    delete_on_termination = true
  }

  tags = {
    Name          = "${var.cluster_name}-community-feed-crawler-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

resource "aws_instance" "misp" {
  ami                         = var.ec2_default_ami
  instance_type               = var.misp_size
  count                       = var.misp_num
  associate_public_ip_address = true
  subnet_id                   = element(aws_subnet.main.*.id, count.index)
  vpc_security_group_ids      = aws_security_group.misp.*.id
  key_name                    = var.aws_ssh_key_name

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 160
    delete_on_termination = true
  }

  tags = {
    Name          = "${var.cluster_name}-misp-${count.index}"
    Role          = "worker"
    ResearchGroup = "csi"
  }
}

### inventory file ###

data "aws_secretsmanager_secret_version" "credentials" {
  secret_id = "thor-credentials"
}

locals {
  creds = jsondecode(
    data.aws_secretsmanager_secret_version.credentials.secret_string
  )
}

resource "local_sensitive_file" "hosts_ini" {
  filename = "../ansible/inventory/hosts.ini"
  content = templatefile("${path.module}/templates/inventory.tpl", {
    elk                          = aws_instance.elk
    es_data                      = aws_instance.es_data
    misp                         = aws_instance.misp
    kafka                        = aws_instance.kafka
    wikijs                       = aws_instance.wikijs
    web_crawler                  = aws_instance.web_crawler
    search_engine                = aws_instance.search_engine
    web_classifier               = aws_instance.web_classifier
    twitter_crawler              = aws_instance.twitter_crawler
    communityfeed_crawler        = aws_instance.communityfeed_crawler
    ansible_user                 = var.ssh_user
    ansible_ssh_private_key_file = var.private_key_path
  })
}

resource "local_sensitive_file" "elk_env" {
  filename = "../service/elk/.env"
  content  = <<EOT
ELASTIC_PASSWORD='${local.creds.elasticsearch_password}'
ES_PUBLISH_HOST='${aws_instance.elk[0].private_ip}'
ES_DATA_HOST1='${aws_instance.es_data[0].private_ip}'
ES_DATA_HOST2='${aws_instance.es_data[1].private_ip}'
ES_DATA_NODE_NUM='${var.es_data_num}'
ES_MASTER_NODE_NAME='${var.es_master_node_name}'
ES_DATA_NODE_NAME='${var.es_data_node_name}'
LOGSTASH_INTERNAL_PASSWORD='${local.creds.logstash_internal_password}'
METRICBEAT_INTERNAL_PASSWORD='${local.creds.metricbeat_internal_password}'
FILEBEAT_INTERNAL_PASSWORD='${local.creds.filebeat_internal_password}'
KIBANA_SYSTEM_PASSWORD='${local.creds.kibana_system_password}'
KAFKA_SERVER='${join(",", formatlist("%s:9093", aws_instance.kafka.*.private_ip))}'
KAFKA_CLEAR_WEB_TOPIC='IoC_ClearWeb_Crawled'
KAFKA_DARK_WEB_TOPIC='IoC_DarkWeb_Crawled'
KAFKA_TWITTER_TOPIC='crawl_TwitterIOC'
EOT
}

resource "local_sensitive_file" "es_data_env" {
  filename = "../service/es_data/.env"
  content  = <<EOT
ES_MASTER_IP='${join(",", formatlist("%s", aws_instance.elk.*.private_ip))}'
ES_DATA_HOST1='${aws_instance.es_data[0].private_ip}'
ES_DATA_HOST2='${aws_instance.es_data[1].private_ip}'
ELASTIC_PASSWORD='${local.creds.elasticsearch_password}'
EOT
}

resource "local_sensitive_file" "web_crawler_env" {
  filename = "../service/crawlers/WebCrawler/.env"
  content  = <<EOT
KAFKA_SERVER='${join(",", formatlist("%s:9093", aws_instance.kafka.*.private_ip))}'
EOT
}

resource "local_sensitive_file" "search_engine_env" {
  filename = "../service/search_engine/server/src/.env"
  content  = <<EOT
ELASTICSEARCH_SERVER='${join(",", formatlist("http://%s:9200", aws_instance.elk.*.private_ip))}'
ELASTICSEARCH_PASSWORD='${local.creds.elasticsearch_password}'
API_PREFIX='/se/api'
EOT
}

resource "local_sensitive_file" "web_classifier_env" {
  filename = "../service/crawlers/WebClassifier/.env"
  content  = <<EOT
ELASTICSEARCH_SERVER='${join(",", formatlist("http://%s:9200", aws_instance.elk.*.private_ip))}'
ELASTICSEARCH_PASSWORD='${local.creds.elasticsearch_password}'
KAFKA_SERVER='${join(",", formatlist("%s:9093", aws_instance.kafka.*.private_ip))}'
EOT
}

resource "local_sensitive_file" "twitter_crawler_env" {
  filename = "../service/crawlers/twitter/.env"
  content  = <<EOT
ELASTICSEARCH_SERVER='${join(",", formatlist("http://%s:9200", aws_instance.elk.*.private_ip))}'
ELASTICSEARCH_PASSWORD='${local.creds.elasticsearch_password}'
KAFKA_SERVER='${join(",", formatlist("%s:9093", aws_instance.kafka.*.private_ip))}'
TWITTER_CONSUMER_KEY='${local.creds.twitter_consumer_key}'
TWITTER_CONSUMER_SECRET='${local.creds.twitter_consumer_secret}'
TWITTER_ACCESS_TOKEN='${local.creds.twitter_access_token}'
TWITTER_ACCESS_TOKEN_SECRET='${local.creds.twitter_access_token_secret}'
EOT
}

resource "local_sensitive_file" "communityfeed_crawler_env" {
  filename = "../service/crawlers/community/.env"
  content  = <<EOT
ELASTICSEARCH_SERVER='${join(",", formatlist("http://%s:9200", aws_instance.elk.*.private_ip))}'
ELASTICSEARCH_PASSWORD='${local.creds.filebeat_internal_password}'
MISP_SERVER='${var.misp_num == 1 ? format("http://%s", aws_instance.misp[0].public_ip) : ""}'
MISP_API_KEY='${local.creds.misp_api_key}'
OTX_API_KEY='${local.creds.otx_api_key}'
EOT
}

resource "local_sensitive_file" "wikijs_env" {
  filename = "../service/wikijs/.env"
  content  = <<EOT
DB_USER='${local.creds.wikijs_db_user}'
DB_PASS='${local.creds.wikijs_db_password}'
EOT
}

resource "local_sensitive_file" "kafka_env" {
  filename = "../service/kafka/.env"
  content  = <<EOT
# note: EXTERNAL_IP will be given by Ansible
KAFKA_ADVERTISE_ADDRESS='${join(",", formatlist("%s", aws_instance.kafka.*.private_ip))}'
EOT
}

resource "local_sensitive_file" "misp_env" {
  filename = "../service/misp/.env"
  content  = <<EOT
HOSTNAME='${var.misp_num == 1 ? format("http://%s", aws_instance.misp[0].public_ip) : ""}'
MYSQL_PASSWORD='${local.creds.misp_mysql_password}'
MYSQL_ROOT_PASSWORD='${local.creds.misp_mysql_root_password}'
EOT
}

resource "local_sensitive_file" "metricbeat_env" {
  filename = "../service/metricbeat/.env"
  content  = <<EOT
ELASTICSEARCH_SERVER='${join(",", formatlist("http://%s", aws_instance.elk.*.private_ip))}'
ELASTICSEARCH_USER='metricbeat_internal'
ELASTICSEARCH_PASSWORD='${local.creds.metricbeat_internal_password}'
EOT
}

resource "local_sensitive_file" "metricbeat_es_env" {
  filename = "../service/metricbeat-es/.env"
  content  = <<EOT
ELASTICSEARCH_SERVER='${join(",", formatlist("http://%s", aws_instance.elk.*.private_ip))}'
ELASTICSEARCH_USER='metricbeat_internal'
ELASTICSEARCH_PASSWORD='${local.creds.metricbeat_internal_password}'
EOT
}



########## T-POT Section ####################

resource "aws_instance" "cyrus_instance_hive" {
  ami               = "ami-0a8d4f587782c4a30" # debian 11, region=Frankfurt
  instance_type     = var.cyrus_instance_hive_size
  availability_zone = "eu-central-1a" # set it to be same as the subnet's
  key_name          = var.aws_ssh_key_name
  count             = var.cyrus_instance_hive_num # allow the number of VMs to be adjusted

  associate_public_ip_address = true
  subnet_id                   = aws_subnet.cyrus_subnet.id
  vpc_security_group_ids      = [aws_security_group.cyrus_security_group.id]

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 120
    delete_on_termination = true
  }

  # attaching the network interface
  # network_interface {
  #   device_index = 0
  #   network_interface_id = aws_network_interface.cyrus_network_interface.id
  # }

  user_data = data.template_file.user_data_hive.rendered

  tags = {
    Name          = "${var.cluster_name}-tpot-hive-${count.index}"
    ResearchGroup = "csi"
  }
}

resource "aws_instance" "cyrus_instance_sensor" {
  ami               = "ami-0a8d4f587782c4a30" # debian 11, region=Frankfurt
  instance_type     = var.cyrus_instance_sensor_size
  availability_zone = "eu-central-1a" # set it to be same as the subnet's
  key_name          = var.aws_ssh_key_name
  count             = var.cyrus_instance_sensor_num # allow the number of VMs to be adjusted

  associate_public_ip_address = true
  subnet_id                   = aws_subnet.cyrus_subnet.id
  vpc_security_group_ids      = [aws_security_group.cyrus_security_group.id]

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 120
    delete_on_termination = true
  }

  user_data = data.template_file.user_data_sensor.rendered

  tags = {
    Name          = "${var.cluster_name}-tpot-sensor-${count.index}"
    ResearchGroup = "csi"
  }
}

data "template_file" "user_data_hive" {
  template = file("./templates/user_data/user_data_for_hive.sh")

  vars = {
    SSH_USER     = local.creds.tpot_ssh_user
    SSH_PASSWORD = local.creds.tpot_ssh_password
    ES_PASSWORD  = local.creds.logstash_internal_password
    MAIN_ES_HOST = "http://crawlers.csilabs.eu:9200"
  }
}

data "template_file" "user_data_sensor" {
  template = file("./templates/user_data/user_data_for_sensor.sh")

  vars = {
    # does not need to provide MY_HIVE_IP if there is no Hive
    MY_HIVE_IP   = var.cyrus_instance_hive_num >= 1 ? "${aws_instance.cyrus_instance_hive[0].public_ip}" : ""
    SSH_USER     = local.creds.tpot_ssh_user
    SSH_PASSWORD = local.creds.tpot_ssh_password
  }
}
