import os
import json
import glob
import shutil
import subprocess

# --------------- CONFIG ----------------
INPUT_DIR = "input"
OUTPUT_DIR = "output"
OUTPUT_MMD_FILE = "aws_org_diagram.mmd"
OUTPUT_IMAGE_FILE = "aws_org_diagram.png"  # or .svg
SCALE_FACTOR = "5"  # Increase if you want even higher resolution
# ---------------------------------------

# ✅ Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------
# ✅ 1️⃣ Load ROOT info
# ---------------------------------------
root_file = os.path.join(INPUT_DIR, "list-roots.json")
with open(root_file) as f:
    roots_data = json.load(f)

root_name = roots_data["Roots"][0]["Name"]
print(f"✅ Root Name: {root_name}")

# ---------------------------------------
# ✅ 2️⃣ Load Organizational Units
# ---------------------------------------
ous_file = os.path.join(INPUT_DIR, "list-organizational-units-for-parent.json")
with open(ous_file) as f:
    ous_data = json.load(f)

ous_list = ous_data.get("OrganizationalUnits", [])
print(f"✅ Found {len(ous_list)} Organizational Units.")

# ---------------------------------------
# ✅ 3️⃣ Load Accounts for each OU
# ---------------------------------------
accounts_by_ou = {}

account_files_pattern = os.path.join(INPUT_DIR, "list-accounts-for-parent-*.json")
account_files = glob.glob(account_files_pattern)
print(f"✅ Found {len(account_files)} account list files for OUs.")

for account_file in account_files:
    with open(account_file) as f:
        accounts_data = json.load(f)
    
    # Extract OU Name from filename
    filename = os.path.basename(account_file)
    ou_name = filename.replace("list-accounts-for-parent-", "").replace(".json", "")
    
    accounts_list = accounts_data.get("Accounts", [])
    accounts_by_ou[ou_name] = accounts_list
    print(f"✅ Loaded {len(accounts_list)} accounts for OU Name: {ou_name}")

# ---------------------------------------
# ✅ 4️⃣ Generate Mermaid Diagram
# ---------------------------------------
mermaid_lines = []
mermaid_lines.append("graph TD")

# Add Root node
mermaid_lines.append(f'  Root["{root_name}"]')

# ✅ Add links from Root to each OU to enforce hierarchy
for ou in ous_list:
    ou_name = ou["Name"]
    clean_ou_name = ou_name.replace(" ", "").replace("-", "")
    mermaid_lines.append(f'  Root --> {clean_ou_name}')

# For class assignments
class_assignments = []

# Add subgraphs for each OU
for ou in ous_list:
    ou_name = ou["Name"]
    clean_ou_name = ou_name.replace(" ", "").replace("-", "")

    mermaid_lines.append(f'  subgraph {clean_ou_name} ["{ou_name}"]')

    accounts = accounts_by_ou.get(ou_name, [])
    if not accounts:
        print(f"⚠️ WARNING: No accounts found for OU '{ou_name}'")

    for account in accounts:
        acc_name = account["Name"]
        acc_status = account["Status"]
        node_id = acc_name.replace(" ", "").replace("-", "")

        # ✅ Rename if account name matches OU name
        if acc_name.strip().lower() == ou_name.strip().lower():
            print(f"⚠️ Renaming account '{acc_name}' in OU '{ou_name}' to '{acc_name} (Account)' to avoid cycle")
            acc_name_display = f"{acc_name} (Account)"
            node_id = node_id + "Account"
        else:
            acc_name_display = acc_name

        # Node label with status
        mermaid_lines.append(f'    {node_id}["{acc_name_display} ({acc_status})"]')
        class_assignments.append((node_id, acc_status))

    mermaid_lines.append("  end")

# Add style definitions
mermaid_lines.append("")
mermaid_lines.append("classDef active fill:#28a745,stroke:#333,stroke-width:1px;")
mermaid_lines.append("classDef suspended fill:#d73a49,stroke:#333,stroke-width:1px;")
mermaid_lines.append("")

# Assign classes
for node_id, status in class_assignments:
    if status == "ACTIVE":
        mermaid_lines.append(f'class {node_id} active')
    elif status == "SUSPENDED":
        mermaid_lines.append(f'class {node_id} suspended')

# ---------------------------------------
# ✅ 5️⃣ Write to .mmd output file
# ---------------------------------------
output_mmd_path = os.path.join(OUTPUT_DIR, OUTPUT_MMD_FILE)
with open(output_mmd_path, "w") as f:
    f.write("\n".join(mermaid_lines))

print(f"✅ Mermaid diagram saved to: {output_mmd_path}")

# ---------------------------------------
# ✅ 6️⃣ Check for mmdc and render PNG/SVG
# ---------------------------------------
mmdc_path = shutil.which("mmdc")
if not mmdc_path:
    print("❗ ERROR: Mermaid CLI (mmdc) not found in PATH.")
    print("✅ Install it with: npm install -g @mermaid-js/mermaid-cli")
    exit(1)

print(f"✅ Mermaid CLI found at: {mmdc_path}")

output_image_path = os.path.join(OUTPUT_DIR, OUTPUT_IMAGE_FILE)

try:
    subprocess.run([
        mmdc_path,
        "-i", output_mmd_path,
        "-o", output_image_path,
        "-s", SCALE_FACTOR
    ], check=True)
    print(f"✅ Diagram image generated at: {output_image_path}")

except subprocess.CalledProcessError as e:
    print("❗ ERROR: Mermaid CLI failed to generate diagram.")
    print(e)
    exit(1)
