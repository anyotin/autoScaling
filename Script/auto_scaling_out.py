import sys
import utility
import asyncio


def scaling_out_process() -> None:
    # インスタンスの起動
    # utility.run_instances_launch_template(launch_instance_num=int(args[1]))

    # 起動したインスタンス
    launch_instances = utility.execute_describe_instances('*')

    target_group = utility.execute_describe_target_groups('')
    target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']

    for instance in launch_instances:
        instance_id = instance['InstanceId']
        public_ip = instance['PublicIpAddress']

        # 清浄機起動しているかの確認
        if not utility.is_running_instance(instance_id):
            continue

        # 起動したインスタンスへ初期設定を実施
        asyncio.run(utility.async_run_initial_setting_current(public_ip))

        # 起動したインスタンスをターゲットグループへ追加
        utility.execute_elb_register_targets_current(target_group_arn, instance_id)

        # ヘルスチェックを実施し、全て完了すればOKとみなす。
        if not utility.check_health_instance(instance_id):
            continue


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        raise Exception('Error!')

    # scaling_out_process()
    print(utility.execute_describe_instances())

