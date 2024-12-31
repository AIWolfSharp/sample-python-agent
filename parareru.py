import argparse
import subprocess

# メイン関数
# この関数ではコマンドライン引数を解析し、指定された数のプロセスを起動します。
def main():
    # argparseを使用してコマンドライン引数を解析
    parser = argparse.ArgumentParser(description="指定されたホストとポートで複数のプロセスを起動します。")
    
    # ホストアドレスを指定する引数
    parser.add_argument(
        "-H", "--host", 
        type=str, 
        required=True, 
        help="ホストアドレスを指定します (例: 127.0.0.1)。"
    )
    
    # ポート番号を指定する引数 (デフォルト値は10000)
    parser.add_argument(
        "-P", "--port", 
        type=int, 
        default=10000, 
        help="開始ポート番号を指定します (デフォルト: 10000)。"
    )
    
    # 起動するプロセスの数を指定する引数 (デフォルト値は10)
    parser.add_argument(
        "-n", "--num_processes", 
        type=int, 
        default=10, 
        help="起動するプロセスの数を指定します (デフォルト: 10)。"
    )
    
    # 引数を解析して取得
    args = parser.parse_args()

    # 引数から各パラメータを取得
    HOST = args.host  # ホストアドレス
    PORT = args.port  # 開始ポート番号
    NUM_PROCESSES = args.num_processes  # 起動するプロセスの数

    # プロセスを管理するリスト
    processes = []

    # 指定された数のプロセスを起動
    for i in range(1, NUM_PROCESSES + 1):
        # プロセスごとの名前を生成 (例: Sample01, Sample02,...)
        name = f"Sample{i:02d}"
        
        # 実行するコマンドをリスト形式で作成
        # ここでは"python3 start.py"を起動し、ホスト、ポート、名前を渡します。
        cmd = [
            "python3", "start.py", 
            "-h", HOST, 
            "-p", str(PORT), 
            "-n", name
        ]

        # subprocessを使ってプロセスを非同期で起動し、リストに追加
        processes.append(subprocess.Popen(cmd))

    # 起動したすべてのプロセスが終了するのを待つ
    for p in processes:
        p.wait()

# Pythonスクリプトが直接実行された場合にのみ、main関数を呼び出す
if __name__ == "__main__":
    main()

