import os
import json
import glob
import datetime
from common.utils import export_table_csv_docx


def parse_scp_files(input_root):
    scp_rows_accounts = []
    scp_rows_ous = []

    for filepath in glob.glob(os.path.join(input_root, "**", "Policy-*.json"), recursive=True):
        with open(filepath) as f:
            data = json.load(f)
            policies = data.get("Policies", [])

        filename = os.path.basename(filepath)
        if filename.startswith("Policy-Account-"):
            name = filename.replace("Policy-Account-", "").replace(".json", "")
            for p in policies:
                scp_rows_accounts.append([
                    name,
                    p.get("Name", ""),
                    p.get("Id", ""),
                    p.get("Arn", ""),
                    p.get("Description", "")
                ])

        elif filename.startswith("Policy-OU-"):
            name = filename.replace("Policy-OU-", "").replace(".json", "")
            for p in policies:
                scp_rows_ous.append([
                    name,
                    p.get("Name", ""),
                    p.get("Id", ""),
                    p.get("Arn", ""),
                    p.get("Description", "")
                ])

    return scp_rows_accounts, scp_rows_ous


def run():
    print("\n🔐 SCP Summary Generator")
    input_root = input("Enter the path to the folder containing SCP policy files: ").strip()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    output_dir = os.path.join("output", f"SCP_Summary_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    scp_rows_accounts, scp_rows_ous = parse_scp_files(input_root)

    if not scp_rows_accounts and not scp_rows_ous:
        print("❗ No SCP data found.")
        return

    if scp_rows_accounts:
        export_table_csv_docx(
            scp_rows_accounts,
            ["Account Name", "Policy Name", "Policy ID", "Policy ARN", "Description"],
            os.path.join(output_dir, "scp_accounts.csv"),
            os.path.join(output_dir, "scp_accounts.docx"),
            "Service Control Policies Attached to Accounts"
        )

    if scp_rows_ous:
        export_table_csv_docx(
            scp_rows_ous,
            ["OU Name", "Policy Name", "Policy ID", "Policy ARN", "Description"],
            os.path.join(output_dir, "scp_ous.csv"),
            os.path.join(output_dir, "scp_ous.docx"),
            "Service Control Policies Attached to Organizational Units"
        )

    print(f"✅ SCP summary exported to folder: {output_dir}")

