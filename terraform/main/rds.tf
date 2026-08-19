resource "aws_db_subnet_group" "warehouse" {
  name = "totesys-dev-warehouse-subnets"

  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]
}

resource "aws_db_instance" "warehouse" {
  identifier = "totesys-dev-warehouse"

  engine         = "postgres"
  instance_class = "db.t3.micro"
  port           = 5432

  allocated_storage = 20
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = "warehouse"
  username = "warehouse_admin"

  manage_master_user_password = true

  db_subnet_group_name = aws_db_subnet_group.warehouse.name

  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false
  multi_az            = false
}