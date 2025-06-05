#----------------------------------------
# Subnetの作成
#----------------------------------------
resource "aws_subnet" "eggplant-lb-a" {
  vpc_id     = aws_vpc.eggplant.id
  cidr_block = "172.23.10.0/24"
  availability_zone = "ap-northeast-1a"

  tags = {
    Name = "eggplant_lb_a"
  }
}

resource "aws_subnet" "eggplant-lb-c" {
  vpc_id     = aws_vpc.eggplant.id
  cidr_block = "172.23.11.0/24"
  availability_zone = "ap-northeast-1c"

  tags = {
    Name = "eggplant_lb_c"
  }
}

resource "aws_subnet" "eggplant-public-a" {
  vpc_id     = aws_vpc.eggplant.id
  cidr_block = "172.23.12.0/24"
  availability_zone = "ap-northeast-1a"

  // サブネットで起動したインスタンスにパブリックIPを自動割り当て
  map_public_ip_on_launch = true

  tags = {
    Name = "eggplant_public_a"
  }
}

resource "aws_subnet" "eggplant-public-c" {
  vpc_id     = aws_vpc.eggplant.id
  cidr_block = "172.23.13.0/24"
  availability_zone = "ap-northeast-1c"

  // サブネットで起動したインスタンスにパブリックIPを自動割り当て
  map_public_ip_on_launch = true

  tags = {
    Name = "eggplant_public_c"
  }
}
