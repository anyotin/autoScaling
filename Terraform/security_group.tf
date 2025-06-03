#----------------------------------------
# セキュリティグループの作成(lb)
#----------------------------------------
resource "aws_security_group" "auto-scaling-lb" {
  vpc_id = aws_vpc.auto-scaling.id
  name   = "auto_scaling_lb"
}

#----------------------------------------
# セキュリティグループのルール作成(lb)
#----------------------------------------
resource "aws_vpc_security_group_ingress_rule" "auto-scaling-allow-http" {
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
  cidr_ipv4         = "219.120.96.216/29"
  security_group_id = aws_security_group.auto-scaling-lb.id

  tags = {
    Name = "auto_scaling_allow_http"
  }
}

resource "aws_vpc_security_group_ingress_rule" "auto-scaling-allow-https" {
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "219.120.96.216/29"
  security_group_id = aws_security_group.auto-scaling-lb.id

  tags = {
    Name = "auto_scaling_allow_https"
  }
}

resource "aws_vpc_security_group_egress_rule" "auto-scaling-all" {
  ip_protocol      = "-1"
  cidr_ipv4        = "0.0.0.0/0"
  security_group_id = aws_security_group.auto-scaling-lb.id

  tags = {
    Name = "auto_scaling_all"
  }
}

#----------------------------------------
# セキュリティグループの作成(public)
#----------------------------------------
resource "aws_security_group" "auto-scaling-public" {
  name        = "tnn_sg_public"
  vpc_id      = aws_vpc.auto-scaling.id
}

#----------------------------------------
# セキュリティグループのルール作成(public)
#----------------------------------------
resource "aws_vpc_security_group_ingress_rule" "auto-scaling-allow-public" {
  from_port         = 0
  to_port           = 65535
  ip_protocol       = "tcp"
  cidr_ipv4         = "172.23.0.0/16"
  security_group_id = aws_security_group.auto-scaling-public.id

  tags = {
    Name = "auto_scaling_allow_public"
  }
}

resource "aws_vpc_security_group_egress_rule" "auto-scaling-allow-public" {
  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
  security_group_id = aws_security_group.auto-scaling-public.id

  tags = {
    Name = "auto_scaling_allow_public"
  }
}

#----------------------------------------
# セキュリティグループの作成(ssh)
#----------------------------------------
resource "aws_security_group" "auto-scaling-ssh" {
  name    = "tnn_sg_ssh"
  vpc_id  = aws_vpc.auto-scaling.id
}

#----------------------------------------
# セキュリティグループのルール作成(ssh)
#----------------------------------------
resource "aws_vpc_security_group_ingress_rule" "auto-scaling-allow-ssh-00" {
  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
  cidr_ipv4   = "219.120.96.216/29"
  security_group_id = aws_security_group.auto-scaling-ssh.id

  tags = {
    Name = "auto_scaling_allow_ssh_00"
  }
}

resource "aws_vpc_security_group_ingress_rule" "auto-scaling-allow-ssh-01" {
  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
  cidr_ipv4   = "218.42.203.175/32"
  security_group_id = aws_security_group.auto-scaling-ssh.id

  tags = {
    Name = "auto_scaling_allow_ssh_01"
  }
}

resource "aws_vpc_security_group_egress_rule" "auto-scaling-allow-ssh" {
  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
  security_group_id = aws_security_group.auto-scaling-ssh.id

  tags = {
    Name = "auto_scaling_allow_ssh"
  }
}
