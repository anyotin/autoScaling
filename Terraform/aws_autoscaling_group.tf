#----------------------------------------
# 起動テンプレート
#----------------------------------------
resource "aws_launch_template" "eggplant" {
  name = "eggplant"
  image_id      = "ami-073770dc3242b2a06" # Debian 11 (HVM), SSD Volume Type
  instance_type = "t3.micro"
  key_name      = aws_key_pair.eggplant-ssh-key.key_name

  iam_instance_profile {
    name = aws_iam_instance_profile.eggplant-web.name
  }

  network_interfaces {
    subnet_id = aws_subnet.eggplant-public-a.id
    security_groups = [aws_security_group.eggplant-public.id, aws_security_group.eggplant-ssh.id]
  }

  tag_specifications {
    resource_type = "instance"

    tags = {
      Name = "web_eggplant"
    }
  }
}