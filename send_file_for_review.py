import json, sys, pathlib, uuid, subprocess

file_path = pathlib.Path(sys.argv[1])
lang = sys.argv[2] if len(sys.argv) > 2 else "python"

payload = {
    "id": str(uuid.uuid4()),
    "language": lang,
    "code": file_path.read_text(encoding="utf-8")
}
cmd = [
    "docker", "exec", "-i", "kafka",
    "kafka-console-producer",
    "--bootstrap-server", "localhost:9092",
    "--topic", "code_review_requests"
]
subprocess.run(cmd, input=json.dumps(payload), text=True)
print("Sent", payload["id"])