#----------------------------------------
# Webサーバー作成
#----------------------------------------
resource "aws_instance" "eggplant" {
  ami                    = "ami-073770dc3242b2a06" # Debian 11 (HVM), SSD Volume Type
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.eggplant-ssh-key.key_name
  subnet_id              = aws_subnet.eggplant-public-a.id
  vpc_security_group_ids = [aws_security_group.eggplant-public.id, aws_security_group.eggplant-ssh.id]
  private_ip             = "172.23.12.12"
  iam_instance_profile   = aws_iam_instance_profile.eggplant-web.name

//  user_data = file("./user_data/ec2-web.sh")

  tags = {
    Name = "eggplant"
  }
}

#----------------------------------------
# 公開鍵の作成
#----------------------------------------
resource "aws_key_pair" "eggplant-ssh-key" {
  key_name   = "tnn_ssh_key"
  public_key = file("./files/ssh/ssh_rsa_key.pub")
}

# ------------------------------
# IAM Role
# ------------------------------
resource "aws_iam_role" "eggplant-web" {
  name               = "tnn_iam_role_ec2"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.eggplant-web.json

  tags = {
    Roles = "eggplant_web"
  }
}

data "aws_iam_policy_document" "eggplant-web" {
  statement {
    # 誰が(EC2が)
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]  # 何をして(STSからIAM roleをassumeして)
    effect  = "Allow"  # 良い
  }
}

resource "aws_iam_role_policy_attachment" "eggplant-container-registry" {
  role       = aws_iam_role.eggplant-web.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

resource "aws_iam_role_policy_attachment" "eggplant-ec2" {
  role       = aws_iam_role.eggplant-web.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}

//resource "aws_iam_policy" "ecr_access_policy" {
//  name        = "ECRAccessPolicy"
//  description = "Allows EC2 to access specific ECR repository"
//  policy      = jsonencode({
//    Version = "2012-10-17",
//    Statement = [
//      {
//        Sid    = "GetAuthorizationToken",
//        Effect = "Allow",
//        Action = [
//          "ecr:GetAuthorizationToken"
//        ],
//        Resource = "*"
//      },
//      {
//        Sid    = "ManageRepositoryContents",
//        Effect = "Allow",
//        Action = [
//          "ecr:BatchCheckLayerAvailability",
//          "ecr:GetDownloadUrlForLayer",
//          "ecr:GetRepositoryPolicy",
//          "ecr:DescribeRepositories",
//          "ecr:ListImages",
//          "ecr:DescribeImages",
//          "ecr:BatchGetImage",
//          "ecr:InitiateLayerUpload",
//          "ecr:UploadLayerPart",
//          "ecr:CompleteLayerUpload",
//          "ecr:PutImage"
//        ],
//        Resource = "arn:aws:ecr:us-east-1:123456789012:repository/my-repo"
//      }
//    ]
//  })
//}
//
//
//resource "aws_iam_role_policy_attachment" "tnn_iam_role_policy_attachment_ecr" {
//  role       = aws_iam_role.tnn_iam_role_ec2.name
//  policy_arn = aws_iam_policy.ecr_access_policy.arn
//}

# ------------------------------
# Instance Profile
# ------------------------------
resource "aws_iam_instance_profile" "eggplant-web" {
  name = "tnn_iam_instance_profile_ec2"
  role = aws_iam_role.eggplant-web.name

  tags = {
    Roles = "eggplant_web"
  }
}
