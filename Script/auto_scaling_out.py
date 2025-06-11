import sys
import utility
import asyncio
import threading
import time

def run_scaling_out_process() -> None:
    # オートスケーリングインスタンスの許容量チェック
    launch_instances = utility.execute_describe_instances('*eggplant_auto_scaling_*', [0, 16])
    if len(launch_instances) + int(args[1]) > 4:
        raise Exception('Already launch for auto scaling instances!')

    # 対象のターゲットグループのArnを取得
    target_group = utility.execute_describe_target_groups('tnn-alb-tg')
    target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']

    for i in range(1, int(args[1])+1):
        scaling_out_task = threading.Thread(target=run_scaling_out_task, args=(i, target_group_arn))
        scaling_out_task.start()
        scaling_out_task.join()


def run_scaling_out_task(index: int, target_group_arn: str):
    # インスタンス起動
    utility.run_instances_launch_template(index)

    # 起動したインスタンス取得
    get_instance = asyncio.run(utility.getting_instance_async(f'eggplant_auto_scaling_{index}'))

    instance_id = get_instance[0]['InstanceId']
    public_ip = get_instance[0]['PublicIpAddress']

    # 正常機起動しているかの確認
    if not asyncio.run(utility.check_instance_status_async(instance_id, 'running')):
        return

    # 少し待たないとエラーになる....
    time.sleep(10)

    # 起動したインスタンスへ初期設定を実施
    asyncio.run(utility.async_run_ansible_playbook(public_ip))

    # 起動したインスタンスをターゲットグループへ追加
    utility.execute_elb_register_targets_current(target_group_arn, instance_id)

    # ヘルスチェックを実施し、全て完了すればOKとみなす。
    if not asyncio.run(utility.check_health_instance(target_group_arn, instance_id)):
        return

    print(f"\ninstance_id: {instance_id}, public_ip: {public_ip}のインスタンスは正常に起動しております。")


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        raise Exception('Error!')

    run_scaling_out_process()