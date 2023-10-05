### vpc, internet gateway, and nat ###

data "aws_availability_zones" "available" {}

# https://registry.terraform.io/providers/hashicorp/aws/4.16.0/docs/resources/vpc

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr_block_main

  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.cluster_name}-main"
  }
}

# https://registry.terraform.io/providers/hashicorp/aws/4.16.0/docs/resources/internet_gateway

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.cluster_name}-main"
  }
}


# resource "aws_eip" "cluster-nat-eip" {
#   count = 1
#   vpc   = true
# }

# resource "aws_nat_gateway" "cluster-nat-gateway" {
#   count         = length(var.cidr_subnets_public)
#   allocation_id = element(aws_eip.cluster-nat-eip.*.id, count.index)
#   subnet_id     = element(aws_subnet.cluster-vpc-subnets-public.*.id, count.index)
# }

### subnets ###

# https://registry.terraform.io/providers/hashicorp/aws/4.16.0/docs/resources/subnet

resource "aws_subnet" "main" {
  vpc_id            = aws_vpc.main.id
  count             = length(var.cidr_subnets_main)
  availability_zone = element(data.aws_availability_zones.available.names, count.index % length(data.aws_availability_zones.available.names))
  cidr_block        = element(var.cidr_subnets_main, count.index)

  tags = {
    Name = "${var.cluster_name}-${element(data.aws_availability_zones.available.names, count.index)}-main"
  }
}

### route table ###

# https://registry.terraform.io/providers/hashicorp/aws/4.16.0/docs/resources/route_table

resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.cluster_name}-main"
  }
}

# https://registry.terraform.io/providers/hashicorp/aws/4.16.0/docs/resources/route_table_association

resource "aws_route_table_association" "main" {
  count          = length(var.cidr_subnets_main)
  subnet_id      = element(aws_subnet.main.*.id, count.index)
  route_table_id = aws_route_table.main.id
}

### security group ###

# https://registry.terraform.io/providers/hashicorp/aws/4.16.0/docs/resources/security_group

resource "aws_security_group" "elk" {
  name   = "${var.cluster_name}-elk"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.cidr_subnets_main
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming HTTP connections for issuing TLS certifcates"
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming HTTPS connections for issuing TLS certifcates"
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming SSH connection from VPN network"
  }

  # ingress {
  #  from_port   = 9200
  #  to_port     = 9200
  #  protocol    = "tcp"
  #  cidr_blocks = ["${aws_instance.cyrus_instance_hive[0].public_ip}/32"]
  #  description = "allow incoming Elasticsearch data from tpot hive node"
  #}

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-elk"
  }
}

resource "aws_security_group" "es_data" {
  name   = "${var.cluster_name}-es-data"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.cidr_subnets_main
    description = "allow incoming traffic from main subnet"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming SSH connection"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "allow access to Internet"
  }

  tags = {
    Name = "${var.cluster_name}-es-data"
  }
}

resource "aws_security_group" "kafka" {
  name   = "${var.cluster_name}-kafka"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.cidr_subnets_main
    description = "allow incoming traffic from main subnet"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming SSH connection"
  }

  ingress {
    from_port   = 31313
    to_port     = 31313
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "NGINX + basic auth to protect Kafdrop"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "allow access to Internet"
  }

  tags = {
    Name = "${var.cluster_name}-kafka"
  }
}

resource "aws_security_group" "web_crawler" {
  name   = "${var.cluster_name}-web-crawler"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.cidr_subnets_main
    description = "allow incoming traffic from main subnet"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming SSH connection"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "allow access to Internet"
  }

  tags = {
    Name = "${var.cluster_name}-web-crawler"
  }
}

resource "aws_security_group" "web_classifier" {
  name   = "${var.cluster_name}-web-classifier"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.cidr_subnets_main
    description = "allow incoming traffic from main subnet"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming SSH connection"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "allow access to Internet"
  }

  tags = {
    Name = "${var.cluster_name}-web-classifier"
  }
}

resource "aws_security_group" "twitter_crawler" {
  name   = "${var.cluster_name}-twitter-crawler"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.cidr_subnets_main
    description = "allow incoming traffic from main subnet"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming SSH connection"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "allow access to Internet"
  }

  tags = {
    Name = "${var.cluster_name}-twitter-crawler"
  }
}

resource "aws_security_group" "communityfeed_crawler" {
  name   = "${var.cluster_name}-communityfeed-crawler"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.cidr_subnets_main
    description = "allow incoming traffic from main subnet"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming SSH connection"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "allow access to Internet"
  }

  tags = {
    Name = "${var.cluster_name}-community-feed-crawler"
  }
}

resource "aws_security_group" "wikijs" {
  name   = "${var.cluster_name}-wikijs"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.cidr_subnets_main
    description = "allow incoming traffic from main subnet"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow incoming SSH connection"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["130.231.0.0/16"]
    description = "allow access to WikiJS"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "allow access to Internet"
  }

  tags = {
    Name = "${var.cluster_name}-wikijs"
  }
}

########## T-Pot Section ##########

resource "aws_vpc" "cyrus_vpc" {
  cidr_block = "11.2.0.0/16"

  tags = {
    Name = "${var.cluster_name}-cyrus-vpc"
  }
}

resource "aws_subnet" "cyrus_subnet" {
  vpc_id            = aws_vpc.cyrus_vpc.id
  cidr_block        = "11.2.1.0/24"
  availability_zone = "eu-central-1a"

  tags = {
    Name = "${var.cluster_name}-cyrus-subnet"
  }
}

resource "aws_internet_gateway" "cyrus_internet_gateway" {
  vpc_id = aws_vpc.cyrus_vpc.id

  tags = {
    Name = "${var.cluster_name}-cyrus-internet-gateway"
  }
}

resource "aws_route_table" "cyrus_route_table" {
  vpc_id = aws_vpc.cyrus_vpc.id

  # send all the data to the provided gateway
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.cyrus_internet_gateway.id
  }

  tags = {
    Name = "${var.cluster_name}-cyrus-route-table"
  }
}

resource "aws_route_table_association" "cyrus_route_table_association" {
  subnet_id      = aws_subnet.cyrus_subnet.id
  route_table_id = aws_route_table.cyrus_route_table.id
}

resource "aws_security_group" "cyrus_security_group" {
  name        = "${var.cluster_name}-cyrus-security-group"
  description = "Allows all ports and IPs to come in and out."
  vpc_id      = aws_vpc.cyrus_vpc.id

  ingress {
    description = "Allow all ports and IPs to come in."
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    #protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-cyrus-security-group"
  }
}

resource "aws_security_group" "misp" {
  name   = "${var.cluster_name}-misp"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.cidr_subnets_main
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "allow incoming SSH connection"
  }

  # disable https for development and test
  # ingress {
  #   from_port   = 443
  #   to_port     = 443
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-misp"
  }
}
