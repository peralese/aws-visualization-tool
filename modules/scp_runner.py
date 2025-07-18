import os
import json
import glob
from common.utils import normalize, export_table_csv_docx

def run():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    print("\n🟣 Processing Service Control Policies")
    print(f"✅ Input folder: {input_dir}")
    print(f"✅ Output folder: {output_dir}")

    # Discover policy files
    policy_files = glob.glob(os.path.join(input_dir, "**", "Policy-*.json"), recursive=True)
    print(f"✅ Found {len(policy_files)} SCP policy attachment files.")

    account_policies = []
    ou_policies = []

    for pf in policy_files:
        name = os.path.basename(pf).replace("Policy-", "").replace(".json", "")
        parts = name.split("-", 1)
        if len(parts) != 2:
            continue
        target_type, target_name = parts

        with open(pf) as f:
            policies = json.load(f).get("Policies", [])

        for p in policies:
            row = [target_name, p.get("Name"), p.get("Id"), p.get("AwsManaged", False)]
            if target_type.lower() == "account":
                account_policies.append(row)
            elif target_type.lower() == "ou":
                ou_policies.append(row)

    export_table_csv_docx(account_policies,
        ["Account Name", "Policy Name", "Policy ID", "AWS Managed"],
        os.path.join(output_dir, "scp_accounts.csv"),
        os.path.join(output_dir, "scp_accounts.docx"),
        "Service Control Policies - Accounts")

    export_table_csv_docx(ou_policies,
        ["OU Name", "Policy Name", "Policy ID", "AWS Managed"],
        os.path.join(output_dir, "scp_ous.csv"),
        os.path.join(output_dir, "scp_ous.docx"),
        "Service Control Policies - Organizational Units")

    print("✅ SCP summary tables generated.")
