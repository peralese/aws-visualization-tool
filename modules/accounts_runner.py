import os
import json
import glob
import shutil
import subprocess
from datetime import datetime
from common.utils import normalize, export_table_csv_docx

def generate_account_diagram(input_dir, output_base_dir, image_format="png", scale="2"):
    print("\n🟢 AWS Account Visualization Running")
    print(f"✅ Input folder: {input_dir}")
    print(f"✅ Base output folder: {output_base_dir}")
    print(f"✅ Image format: {image_format}")
    print(f"✅ Scale factor: {scale}\n")

    # ✅ Create timestamped output folder
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    final_output_dir = os.path.join(output_base_dir, timestamp)
    os.makedirs(final_output_dir, exist_ok=True)
    print(f"✅ Output will be saved in: {final_output_dir}")

    # Load Root
    root_file = glob.glob(os.path.join(input_dir, "**", "list-roots.json"), recursive=True)[0]
    with open(root_file) as f:
        root_name = json.load(f)["Roots"][0]["Name"]
    print(f"✅ Root Name: {root_name}")

    # Load OUs
    ous_file = glob.glob(os.path.join(input_dir, "**", "list-organizational-units-for-parent.json"), recursive=True)[0]
    ous_list = json.load(open(ous_file)).get("OrganizationalUnits", [])
    print(f"✅ Found {len(ous_list)} Organizational Units.")
    ou_name_to_id = {ou["Name"]: ou["Id"] for ou in ous_list}

    # Load all accounts
    all_accounts_file = glob.glob(os.path.join(input_dir, "**", "list-accounts.json"), recursive=True)[0]
    all_accounts_list = json.load(open(all_accounts_file)).get("Accounts", [])
    print(f"✅ Loaded {len(all_accounts_list)} total accounts.")

    account_name_to_id = {acct["Name"]: acct["Id"] for acct in all_accounts_list}

    # Load account-per-OU
    accounts_by_ou = {}
    for account_file in glob.glob(os.path.join(input_dir, "**", "list-accounts-for-parent-*.json"), recursive=True):
        with open(account_file) as f:
            accounts = json.load(f).get("Accounts", [])
        ou_name = os.path.basename(account_file).replace("list-accounts-for-parent-", "").replace(".json", "")
        accounts_by_ou[normalize(ou_name)] = accounts
        print(f"✅ Loaded {len(accounts)} accounts for OU Name: {ou_name}")

    # Build tables
    account_id_to_ou = {}
    for ou in ous_list:
        ou_name = ou["Name"]
        for account in accounts_by_ou.get(normalize(ou_name), []):
            account_id_to_ou[account["Id"]] = ou_name

    master_table = [
        [acct["Name"], acct["Id"], acct["Status"], account_id_to_ou.get(acct["Id"], "None")]
        for acct in all_accounts_list
    ]

    ou_table = []
    for ou in ous_list:
        ou_name = ou["Name"]
        for acct in accounts_by_ou.get(normalize(ou_name), []):
            ou_table.append([ou_name, acct["Name"], acct["Id"], acct["Status"]])

    export_table_csv_docx(master_table, ["Account Name", "Account ID", "Status", "OU Name"],
                          os.path.join(final_output_dir, "aws_org_all_accounts.csv"),
                          os.path.join(final_output_dir, "aws_org_all_accounts.docx"),
                          "AWS Organizations - All Accounts (Master List)")

    export_table_csv_docx(ou_table, ["OU Name", "Account Name", "Account ID", "Status"],
                          os.path.join(final_output_dir, "aws_org_accounts_by_ou.csv"),
                          os.path.join(final_output_dir, "aws_org_accounts_by_ou.docx"),
                          "AWS Organizations - Accounts by OU")

    # ✅ Mermaid Diagram
    mermaid_lines = []
    mermaid_lines.append("graph LR")
    mermaid_lines.append(f'  Root["{root_name}"]')

    class_assignments = []

    for ou in ous_list:
        ou_name = ou["Name"]
        clean_ou_name = normalize(ou_name)
        mermaid_lines.append(f'  Root --> {clean_ou_name}')

    for ou in ous_list:
        ou_name = ou["Name"]
        clean_ou_name = normalize(ou_name)
        mermaid_lines.append(f'  subgraph {clean_ou_name} ["{ou_name}"]')
        for acct in accounts_by_ou.get(clean_ou_name, []):
            node_id = normalize(acct["Name"])
            if node_id == clean_ou_name:
                node_id += "Account"
                acct["Name"] += " (Account)"
            mermaid_lines.append(f'    {node_id}["{acct["Name"]} ({acct["Status"]})"]')
            class_assignments.append((node_id, acct["Status"]))
        mermaid_lines.append("  end")

    mermaid_lines.append("classDef active fill:#28a745,stroke:#333,stroke-width:1px;")
    mermaid_lines.append("classDef suspended fill:#d73a49,stroke:#333,stroke-width:1px;")
    for node_id, status in class_assignments:
        if status == "ACTIVE":
            mermaid_lines.append(f'class {node_id} active')
        elif status == "SUSPENDED":
            mermaid_lines.append(f'class {node_id} suspended')

    output_mmd_path = os.path.join(final_output_dir, "aws_org_diagram.mmd")
    with open(output_mmd_path, "w") as f:
        f.write("\n".join(mermaid_lines))
    print(f"✅ Mermaid diagram saved to: {output_mmd_path}")

    mmdc_path = shutil.which("mmdc")
    if not mmdc_path:
        raise RuntimeError("❗ Mermaid CLI (mmdc) not found in PATH.")
    subprocess.run([
        mmdc_path,
        "-i", output_mmd_path,
        "-o", os.path.join(final_output_dir, f"aws_org_diagram.{image_format}"),
        "-s", scale
    ], check=True)
    print(f"✅ Diagram image generated.")

    return final_output_dir

def run():
    generate_account_diagram("input", "output", image_format="png", scale="2")

