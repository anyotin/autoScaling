import subprocess
import json
import os
import asyncio
import time
import scaling_enum

Instance_State_Check_Timeout = 30
Instance_Health_Check_Timeout = 30


# インスタンス情報確認
def describe_instances(filter_name='*', instance_state_code: scaling_enum.StateCode = scaling_enum.StateCode.RUNNING) -> []:
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
def describe_launch_templates() -> []:
    cli_cmd = ['aws', 'ec2', 'describe-launch-templates']
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception(f"エラー: {run_result.stderr}")

    LaunchTemplateIds = []
    run_result_json = json.loads(run_result.stdout)

    for template in run_result_json['LaunchTemplates']:
        LaunchTemplateIds.append(template['LaunchTemplateId'])

    return LaunchTemplateIds


# 使用する起動テンプレートを取得
def get_launch_templateId() -> str:
    return describe_launch_templates()[0]


# 起動テンプレートでの起動
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


# 複数インスタンスの初期設定
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


# インスタンスの初期設定
async def async_run_initial_setting_current(public_ip: str) -> None:
    result = asyncio.run(async_run_ansible_playbook(public_ip))

    # 結果を処理
    if result['return_code'] == 0:
        print(f"✓ {result['target_ip']}: Success")
        [print(f"{i:3d}: {line}") for i, line in enumerate(result['stdout'].splitlines(), 1)]
    else:
        print(f"✗ {result['target_ip']}: Failed")
        print(f"Error: {result['stderr']}")
        raise Exception('Error in async_run_initial_setting!')


# 各ホストに対してAnsible実行
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


# ターゲットグループ取得
def describe_target_groups(target_group_name: str) -> []:
    # AWS CLIコマンドを実行
    cli_cmd = ['aws', 'elbv2', 'describe-target-groups', '--names', target_group_name, '--output', 'json']
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception(f"エラー: {run_result.stderr}")

    return json.loads(run_result.stdout)


# ターゲットグループへの追加
def elb_register_targets() -> None:
    target_group = describe_target_groups('*tnn-alb-tg*')
    targetGroupArn = target_group['TargetGroups'][0]['TargetGroupArn']

    describe_instances_result = describe_instances('*tnn_api_dev_auto_scaling*')
    targets = get_register_target_instance(describe_instances_result)
    cli_cmd = ['aws', 'elbv2', 'register-targets', '--target-group-arn', targetGroupArn, '--targets', targets]
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in elb_register_targets!')


# ターゲットグループへの追加
def elb_register_targets_current(target_group_arn: str, instance_id: str) -> None:
    cli_cmd = ['aws', 'elbv2', 'register-targets', '--target-group-arn', target_group_arn, '--targets', [{'Id': instance_id}]]
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in elb_register_targets!')


def get_register_target_instance(describe_instances_result: []) -> []:
    return json.dumps([{'Id': instance['InstanceId']} for instance in describe_instances_result])


# インスタンスステータスの確認
def describe_instance_status(target_instance_id: str) -> []:
    cli_cmd = ['aws', 'ec2', 'describe-instance-status', '--instance-ids', target_instance_id]
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in describe_instance_status!')

    return json.loads(run_result.stdout)


# インスタンスの起動状態チェック
def is_running_instance(target_instance_id: str) -> bool:
    print(f"インスタンス {target_instance_id} のステータスチェックを開始します...")

    start_time = time.time()
    check_interval = 3

    while time.time() - start_time < Instance_State_Check_Timeout:
        try:
            target_instance_status = describe_instance_status(target_instance_id)

            if not target_instance_status['Reservations']:
                print(f"インスタンス {target_instance_id} が見つかりません")
                return False

            instance = target_instance_status['Reservations'][0]['Instances'][0]
            state = instance['State']['Name']

            elapsed_time = int(time.time() - start_time)
            print(f"[{elapsed_time}s] インスタンス状態: {state}")

            # インスタンスが正常状態（running）かチェック
            if state == 'running':
                print(f"✓ インスタンス {target_instance_id} は正常に稼働しています")
                return True
            elif state in ['stopped', 'stopping', 'terminated', 'terminating']:
                print(f"✗ インスタンス {target_instance_id} は停止状態です: {state}")
                return False

        except subprocess.TimeoutExpired:
            print("AWS CLIコマンドがタイムアウトしました")
        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
        except Exception as e:
            print(f"予期しないエラー: {e}")

        time.sleep(check_interval)

    print(f"✗ タイムアウト ({Instance_State_Check_Timeout}秒) に達しました")
    return False


# ヘルスチェックの状態確認
def describe_target_health(target_group_arn: str, instance_id: str) -> []:
    cli_cmd = ['aws', 'elbv2', 'describe-target-health', '--target-group-arn', target_group_arn, '--targets', [{'Id': instance_id}]]
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in describe_instance_status!')

    return json.loads(run_result.stdout)


# ヘルスチェック
def check_health_instance(target_instance_id: str):
    print(f"インスタンス {target_instance_id} のヘルスチェックチェックを開始します...")

    start_time = time.time()
    check_interval = 3

    target_group = describe_target_groups('tnn-lb-tg')
    target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']

    while time.time() - start_time < Instance_Health_Check_Timeout:
        try:
            target_instance_health = describe_target_health(target_group_arn, target_instance_id)

            if not target_instance_health['TargetHealthDescriptions']:
                print(f"インスタンス {target_instance_id} が見つかりません")
                return False

            state = target_instance_health['TargetHealthDescriptions'][0]['TargetHealth']['State']

            elapsed_time = int(time.time() - start_time)
            print(f"[{elapsed_time}s] インスタンス状態: {state}")

            # インスタンスが正常状態（running）かチェック
            if state == 'healthy':
                print(f"✓ インスタンス {target_instance_id} はヘルスチェックが完了しました。")
                return True
            else:
                print(f"✗ インスタンス {target_instance_id} ヘルスチェックが完了していません。: {state}")
                return False

        except subprocess.TimeoutExpired:
            print("AWS CLIコマンドがタイムアウトしました")
        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
        except Exception as e:
            print(f"予期しないエラー: {e}")

        time.sleep(check_interval)

    print(f"✗ タイムアウト ({Instance_Health_Check_Timeout}秒) に達しました")
    return False


# ターゲットグループから解除
def elb_deregister_targets() -> None:
    target_group = describe_target_groups('*tnn-alb-tg*')
    targetGroupArn = target_group['TargetGroups'][0]['TargetGroupArn']

    describe_instances_result = describe_instances('*tnn_api_dev_auto_scaling*')
    targets = get_register_target_instance(describe_instances_result)
    cli_cmd = ['aws', 'elbv2', 'deregister-targets', '--target-group-arn', targetGroupArn, '--targets', targets]
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in elb_deregister_targets!')


# インスタンスをシャットダウン
def shutdown_instances() -> None:
    describe_instances_result = describe_instances('*tnn_api_dev_auto_scaling*')

    shutdown_target_instances = [instance['InstanceId'] for instance in describe_instances_result]

    cli_cmd = ['aws', 'ec2', 'stop-instances', '--instance-ids'] + shutdown_target_instances
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in shutdown_instances!')


# インスタンスを削除
def terminate_instances() -> None:
    describe_instances_result = describe_instances('*tnn_api_dev_auto_scaling*', scaling_enum.StateCode.STOPPED)

    terminate_target_instances = [instance['InstanceId'] for instance in describe_instances_result]

    print(terminate_target_instances)

    cli_cmd = ['aws', 'ec2', 'terminate-instances', '--instance-ids'] + terminate_target_instances
    run_result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if run_result.returncode != 0:
        raise Exception('Error in terminate_instances!')