data "aws_availability_zones" "available"{
    state = "available"
}

resource "aws_vpc" "main"{
    cidr_block = "10.0.0.0/16"
    
    enable_dns_support = true
    enable_dns_hostnames = true
    tags = {
        Name = "totesys-dev-vpc"
    }
}

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]

  map_public_ip_on_launch = false

  tags = {
    Name = "totesys-dev-vpc-private-a"
  }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]

  map_public_ip_on_launch = false
}

#Lambda Security Group
resource "aws_security_group" "lambda" {
  name        = "totesys-dev-lambda-sg"
  description = "Security group for schema Lambda"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "Allow outbound connections"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#RDS Security Group
resource "aws_security_group" "rds" {
  name        = "totesys-dev-rds-sg"
  description = "Allow PostgreSQL from schema Lambda"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from Lambda"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }
}

#secret manage
resource "aws_security_group" "secrets_endpoint" {
  name        = "totesys-dev-secrets-endpoint-sg"
  description = "Allow Lambda to access Secrets Manager endpoint"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTPS from Lambda"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }
}

resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id = aws_vpc.main.id

  service_name      = "com.amazonaws.eu-west-2.secretsmanager"
  vpc_endpoint_type = "Interface"

  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]

  security_group_ids = [
    aws_security_group.secrets_endpoint.id
  ]

  private_dns_enabled = true
}