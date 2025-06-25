terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.53.0"
    }
    awscc = {
      source  = "hashicorp/awscc"
      version = ">= 0.25.0"
    }
  }
}

provider "aws" {
  region     = var.aws_region
  # access_key = var.aws_access_key
  # secret_key = var.aws_secret_key
  assume_role {
    role_arn = var.system_role  #<自分のAWSアカウントID>:role/<スイッチロール先のIAMロール名>
  }
}
