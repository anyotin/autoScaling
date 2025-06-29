#----------------------------------------
# セキュリティグループの作成(lb)
#----------------------------------------
resource "aws_security_group" "eggplant-lb" {
  vpc_id = aws_vpc.eggplant.id
  name   = "eggplant_lb"
}

#----------------------------------------
# セキュリティグループのルール作成(lb)
#----------------------------------------
resource "aws_vpc_security_group_ingress_rule" "eggplant-allow-http" {
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
  cidr_ipv4         = "219.120.96.216/29"
  security_group_id = aws_security_group.eggplant-lb.id

  tags = {
    Name = "eggplant_allow_http"
  }
}

resource "aws_vpc_security_group_ingress_rule" "eggplant-allow-https" {
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "219.120.96.216/29"
  security_group_id = aws_security_group.eggplant-lb.id

  tags = {
    Name = "eggplant_allow_https"
  }
}

resource "aws_vpc_security_group_egress_rule" "eggplant-all" {
  ip_protocol      = "-1"
  cidr_ipv4        = "0.0.0.0/0"
  security_group_id = aws_security_group.eggplant-lb.id

  tags = {
    Name = "eggplant_all"
  }
}

#----------------------------------------
# セキュリティグループの作成(public)
#----------------------------------------
resource "aws_security_group" "eggplant-public" {
  name        = "tnn_sg_public"
  vpc_id      = aws_vpc.eggplant.id
}

#----------------------------------------
# セキュリティグループのルール作成(public)
#----------------------------------------
resource "aws_vpc_security_group_ingress_rule" "eggplant-allow-public" {
  from_port         = 0
  to_port           = 65535
  ip_protocol       = "tcp"
  cidr_ipv4         = "172.23.0.0/16"
  security_group_id = aws_security_group.eggplant-public.id

  tags = {
    Name = "eggplant_allow_public"
  }
}

resource "aws_vpc_security_group_egress_rule" "eggplant-allow-public" {
  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
  security_group_id = aws_security_group.eggplant-public.id

  tags = {
    Name = "eggplant_allow_public"
  }
}

#----------------------------------------
# セキュリティグループの作成(ssh)
#----------------------------------------
resource "aws_security_group" "eggplant-ssh" {
  name    = "tnn_sg_ssh"
  vpc_id  = aws_vpc.eggplant.id
}

#----------------------------------------
# セキュリティグループのルール作成(ssh)
#----------------------------------------
resource "aws_vpc_security_group_ingress_rule" "eggplant-allow-ssh-00" {
  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
  cidr_ipv4   = var.company_ip1
  security_group_id = aws_security_group.eggplant-ssh.id

  tags = {
    Name = "eggplant_allow_ssh_00"
  }
}

resource "aws_vpc_security_group_ingress_rule" "eggplant-allow-ssh-01" {
  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
  cidr_ipv4   = var.company_ip2
  security_group_id = aws_security_group.eggplant-ssh.id

  tags = {
    Name = "eggplant_allow_ssh_01"
  }
}

resource "aws_vpc_security_group_ingress_rule" "eggplant-allow-ssh-local-01" {
  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
  cidr_ipv4   = var.local_ip
  security_group_id = aws_security_group.eggplant-ssh.id

  tags = {
    Name = "eggplant_allow_ssh_local_01"
  }
}

resource "aws_vpc_security_group_egress_rule" "eggplant-allow-ssh" {
  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
  security_group_id = aws_security_group.eggplant-ssh.id

  tags = {
    Name = "eggplant_allow_ssh"
  }
}
