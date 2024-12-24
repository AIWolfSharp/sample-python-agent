import subprocess

HOST = "133.24.115.177"
PORT = 10000

processes = []

for i in range(1, 11):
    name = f"Sample{i:02d}"
    cmd = ["python3", "start.py", "-h", HOST, "-p", str(PORT), "-n", name]
    processes.append(subprocess.Popen(cmd))

# 全プロセスが終了するのを待つ
for p in processes:
    p.wait()
