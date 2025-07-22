import os
import json
import datetime
import shutil
import subprocess
from common.utils import normalize, export_table_csv_docx

def run():
    print("\n📊 AWS Organizations: OU and Account Visualization")
    input_dir = input("Enter the path to the input folder (e.g., 'input'): ").strip()
    image_format = input("Enter desired image format (png/svg): ").strip().lower() or "png"
    scale = input("Enter scale factor (e.g., 1, 2, 3...): ").strip() or "2"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    output_base_dir = os.path.join("output", f"Accounts_Visualization_{timestamp}")
    os.makedirs(output_base_dir, exist_ok=True)

    # Load input data
    roots_path = os.path.join(input_dir, "list-roots.json")
    ou_path = os.path.join(input_dir, "list-organizational-units-for-parent.json")
    all_accounts_path = os.path.join(input_dir, "list-accounts.json")

    with open(roots_path) as f:
        root_data = json.load(f)
        root_name = root_data['Roots'][0]['Name']

    with open(ou_path) as f:
        ous_data = json.load(f)
        ous_list = ous_data['OrganizationalUnits']

    with open(all_accounts_path) as f:
        all_accounts_list = json.load(f)['Accounts']

    accounts_by_ou = {}
    for filename in os.listdir(input_dir):
        if filename.startswith("list-accounts-for-parent") and filename.endswith(".json"):
            with open(os.path.join(input_dir, filename)) as f:
                accounts_data = json.load(f).get("Accounts", [])
                ou_name = filename.replace("list-accounts-for-parent-", "").replace(".json", "")
                accounts_by_ou[normalize(ou_name)] = accounts_data

    # ---------------------------------------
    # ✅ Build Mermaid Diagram
    # ---------------------------------------
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
        accounts = accounts_by_ou.get(clean_ou_name, [])
        for account in accounts:
            acc_name = account["Name"]
            acc_status = account["Status"]
            node_id = normalize(acc_name)
            if normalize(acc_name) == clean_ou_name:
                acc_name_display = f"{acc_name} (Account)"
                node_id = node_id + "Account"
            else:
                acc_name_display = acc_name
            mermaid_lines.append(f'    {node_id}["{acc_name_display} ({acc_status})"]')
            class_assignments.append((node_id, acc_status))
        mermaid_lines.append("  end")

    mermaid_lines.append("")
    mermaid_lines.append("classDef active fill:#28a745,stroke:#333,stroke-width:1px;")
    mermaid_lines.append("classDef suspended fill:#d73a49,stroke:#333,stroke-width:1px;")
    mermaid_lines.append("")
    for node_id, status in class_assignments:
        if status == "ACTIVE":
            mermaid_lines.append(f'class {node_id} active')
        elif status == "SUSPENDED":
            mermaid_lines.append(f'class {node_id} suspended')

    output_mmd_file = "aws_org_diagram.mmd"
    output_image_file = f"aws_org_diagram.{image_format}"
    output_mmd_path = os.path.join(output_base_dir, output_mmd_file)
    with open(output_mmd_path, "w") as f:
        f.write("\n".join(mermaid_lines))
    print(f"\n✅ Mermaid diagram saved to: {output_mmd_path}")

    mmdc_path = shutil.which("mmdc")
    if not mmdc_path:
        raise RuntimeError(
            "❗ Mermaid CLI (mmdc) not found in PATH. "
            "Install it with: npm install -g @mermaid-js/mermaid-cli"
        )
    output_image_path = os.path.join(output_base_dir, output_image_file)
    subprocess.run([
        mmdc_path,
        "-i", output_mmd_path,
        "-o", output_image_path,
        "-s", scale
    ], check=True)
    print(f"✅ Diagram image generated at: {output_image_path}")

    # ---------------------------------------
    # ✅ Export Tables
    # ---------------------------------------
    all_accounts_table = [[a["Name"], a["Id"], a["Status"]] for a in all_accounts_list]
    export_table_csv_docx(
        all_accounts_table,
        ["Account Name", "Account ID", "Status"],
        os.path.join(output_base_dir, "aws_org_all_accounts.csv"),
        os.path.join(output_base_dir, "aws_org_all_accounts.docx"),
        "All AWS Accounts"
    )

    grouped_table = []
    for ou in ous_list:
        ou_name = ou["Name"]
        clean_ou_name = normalize(ou_name)
        for a in accounts_by_ou.get(clean_ou_name, []):
            grouped_table.append([ou_name, a["Name"], a["Id"], a["Status"]])

    export_table_csv_docx(
        grouped_table,
        ["OU Name", "Account Name", "Account ID", "Status"],
        os.path.join(output_base_dir, "aws_org_accounts_by_ou.csv"),
        os.path.join(output_base_dir, "aws_org_accounts_by_ou.docx"),
        "Accounts by Organizational Unit"
    )

    print(f"✅ All files saved in: {output_base_dir}")


