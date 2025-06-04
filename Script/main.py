import subprocess
import json
import sys
import os
import asyncio


# インスタンス情報確認
# aws ec2 describe-instances | jq '.Reservations[].Instances[] | { InstanceName: (.Tags[] | select(.Key=="Name").Value), InstanceId, PrivateIpAddress}'
# 0 : pending, 16 : running, 32 : shutting-down, 48 : terminated, 64 : stopping, 80 : stopped
def describe_instances(filter_name='*', instance_state_code=16) -> []:
    # AWS CLIコマンドを実行
    describe_instances_result = subprocess.run(
        ['aws', 'ec2', 'describe-instances', '--filters', f'Name=tag:Name,Values={filter_name}',
         f'Name=instance-state-code,Values={instance_state_code}', '--output', 'json'],
        capture_output=True,
        text=True,
        check=True
    )

    # 2番目のコマンド: jq処理
    result = subprocess.run(
        [
            'jq',
            '[.Reservations[].Instances[] | '
            '{InstanceName: (.Tags[] | select(.Key=="Name").Value), InstanceId, PrivateIpAddress, PublicIpAddress}]'
        ],
        input=describe_instances_result.stdout,  # 前のコマンドの出力を入力として使用
        capture_output=True,
        text=True,
        check=True
    )
    if result.returncode != 0:
        raise Exception(f"エラー: {result.stderr}")

    return json.loads(result.stdout)


# ランチテンプレートの確認
# aws ec2 describe-launch-templates
def describe_launch_templates() -> []:
    cli_cmd = ['aws', 'ec2', 'describe-launch-templates']
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception(f"エラー: {run_result.stderr}")

    launch_template_ids = []
    run_result_json = json.loads(run_result.stdout)

    for template in run_result_json['LaunchTemplates']:
        launch_template_ids.append(template['LaunchTemplateId'])

    return launch_template_ids


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
                   '--tag-specifications',
                   f"ResourceType=instance,Tags=[{{Key=Name,Value=tnn_api_dev_auto_scaling_{i + 1}}}]"]

        run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
        if run_result.returncode != 0:
            raise Exception('Error in run_instances_launch_template!')


async def async_run_initial_setting():
    # 複数のターゲットで並列実行
    describe_instances_result = describe_instances('*tnn_api_dev_auto_scaling*')

    # 並列実行
    results = await asyncio.gather(*[
        async_run_ansible_playbook(instance['PublicIpAddress'])
        for instance in describe_instances_result
    ])

    # 結果を処理
    for result in results:
        if result['return_code'] == 0:
            print(f"✓ {result['target_ip']}: Success")
            [print(f"{i:3d}: {line}") for i, line in enumerate(result['stdout'].splitlines(), 1)]
        else:
            print(f"✗ {result['target_ip']}: Failed")
            print(f"Error: {result['stderr']}")
            raise Exception('Error in async_run_initial_setting!')


async def async_run_ansible_playbook(target_ip):
    target_host = f"{os.environ['HOME']}/AWS/AutoScalingVerification/Ansible/hosts.yml"
    target_set_up = f"{os.environ['HOME']}/AWS/AutoScalingVerification/Ansible/setup.yml"

    """単一のAnsibleプレイブックを非同期実行"""
    ansible_run_cmd = [
        'ansible-playbook', target_set_up, '-i', target_host, '-e', f'target_ip={target_ip}'
    ]

    # asyncio.subprocessを使用
    process = await asyncio.create_subprocess_exec(
        *ansible_run_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    return {
        'return_code': process.returncode,
        'stdout': stdout,
        'stderr': stderr,
        'target_ip': target_ip
    }


# ターゲットグループへの追加
# aws elbv2 register-targets --target-group-arn arn:aws:elasticloadbalancing:ap-northeast-1:560655421385:targetgroup/tnn-alb-tg/4067c44f872b24c5 --targets Id=i-06ecf695c8f9b04dd
def elb_register_targets() -> None:
    # AWS CLIコマンドを実行
    cli_cmd = ['aws', 'elbv2', 'describe-target-groups', '--names', 'tnn-alb-tg', '--output', 'json']
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception(f"エラー: {run_result.stderr}")

    # [print(f"{i:3d}: {line}") for i, line in enumerate(run_result.stdout.splitlines(), 1)]
    run_result_json = json.loads(run_result.stdout)

    describe_instances_result = describe_instances('*tnn_api_dev_auto_scaling*')
    targetGroupArn = run_result_json['TargetGroups'][0]['TargetGroupArn']
    targets = get_register_target_instance(describe_instances_result)
    cli_cmd = ['aws', 'elbv2', 'register-targets', '--target-group-arn', targetGroupArn, '--targets', targets]
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in elb_register_targets!')


def get_register_target_instance(describe_instances_result: []) -> []:
    return json.dumps([{'Id': instance['InstanceId']} for instance in describe_instances_result])


# インスタンスステータスの確認
def describe_instance_status():
    raise Exception


# ヘルスチェックの状態確認
# aws elbv2 describe-target-health --target-group-arn=arn:aws:elasticloadbalancing:ap-northeast-1:560655421385:targetgroup/tnn-alb-tg/4067c44f872b24c5 --targets Id=i-06ecf695c8f9b04dd
def describe_target_health():
    raise Exception


def elb_deregister_targets() -> None:
    # AWS CLIコマンドを実行
    cli_cmd = ['aws', 'elbv2', 'describe-target-groups', '--names', 'tnn-alb-tg', '--output', 'json']
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception(f"エラー: {run_result.stderr}")

    # [print(f"{i:3d}: {line}") for i, line in enumerate(run_result.stdout.splitlines(), 1)]
    run_result_json = json.loads(run_result.stdout)

    describe_instances_result = describe_instances('*tnn_api_dev_auto_scaling*')
    target_group_arn = run_result_json['TargetGroups'][0]['TargetGroupArn']
    targets = get_register_target_instance(describe_instances_result)
    cli_cmd = ['aws', 'elbv2', 'deregister-targets', '--target-group-arn', target_group_arn, '--targets', targets]
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in elb_deregister_targets!')


def shutdown_instances() -> None:
    describe_instances_result = describe_instances('*tnn_api_dev_auto_scaling*')

    shutdown_target_instances = [instance['InstanceId'] for instance in describe_instances_result]

    cli_cmd = ['aws', 'ec2', 'stop-instances', '--instance-ids'] + shutdown_target_instances
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in shutdown_instances!')


def terminate_instances() -> None:
    describe_instances_result = describe_instances('*tnn_api_dev_auto_scaling*', 80)

    terminate_target_instances = [instance['InstanceId'] for instance in describe_instances_result]

    print(terminate_target_instances)

    cli_cmd = ['aws', 'ec2', 'terminate-instances', '--instance-ids'] + terminate_target_instances
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in terminate_instances!')


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        raise Exception('Error!')

    # インスタンスの起動
    # run_instances_launch_template(launch_instance_num=int(args[1]))

    # 起動したインスタンスへ初期設定を実施
    # asyncio.run(async_run_initial_setting())

    # 起動したインスタンスをターゲットグループへ追加
    # elb_register_targets()

    # ヘルスチェックを実施し、全て完了すればOKとみなす。

    # 起動したインスタンスをターゲットグループから解除
    # elb_deregister_targets()

    # 起動したインスタンスをシャットダウン
    # shutdown_instances()

    # 起動したインスタンスを終了
    terminate_instances()
