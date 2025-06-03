import subprocess
import json
import sys
import os


# aws ec2 run-instances --launch-template LaunchTemplateId=lt-006a1fc4bbfe00e4b,Version=1

# ターゲットグループへの追加
# aws elbv2 register-targets --target-group-arn arn:aws:elasticloadbalancing:ap-northeast-1:560655421385:targetgroup/tnn-alb-tg/4067c44f872b24c5 --targets Id=i-06ecf695c8f9b04dd

# ヘルスチェックの状態確認
# aws elbv2 describe-target-health --target-group-arn=arn:aws:elasticloadbalancing:ap-northeast-1:560655421385:targetgroup/tnn-alb-tg/4067c44f872b24c5 --targets Id=i-06ecf695c8f9b04dd

# インスタンス情報確認
# aws ec2 describe-instances | jq '.Reservations[].Instances[] | { InstanceName: (.Tags[] | select(.Key=="Name").Value), InstanceId, PrivateIpAddress}'
def describe_instances(filter_name='*tnn*') -> []:
    # AWS CLIコマンドを実行
    cli_cmd = ['aws', 'ec2', 'describe-instances', '--filters', f'Name=tag:Name,Values={filter_name}', 'Name=instance-state-code,Values=16', '--output', 'json']
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)

    if run_result.returncode == 0:
        run_result_json = json.loads(run_result.stdout)

        # jqと同じ処理をPythonで実行
        describe_instances = []
        for reservation in run_result_json['Reservations']:
            for instance in reservation['Instances']:
                # Name タグを探す
                instance_name = None
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            break

                describe_instances.append({
                    'InstanceName': instance_name,
                    'InstanceId': instance['InstanceId'],
                    'PrivateIpAddress': instance.get('PrivateIpAddress')
                })

        return describe_instances
    else:
        print(f"エラー: {run_result.stderr}")
        return []


# ランチテンプレートの確認
# aws ec2 describe-launch-templates
def describe_launch_templates() -> []:
    cli_cmd = ['aws', 'ec2', 'describe-launch-templates']
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)

    if run_result.returncode == 0:
        LaunchTemplateIds = []
        run_result_json = json.loads(run_result.stdout)

        for template in run_result_json['LaunchTemplates']:
            LaunchTemplateIds.append(template['LaunchTemplateId'])

        return LaunchTemplateIds
    else:
        print(f"エラー: {run_result.stderr}")
        return []


# 使用する起動テンプレートを取得
def get_launch_templateId() -> str:
    return describe_launch_templates()[0]


# 起動テンプレートでの起動
# aws ec2 run-instances --launch-template LaunchTemplateId=lt-006a1fc4bbfe00e4b,Version=1
def run_instances_launch_template(launch_instance_num: int = 1, version: int = 1):
    describe_instances_result = describe_instances()

    print(describe_instances_result)

    if len(describe_instances_result) + launch_instance_num > 4:
        raise Exception('Error in run_instances_launch_template!')

    LaunchTemplateId = get_launch_templateId()

    for i in list(range(launch_instance_num)):
        cli_cmd = ['aws', 'ec2', 'run-instances',
                   '--launch-template', f'LaunchTemplateId={LaunchTemplateId},Version={version}',
                   '--tag-specifications', f"ResourceType=instance,Tags=[{{Key=Name,Value=tnn_api_dev_auto_scaling_{i + 1}}}]"]

        print(cli_cmd)

        run_result = subprocess.run(cli_cmd, capture_output=True, text=True)

        if run_result.returncode != 0:
            raise Exception('Error in run_instances_launch_template!')


def run_initial_setting():
    # cli_cmd = ['sed', '-e', '']
    describe_instances_result = describe_instances('*auto_scaling*')

    current_path = os.getcwd()
    print(current_path)

    for instance in describe_instances_result:
        print(instance)
        InstanceId = instance['InstanceId']
        cmd = f"sed -i '' '/^\[server\]$/a\\\n {InstanceId}' '{current_path}/../Ansible/hosts'"
        run_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(run_result)

    # ansible_cmd = ['ansible-playbook', '-i', '/Users/tanino/AWS/AutoScalingVerification/Ansible/hosts', '/Users/tanino/AWS/AutoScalingVerification/Ansible/setup.yml']


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        raise Exception('Error!')

    # run_instances_launch_template(launch_instance_num=int(args[1]))

    # 起動したインスタンスへ初期設定を実施
    run_initial_setting()
    # ECRからNginxのイメージを取得してコンテナ起動
    # 起動したインスタンスをターゲットグループへ追加
    # ヘルスチェックを実施し、全て完了すればOKとみなす。