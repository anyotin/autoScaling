#----------------------------------------
# 起動テンプレート
#----------------------------------------
resource "aws_launch_template" "auto-scaling" {
  name_prefix   = "auto-scaling"
  image_id      = "ami-073770dc3242b2a06" # Debian 11 (HVM), SSD Volume Type
  instance_type = "t3.micro"
  key_name      = aws_key_pair.auto-scaling-ssh-key.key_name

  iam_instance_profile {
    name = aws_iam_instance_profile.auto-scaling-ec2.name
  }

  network_interfaces {
    subnet_id = aws_subnet.auto-scaling-public-a.id
    security_groups = [aws_security_group.auto-scaling-public.id, aws_security_group.auto-scaling-ssh.id]
  }

  tag_specifications {
    resource_type = "instance"

    tags = {
      Name = "tnn_api_dev_as"
    }
  }
}