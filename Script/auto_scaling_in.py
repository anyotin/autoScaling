import sys
import utility


def scaling_in_process() -> None:
    # 起動したインスタンスをターゲットグループから解除
    utility.elb_deregister_targets()

    # 起動したインスタンスをシャットダウン
    utility.execute_shutdown_instances()

    # 起動したインスタンスを終了
    utility.execute_terminate_instances()


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        raise Exception('Error!')