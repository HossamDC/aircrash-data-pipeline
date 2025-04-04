terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------
# ✅ S3 Bucket
# ---------------------------------------------
resource "aws_s3_bucket" "data_bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = "Spark Data Bucket"
    Environment = "Dev"
  }
}

# ---------------------------------------------
# ✅ Redshift IAM Role (Basic S3)
# ---------------------------------------------
resource "aws_iam_role" "redshift_role" {
  name = "RedshiftS3AccessRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "redshift.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "redshift_s3_access" {
  role       = aws_iam_role.redshift_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

# ---------------------------------------------
# ✅ Redshift Spectrum IAM Role (S3 + Glue)
# ---------------------------------------------
resource "aws_iam_role" "redshift_spectrum_role" {
  name = "RedshiftSpectrumRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "redshift.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "spectrum_s3_access" {
  role       = aws_iam_role.redshift_spectrum_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "spectrum_glue_access" {
  role       = aws_iam_role.redshift_spectrum_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
}

# ---------------------------------------------
# ✅ Redshift Subnet Group & Security Group
# ---------------------------------------------
resource "aws_redshift_subnet_group" "demo_subnet_group" {
  name       = "demo-subnet-group"
  subnet_ids = ["subnet-0b89383302cc9b2c1", "subnet-01e5b7a12aa5dfa94", "subnet-0c7a53c5ec9e6d3bc", "subnet-06eb68aa5e99d735d"]

  tags = {
    Name = "Demo Subnet Group"
  }
}

resource "aws_security_group" "redshift_sg" {
  name        = "redshift-sg"
  description = "Security group for Redshift"
  vpc_id      = "vpc-03675f21362ca33bd"

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Redshift SG"
  }
}

# ---------------------------------------------
# ✅ Redshift Cluster
# ---------------------------------------------
resource "aws_redshift_cluster" "demo_cluster" {
  cluster_identifier      = "demo-cluster"
  database_name           = "demo_db"
  master_username         = "admin"
  master_password         = "YourStrongPassword123!"
  node_type               = "dc2.large"
  cluster_type            = "single-node"
  skip_final_snapshot     = true

  iam_roles = [
    aws_iam_role.redshift_role.arn,
    aws_iam_role.redshift_spectrum_role.arn
  ]

  cluster_subnet_group_name = aws_redshift_subnet_group.demo_subnet_group.name
  vpc_security_group_ids    = [aws_security_group.redshift_sg.id]

  tags = {
    Name        = "Demo Cluster"
    Environment = "Dev"
  }
}

# ---------------------------------------------
# ✅ EMR Roles
# ---------------------------------------------
resource "aws_iam_role" "EMR_DefaultRole" {
  name = "EMR_DefaultRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "elasticmapreduce.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })

  tags = {
    "for-use-with-amazon-emr-managed-policies" = "true"
  }
}

resource "aws_iam_policy_attachment" "emr_service_policy" {
  name       = "emr_service_policy_attachment"
  roles      = [aws_iam_role.EMR_DefaultRole.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEMRServicePolicy_v2"
}

resource "aws_iam_role" "EMR_EC2_DefaultRole" {
  name = "EMR_EC2_DefaultRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "ec2.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })

  tags = {
    "for-use-with-amazon-emr-managed-policies" = "true"
  }
}

resource "aws_iam_policy_attachment" "emr_ec2_policy" {
  name       = "emr_ec2_policy_attachment"
  roles      = [aws_iam_role.EMR_EC2_DefaultRole.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforEC2Role"
}

resource "aws_iam_instance_profile" "emr_profile" {
  name = "EMR_EC2_InstanceProfile"
  role = aws_iam_role.EMR_EC2_DefaultRole.name
}

# ---------------------------------------------
# ✅ EMR Cluster
# ---------------------------------------------
resource "aws_emr_cluster" "spark_cluster" {
  name          = "MyEMRCluster"
  release_label = "emr-6.10.0"
  applications  = ["Spark"]

  service_role = aws_iam_role.EMR_DefaultRole.arn

  log_uri = "s3://${var.bucket_name}/emr-logs/"
  termination_protection            = false
  keep_job_flow_alive_when_no_steps = true

  ec2_attributes {
    key_name                          = var.key_name
    subnet_id                         = var.subnet_id
    emr_managed_master_security_group = var.vpc_security_group_ids[0]
    emr_managed_slave_security_group  = var.vpc_security_group_ids[0]
    instance_profile                  = aws_iam_instance_profile.emr_profile.arn
  }

  master_instance_group {
    instance_type  = "m5.xlarge"
    instance_count = 1
  }

  core_instance_group {
    instance_type  = "m5.xlarge"
    instance_count = 2
  }

  tags = {
    Name        = "Spark Cluster"
    Environment = "Dev"
    for-use-with-amazon-emr-managed-policies = "true"
  }
}

# ---------------------------------------------
# ✅ Open SSH to EMR Master Node
# ---------------------------------------------
resource "aws_security_group_rule" "allow_ssh_to_emr" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = var.vpc_security_group_ids[0]
}