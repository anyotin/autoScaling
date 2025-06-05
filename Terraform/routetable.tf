#----------------------------------------
# ルートテーブルの作成(subnet_lb)
#----------------------------------------
resource "aws_route_table" "eggplant-lb" {
  vpc_id = aws_vpc.eggplant.id

  route {
    cidr_block = "0.0.0.0/0" // どこからのアクセスを受け入れるかを指定
    gateway_id = aws_internet_gateway.eggplant.id
  }

  tags = {
    Name = "eggplant_lb"
  }
}

#----------------------------------------
# ルートテーブルの関連付け(subnet_lb)
#----------------------------------------
resource "aws_route_table_association" "eggplant-lb-a" {
  route_table_id = aws_route_table.eggplant-lb.id
  subnet_id      = aws_subnet.eggplant-lb-a.id
}

resource "aws_route_table_association" "eggplant-lb-c" {
  route_table_id = aws_route_table.eggplant-lb.id
  subnet_id      = aws_subnet.eggplant-lb-c.id
}

#----------------------------------------
# ルートテーブルの作成(subnet_public)
#----------------------------------------
resource "aws_route_table" "eggplant-public" {
  vpc_id = aws_vpc.eggplant.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.eggplant.id
  }

  tags = {
    Name = "eggplant_public"
  }
}

#----------------------------------------
# ルートテーブルの関連付け(subnet_public)
#----------------------------------------
resource "aws_route_table_association" "eggplant-public-a" {
  route_table_id = aws_route_table.eggplant-public.id
  subnet_id      = aws_subnet.eggplant-public-a.id
}
