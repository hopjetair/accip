provider "aws" {
  region = var.aws_region
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "airline-vpc"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = element(data.aws_availability_zones.available.names, count.index)
  tags = {
    Name = "private-subnet-${count.index}"
  }
}

data "aws_availability_zones" "available" {}

resource "aws_db_subnet_group" "airline" {
  name       = "airline-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_security_group" "airline_sg" {
  name        = "airline-sg"
  description = "Allow PostgreSQL traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Restrict in production
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_rds_cluster" "airline_aurora" {
  cluster_identifier      = "airline-aurora"
  engine                  = "aurora-postgresql"
  engine_version          = "15.3"
  database_name           = var.db_name
  master_username         = var.master_username
  master_password         = var.master_password
    db_subnet_group_name    = aws_db_subnet_group.airline.name
  vpc_security_group_ids  = [aws_security_group.airline_sg.id]
  skip_final_snapshot     = true
  apply_immediately       = true
}

resource "aws_rds_cluster_instance" "airline_instance" {
  count              = 1
  identifier         = "airline-aurora-instance"
  cluster_identifier = aws_rds_cluster.airline_aurora.id
  instance_class     = var.instance_class
  engine             = aws_rds_cluster.airline_aurora.engine
  engine_version     = aws_rds_cluster.airline_aurora.engine_version
  db_subnet_group_name = aws_db_subnet_group.airline.name
  publicly_accessible = false
  apply_immediately   = true
}

resource "null_resource" "db_setup" {
  depends_on = [aws_rds_cluster_instance.airline_instance]

  provisioner "local-exec" {
    command = <<EOT
      if ! command -v psql &> /dev/null; then
        echo "Installing PostgreSQL client..."
        sudo apt-get update && sudo apt-get install -y postgresql-client || sudo yum install -y postgresql
      fi

      ENDPOINT=$(aws rds describe-db-clusters --db-cluster-identifier airline-aurora --query 'DBClusters[0].Endpoint.Address' --output text)
      USER=${var.master_username}
      PASSWORD=${var.master_password}
      DB=${var.db_name}

      until psql -h $ENDPOINT -U $USER -d $DB -c "SELECT 1" 2>/dev/null; do
        echo "Waiting for database to be ready..."
        sleep 10
      done

      psql -h $ENDPOINT -U $USER -d $DB -f scripts/create_airline_schema.sql
      python3 scripts/generator.py
    EOT
  }
}