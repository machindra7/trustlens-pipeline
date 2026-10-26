import docker
import re

def parse_and_deploy(file_path, semgrep_finding_snippet):
    client = docker.from_env()
    match = re.search(r'["\']?(\d+):\d+["\']?', semgrep_finding_snippet)
    
    if match:
        exposed_port = match.group(1)
        print(f"[TrustLens] Insecure binding detected on port {exposed_port}. Deploying active defense...")
        
        try:
            # PUT YOUR ACTUAL NEON DB URL HERE
            neon_db_url = "postgresql://user:password@ep-lucky-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require"

            container = client.containers.run(
                "trustlens-honeypot:latest",
                detach=True,
                environment=[
                    f"HONEYPOT_PORT={exposed_port}",
                    f"DATABASE_URL=postgresql://neondb_owner:npg_UTqEb4axL6Ys@ep-fragrant-rice-b4go3j7f-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
                ],
                ports={f"{exposed_port}/tcp": int(exposed_port)},
                name=f"trustlens-trap-{exposed_port}",
                remove=True
            )
            print(f"[TrustLens] Success! Micro-Honeypot container '{container.name}' running on port {exposed_port}.")
            return True
        except docker.errors.APIError as e:
            print(f"[TrustLens Error] Could not deploy container: {e}")
            return False
    else:
        print("[TrustLens] No valid port mapping found in snippet.")
        return False

if __name__ == "__main__":
    mock_semgrep_snippet = 'ports:\n      - "2222:22"'
    parse_and_deploy("docker-compose.yml", mock_semgrep_snippet)
