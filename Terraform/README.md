# Terraformメモ

### 🔸IAMロールを利用してTerraformからアクセス

[概要]<br>
単独のローカル環境で開発作業を行なっている場合、
aws_access_key と aws_secret_key をtfvarsに変数として直接指定してproviderに設定していた。<br>
しかし、直接指定はセキュリティ面からしたらキー情報の漏洩やサービスが不正に利用されてしまう可能性が高い。
そこでIamロールで管理しようってのが目的。

[対応方法]<br>
◽️AWS<br>
　1. 信頼されたエンティティタイプを"AWSアカウント"、AWSアカウントをTerraformを利用するアカウントにそれぞれ設定する。<br>
　2. Terraformでアクセスさせたい範囲のポリシーを選択してロールを作成。

◽️Terraform<br>

```terraform
provider "aws" {
  region     = var.aws_region
  # access_key = var.aws_access_key <- 必要なし
  # secret_key = var.aws_secret_key <- 必要なし
  assume_role {
    role_arn = var.system_role  #<自分のAWSアカウントID>:role/<スイッチロール先のIAMロール名>。作成したロールのArnをコピーして貼り付ける。
  }
}
```