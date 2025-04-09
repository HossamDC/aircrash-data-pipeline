from prefect import flow, task
import subprocess
import os

BASE_DIR = "/home/anaconda/aircrash-data-pipeline"
TERRAFORM_DIR = os.path.join(BASE_DIR, "terraform")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DWH_DIR = os.path.join(BASE_DIR, "aircrash_dwh")
REQUIREMENTS_PATH = os.path.join(BASE_DIR, "scripts", "requirements.txt")  # حطيت الملف هنا حسب طلبك

@task
def terraform_apply():
    print("🚀 Running terraform apply...")
    try:
        subprocess.run(["terraform", "init"], cwd=TERRAFORM_DIR, check=True)
        subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR, check=True)
    except subprocess.CalledProcessError as e:
        if "InvalidPermission.Duplicate" in str(e):
            print("⚠️ Duplicate security rule found — safe to ignore.")
        else:
            raise e

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


@flow(name="Aircrash Phase 1 – Infra + Data")
def phase_one_flow():
    install_requirements()
    # terraform_apply()
    # run_pull_data()
    # run_create_external_table()
    # run_add_partitions()
    # run_generate_profiles()
    run_dbt()

if __name__ == "__main__":
    phase_one_flow()
