import subprocess
import json
import os
import asyncio
import time
import sys

Instance_Launch_Timeout = 30
Instance_State_Check_Timeout = 30
Instance_Health_Check_Timeout = 60

# インスタンス情報確認
# PENDING = 0, RUNNING = 16, SHUTTING_DOWN = 32, TERMINATED = 48, STOPPING = 64, STOPPED = 80
def execute_describe_instances(filter_name: str, instance_state_codes: list[int]) -> list[dict[str, str]]:
    # AWS CLIコマンドを実行
    cli_cmd = ['aws', 'ec2', 'describe-instances', '--filters', f'Name=tag:Name,Values={filter_name}', '--output', 'json']

    cli_query = ['--query', 'Reservations[].Instances[].{'
                            'InstanceId: InstanceId,'
                            'InstanceName: Tags[?Key==`Name`].Value | [0],'
                            'State: State.Code,'
                            'PublicIpAddress: PublicIpAddress,'
                            'PrivateIpAddress: PrivateIpAddress}']

    result = subprocess.run(cli_cmd + cli_query, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_describe_instances コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")

    result_filter = [instance for instance in json.loads(result.stdout) if int(instance.get('State')) in instance_state_codes]

    return result_filter


# 起動テンプレートId取得コマンド実行
def execute_get_launch_template_id() -> str:
    cli_cmd = ['aws', 'ec2', 'describe-launch-templates', '--filters', f'Name=launch-template-name,Values=*foobar*']
    cli_query = ['--query', 'LaunchTemplates[0].LaunchTemplateId']

    result = subprocess.run(cli_cmd + cli_query, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_get_launch_template_id コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")

    return json.loads(result.stdout)


# インスタンス起動コマンド実行
def execute_run_instances(launch_template_id: str, index: int) -> None:
    cli_cmd = ['aws', 'ec2', 'run-instances',
               '--launch-template', f'LaunchTemplateId={launch_template_id},Version=1',
               '--tag-specifications', f"ResourceType=instance,Tags=[{{Key=Name,Value=eggplant_auto_scaling_{index}}}]"]

    result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_run_instances コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")


# ターゲットグループ取得
def execute_describe_target_groups(target_group_name: str) -> list[dict[str, str]]:
    # AWS CLIコマンドを実行
    cli_cmd = ['aws', 'elbv2', 'describe-target-groups', '--names', target_group_name, '--output', 'json']
    cli_query = ['--query', 'LaunchTemplates[0].LaunchTemplateId']

    result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_describe_target_groups コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")

    return json.loads(result.stdout)


# ターゲットグループへの追加
def execute_elb_register_targets_current(target_group_arn: str, instance_id: str) -> None:
    cli_cmd = ['aws', 'elbv2', 'register-targets', '--target-group-arn', target_group_arn, '--targets', json.dumps([{'Id': instance_id}])]

    result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_elb_register_targets_current コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")


# ヘルスチェックの状態確認
def execute_describe_target_health(target_group_arn: str, instance_id: str) -> list[dict[str, str]]:
    cli_cmd = ['aws', 'elbv2', 'describe-target-health', '--target-group-arn', target_group_arn, '--targets', json.dumps([{'Id': instance_id}])]

    result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_describe_target_health コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")

    return json.loads(result.stdout)


# インスタンスステータスの確認
def execute_describe_instance_status(target_instance_id: str) -> list[dict[str, str]]:
    cli_cmd = ['aws', 'ec2', 'describe-instance-status', '--filters', f'Name=launch-template-name,Values=*foobar*']

    cli_cmd = ['aws', 'ec2', 'describe-instance-status', '--instance-ids', target_instance_id]

    result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_describe_instance_status コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")

    return json.loads(result.stdout)


# ターゲットグループから解除
def execute_elb_deregister_targets(target_group_arn: str, target_instances: list[dict[str, str]]) -> None:
    targets = json.dumps([{'Id': instance['InstanceId']} for instance in target_instances])

    cli_cmd = ['aws', 'elbv2', 'deregister-targets', '--target-group-arn', target_group_arn, '--targets', targets]

    result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_elb_deregister_targets コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")


# インスタンスをシャットダウン
def execute_shutdown_instances(target_instances: list[dict[str, str]]) -> None:
    shutdown_target_instances = [instance['InstanceId'] for instance in target_instances]

    cli_cmd = ['aws', 'ec2', 'stop-instances', '--instance-ids'] + shutdown_target_instances

    result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_shutdown_instances コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")


# インスタンスを削除
def execute_terminate_instances(target_instances: list[dict[str, str]]) -> None:
    terminate_target_instances = [instance['InstanceId'] for instance in target_instances]

    cli_cmd = ['aws', 'ec2', 'terminate-instances', '--instance-ids'] + terminate_target_instances

    result = subprocess.run(cli_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("execute_terminate_instances コマンド実行エラー")
        raise Exception(f"エラー: {result.stderr}")


# 起動したインスタンスの取得待機
async def getting_instance_async(target_instance_name: str) -> list[dict[str, str]]:
    print("========== getting_instance_async 実行開始 ==========")

    start_time = time.time()
    check_interval = 1

    result = []

    while time.time() - start_time < Instance_Launch_Timeout:
        time.sleep(check_interval)
        try:
            result = execute_describe_instances(target_instance_name, [0, 16])
            if len(result) != 0:
                break

        except Exception as e:
            print(f"予期しないエラー: {e}")
            continue

    if len(result) == 0:
        print(f"✗ タイムアウト ({Instance_State_Check_Timeout}秒) に達しました")
        raise Exception("exist_instance_async タイムアウトエラー")

    print("========== getting_instance_async 実行終了 ==========")

    return result


# 起動テンプレートでの起動
def run_instances_launch_template(index: int):
    launch_template_id = execute_get_launch_template_id()

    execute_run_instances(launch_template_id, index)


# 各ホストに対してAnsible実行
async def async_run_ansible_playbook(target_ip) -> None:
    print("========== async_run_ansible_playbook 実行開始 ==========")

    target_set_up = f"{os.environ['HOME']}/AWS/AutoScalingVerification/Ansible/setup.yml"
    target_host = f"{os.environ['HOME']}/AWS/AutoScalingVerification/Ansible/hosts.yml"

    """単一のAnsibleプレイブックを非同期実行"""
    ansible_run_cmd = [
        'ansible-playbook', target_set_up, '-i', target_host, '-e', f'target_ip={target_ip}', '--timeout', '30'
    ]

    # asyncio.subprocessを使用
    process = await asyncio.create_subprocess_exec(
        *ansible_run_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    while True:
        if process.stdout.at_eof() and process.stderr.at_eof():
            break

        stdout = (await process.stdout.readline()).decode()
        if stdout:
            print(f'[stdout] {stdout}', end='', flush=True)
        stderr = (await process.stderr.readline()).decode()
        if stderr:
            print(f'[sdterr] {stderr}', end='', flush=True, file=sys.stderr)

        await asyncio.sleep(0.1)

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"✗ {target_ip}: Failed")
        print(f"Error: {stderr}")
        raise Exception(f"エラー: {stderr.decode()}")

    # 結果を処理
    print(f"✓ {target_ip}: Success")
    [print(f"{i:3d}: {line}") for i, line in enumerate(stdout.splitlines(), 1)]
    print("========== async_run_ansible_playbook 実行終了 ==========\n")


# インスタンスの起動状態チェック
async def check_instance_status_async(target_instance_id: str, state: str) -> bool:
    print("========== is_running_instance_async 実行開始 ==========")
    print(f"インスタンス {target_instance_id} のステータスチェックを開始します...")

    start_time = time.time()
    check_interval = 5

    result = False

    while time.time() - start_time < Instance_State_Check_Timeout:
        time.sleep(check_interval)

        try:
            target_instance_status = execute_describe_instance_status(target_instance_id)

            if not target_instance_status['InstanceStatuses']:
                print(f"インスタンス {target_instance_id} が見つかりません")
                continue

            instance_state = target_instance_status['InstanceStatuses'][0]['InstanceState']['Name']

            elapsed_time = int(time.time() - start_time)
            print(f"[{elapsed_time}s] インスタンス状態: {instance_state}")

            # インスタンス状態チェック
            if instance_state == state:
                print(f"✓ インスタンス {target_instance_id} は{state}状態です。")
                result = True
                break
            else:
                print(f"✗ インスタンス {target_instance_id} は {instance_state} 状態です。")
                print("意図した状態ではありません。")

        except Exception as e:
            print(f"予期しないエラー: {e}")
            continue

    if result:
        return result

    print(f"✗ タイムアウト ({Instance_State_Check_Timeout}秒) に達しました")
    print("========== is_running_instance_async 実行終了 ==========")

    return False


# ヘルスチェック
async def check_health_instance(target_group_arn: str, target_instance_id: str, target_status: str = 'healthy') -> bool:
    print("========== check_health_instance 実行開始 ==========")
    print(f"インスタンス {target_instance_id} のヘルスチェックチェックを開始します...")

    start_time = time.time()
    check_interval = 2

    result = False

    while time.time() - start_time < Instance_Health_Check_Timeout:
        time.sleep(check_interval)
        try:
            target_instance_health = execute_describe_target_health(target_group_arn, target_instance_id)

            if not target_instance_health['TargetHealthDescriptions']:
                print(f"インスタンス {target_instance_id} が見つかりません")
                continue

            state = target_instance_health['TargetHealthDescriptions'][0]['TargetHealth']['State']

            elapsed_time = int(time.time() - start_time)
            print(f"[{elapsed_time}s] インスタンス状態: {state}")

            # インスタンスが正常状態（running）かチェック
            if state == target_status:
                print(f"✓ インスタンス {target_instance_id} はヘルスチェックが完了しました。")
                result = True
                break
            else:
                print(f"✗ インスタンス {target_instance_id} ヘルスチェックが完了していません。: {state}")

        except Exception as e:
            print(f"予期しないエラー: {e}")
            continue

    if result:
        return result

    print(f"✗ タイムアウト ({Instance_Health_Check_Timeout}秒) に達しました")
    print("========== check_health_instance 実行終了 ==========")

    return result
