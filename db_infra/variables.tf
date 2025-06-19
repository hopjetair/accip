variable "aws_region" {
  description = "AWS region for the resources"
  default     = "ap-southeast-2"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "db_name" {
  description = "Name of the database"
  default     = "airline_db"
}

variable "master_username" {
  description = "Master username for the database"
  default     = "admin"
}

variable "master_password" {
  description = "Master password for the database"
  default     = "SecurePass123!"
}

variable "aws_role_arn" {
  description = "aws oidc connection for github"
  default     =  "arn:aws:iam::489582127457:role/GitHubActionsRole"
}

variable "instance_class" {
  description = "DB instance class"
  default     = "db.t3.medium"
}