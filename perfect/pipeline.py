from prefect import flow, task
import subprocess
import os
import json

BASE_DIR = "/home/anaconda/aircrash-data-pipeline"
TERRAFORM_DIR = os.path.join(BASE_DIR, "terraform")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DWH_DIR = os.path.join(BASE_DIR, "aircrash_dwh")
REQUIREMENTS_PATH = os.path.join(BASE_DIR, "scripts", "requirements.txt")  
TERRAFORM_OUTPUTS_PATH = os.path.join(BASE_DIR, "terraform", "tf_outputs.json")
S3_SCRIPT_PATH = "s3://my-spark-stage-23-3-1998-v1-01/scripts/spark-test-job.py"
PEM_PATH = os.path.join(BASE_DIR, "terraform", "my-key-pair-EMR.pem")

@task
def terraform_apply():
    print("🚀 Running terraform apply...")
    try:
        subprocess.run(["terraform", "init"], cwd=TERRAFORM_DIR, check=True)
        
        # Run 'apply' without check=True so we can handle errors manually
        result = subprocess.run(
            ["terraform", "apply", "-auto-approve"],
            cwd=TERRAFORM_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            stderr = result.stderr
            tolerated_errors = [
                "InvalidPermission.Duplicate",
                "EntityAlreadyExists",
                "InvalidGroup.Duplicate",
                "already exists",
            ]

            if any(err in stderr for err in tolerated_errors):
                print("⚠️ Terraform warning (tolerated):")
                print(stderr)
                print("✅ Continuing pipeline...")
            else:
                print("❌ Terraform failed with an unknown error:")
                print(stderr)
                raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=stderr)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ Terraform apply failed: {e.stderr}")


@task
def install_requirements():
    print(f"📦 Installing requirements from {REQUIREMENTS_PATH}")
    subprocess.run(["pip", "install", "-r", REQUIREMENTS_PATH], check=True)

@task
def run_pull_data():
    print("🛩️ Running pull-data script...")
    subprocess.run(["python", "pull-data.py"], cwd=SCRIPTS_DIR, check=True)


@task
def run_create_external_table():
    subprocess.run(["python", "create_external_table.py"], cwd=DWH_DIR, check=True)

@task
def run_add_partitions():
    subprocess.run(["python", "add_partitions.py"], cwd=DWH_DIR, check=True)

@task
def run_generate_profiles():
    subprocess.run(["python", "generate_profiles.py"], cwd=TERRAFORM_DIR, check=True)

@task
def run_dbt():
    print("🚀 Running dbt transformations using dbt-env...")
    dbt_executable = "/home/anaconda/dbt-env/bin/dbt"
    subprocess.run([dbt_executable, "run"], cwd=DWH_DIR, check=True)


@task
def get_emr_master_dns():
    print("📥 Loading EMR master public DNS from Terraform outputs...")
    try:
        # Ensure outputs are fresh
        subprocess.run(["terraform", "output", "-json"], cwd=TERRAFORM_DIR, check=True, stdout=open(os.path.join(TERRAFORM_DIR, "tf_outputs.json"), "w"))

        # Load the updated outputs
        with open(os.path.join(TERRAFORM_DIR, "tf_outputs.json")) as f:
            import json  # Make sure json is imported
            outputs = json.load(f)

        emr_dns = outputs["emr_master_public_dns"]["value"]
        print(f"🌐 EMR Master DNS: {emr_dns}")
        return emr_dns
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load EMR DNS: {e}")

@task
def run_test_spark_job(emr_dns: str):
    print("🚀 Running Spark test job on EMR cluster...")
    ssh_command = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-i", PEM_PATH,
        f"hadoop@{emr_dns}",
        f"spark-submit --master yarn --deploy-mode client {S3_SCRIPT_PATH}"
    ]
    subprocess.run(ssh_command, check=True)

@flow(name="Aircrash Phase 1 – Infra + Data")
def phase_one_flow():
    install_requirements()
    terraform_apply()
    run_pull_data()
    run_create_external_table()
    run_add_partitions()
    run_generate_profiles()
    run_dbt()
    emr_dns = get_emr_master_dns()
    run_test_spark_job(emr_dns)
    
if __name__ == "__main__":
    phase_one_flow()
