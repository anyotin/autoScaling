#----------------------------------------
# VPCの作成
#----------------------------------------
resource "aws_vpc" "auto-scaling" {
  cidr_block = "172.23.0.0/16"

  tags = {
    Name = "auto_scaling"
  }
}

#----------------------------------------
# IG(Internet Gateway)の作成
#----------------------------------------
resource "aws_internet_gateway" "auto-scaling" {
  vpc_id = aws_vpc.auto-scaling.id

  tags = {
    Name = "auto_scaling"
  }
}

#----------------------------------------
# Elastic IPの作成
#----------------------------------------
resource "aws_eip" "auto-scaling" {
  domain = "vpc"

  tags = {
    Name = "auto_scaling"
  }
}

#----------------------------------------
# NATG(NAT Gateway)の作成
#----------------------------------------
resource "aws_nat_gateway" "auto-scaling" {
  subnet_id     = aws_subnet.auto-scaling-public-a.id
  allocation_id = aws_eip.auto-scaling.id

  tags = {
    Name = "auto_scaling"
  }
}
