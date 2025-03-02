from ray.job_submission import JobSubmissionClient

client = JobSubmissionClient("http://127.0.0.1:8265")

square_entrypoint = """
wget https://raw.githubusercontent.com/JBris/kubernetes-kind-examples/refs/heads/main/deployment/dev/kuberay/square.py
python square.py
"""


submission_id = client.submit_job(
    entrypoint=square_entrypoint,
)

print("Use the following command to follow this Job's logs:")
print(f"ray job logs '{submission_id}' --address http://127.0.0.1:8265 --follow")
