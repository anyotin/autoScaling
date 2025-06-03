#----------------------------------------
# Subnetの作成
#----------------------------------------
resource "aws_subnet" "auto-scaling-lb-a" {
  vpc_id     = aws_vpc.auto-scaling.id
  cidr_block = "172.23.10.0/24"
  availability_zone = "ap-northeast-1a"

  tags = {
    Name = "auto_scaling_lb_a"
  }
}

resource "aws_subnet" "auto-scaling-lb-c" {
  vpc_id     = aws_vpc.auto-scaling.id
  cidr_block = "172.23.11.0/24"
  availability_zone = "ap-northeast-1c"

  tags = {
    Name = "auto_scaling_lb_c"
  }
}

resource "aws_subnet" "auto-scaling-public-a" {
  vpc_id     = aws_vpc.auto-scaling.id
  cidr_block = "172.23.12.0/24"
  availability_zone = "ap-northeast-1a"

  // サブネットで起動したインスタンスにパブリックIPを自動割り当て
  map_public_ip_on_launch = true

  tags = {
    Name = "auto_scaling_public_a"
  }
}

resource "aws_subnet" "auto-scaling-public-c" {
  vpc_id     = aws_vpc.auto-scaling.id
  cidr_block = "172.23.13.0/24"
  availability_zone = "ap-northeast-1c"

  // サブネットで起動したインスタンスにパブリックIPを自動割り当て
  map_public_ip_on_launch = true

  tags = {
    Name = "auto_scaling_public_c"
  }
}
