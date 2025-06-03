#----------------------------------------
# ルートテーブルの作成(subnet_lb)
#----------------------------------------
resource "aws_route_table" "auto-scaling-lb" {
  vpc_id = aws_vpc.auto-scaling.id

  route {
    cidr_block = "0.0.0.0/0" // どこからのアクセスを受け入れるかを指定
    gateway_id = aws_internet_gateway.auto-scaling.id
  }

  tags = {
    Name = "auto_scaling_lb"
  }
}

#----------------------------------------
# ルートテーブルの関連付け(subnet_lb)
#----------------------------------------
resource "aws_route_table_association" "auto-scaling-lb-a" {
  route_table_id = aws_route_table.auto-scaling-lb.id
  subnet_id      = aws_subnet.auto-scaling-lb-a.id
}

resource "aws_route_table_association" "auto-scaling-lb-c" {
  route_table_id = aws_route_table.auto-scaling-lb.id
  subnet_id      = aws_subnet.auto-scaling-lb-c.id
}

#----------------------------------------
# ルートテーブルの作成(subnet_public)
#----------------------------------------
resource "aws_route_table" "auto-scaling-public" {
  vpc_id = aws_vpc.auto-scaling.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.auto-scaling.id
  }

  tags = {
    Name = "auto_scaling_public"
  }
}

#----------------------------------------
# ルートテーブルの関連付け(subnet_public)
#----------------------------------------
resource "aws_route_table_association" "auto-scaling-public-a" {
  route_table_id = aws_route_table.auto-scaling-public.id
  subnet_id      = aws_subnet.auto-scaling-public-a.id
}
