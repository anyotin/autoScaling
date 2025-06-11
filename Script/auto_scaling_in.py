import utility
import asyncio
import threading

async def run_scaling_in_process() -> None:
    # 終了対象のインスタンス取得
    target_instances = utility.execute_describe_instances('*eggplant_auto_scaling_*', [16])
    print(target_instances)

    target_group = utility.execute_describe_target_groups('tnn-alb-tg')
    target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']

    for instance in target_instances:
        scaling_out_task = threading.Thread(target=run_scaling_in_task, args=(instance, target_group_arn))
        scaling_out_task.start()
        scaling_out_task.join()


def run_scaling_in_task(instance: dict[str, str], target_group_arn: str):
    # 起動したインスタンスをターゲットグループから解除
    utility.execute_elb_deregister_targets(target_group_arn, [instance])

    if not asyncio.run(utility.check_health_instance(target_group_arn, instance['InstanceId'], 'unused')):
        return

    # 起動したインスタンスを終了
    print("========== execute_terminate_instances 実行開始 ==========")
    utility.execute_terminate_instances([instance])
    print("========== execute_terminate_instances 実行完了 ==========")


if __name__ == "__main__":
    asyncio.run(run_scaling_in_process())