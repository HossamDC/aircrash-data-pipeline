variable "aws_region" {
  description = "AWS region"
  default     = "us-west-2"
}

variable "bucket_name" {
  description = "S3 bucket name"
  default     = "my-spark-stage-23-3-1998-v1-01" # Change this to a unique name
}

variable "subnet_id" {
  description = "Subnet ID for Redshift"
  type        = string
  default     = "subnet-0b89383302cc9b2c1"

}

variable "vpc_security_group_ids" {
  description = "VPC Security Group IDs for Redshift"
  type        = list(string)
  default     = ["sg-015beb0175f56cf5f"]
    
}

variable "key_name" {
  description = "Key pair name for accessing EMR cluster"
}
