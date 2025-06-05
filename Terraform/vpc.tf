#----------------------------------------
# VPCの作成
#----------------------------------------
resource "aws_vpc" "eggplant" {
  cidr_block = "172.23.0.0/16"

  tags = {
    Name = "eggplant"
  }
}

#----------------------------------------
# IG(Internet Gateway)の作成
#----------------------------------------
resource "aws_internet_gateway" "eggplant" {
  vpc_id = aws_vpc.eggplant.id

  tags = {
    Name = "eggplant"
  }
}

#----------------------------------------
# Elastic IPの作成
#----------------------------------------
resource "aws_eip" "eggplant" {
  domain = "vpc"

  tags = {
    Name = "eggplant"
  }
}

#----------------------------------------
# NATG(NAT Gateway)の作成
#----------------------------------------
resource "aws_nat_gateway" "eggplant" {
  subnet_id     = aws_subnet.eggplant-public-a.id
  allocation_id = aws_eip.eggplant.id

  tags = {
    Name = "eggplant"
  }
}
