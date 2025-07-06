import os
import json
import glob
import shutil
import subprocess
import argparse
from datetime import datetime

# ---------------------------------------
# ✅ Helper: Normalize Names
# ---------------------------------------
def normalize(name):
    return name.replace(" ", "").replace("-", "").lower()

# ---------------------------------------
# ✅ CLI Argument Parsing
# ---------------------------------------
parser = argparse.ArgumentParser(
    description="Generate AWS Organization diagrams from CLI JSON outputs."
)

parser.add_argument(
    "--input",
    default=None,
    help="Input directory containing AWS Organizations JSON files"
)
parser.add_argument(
    "--output",
    default=None,
    help="Output directory for Mermaid and image files"
)
parser.add_argument(
    "--format",
    choices=["png", "svg"],
    default=None,
    help="Output image format: png or svg"
)
parser.add_argument(
    "--scale",
    default=None,
    help="Scale factor for image resolution"
)

args = parser.parse_args()

# ---------------------------------------
# ✅ Interactive Prompts with Defaults
# ---------------------------------------
def prompt_value(prompt, default):
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input if user_input else default

print("\n🟢 AWS Visualization Tool Interactive Setup")

INPUT_DIR = args.input or prompt_value("Input folder", "input")
OUTPUT_DIR = args.output or prompt_value("Base output folder", "output")
OUTPUT_IMAGE_FORMAT = args.format or prompt_value("Image format (png/svg)", "png")
SCALE_FACTOR = args.scale or prompt_value("Scale factor", "5")

OUTPUT_MMD_FILE = "aws_org_diagram.mmd"
OUTPUT_IMAGE_FILE = f"aws_org_diagram.{OUTPUT_IMAGE_FORMAT}"

# ---------------------------------------
# ✅ Add timestamped subfolder
# ---------------------------------------
timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
final_output_dir = os.path.join(OUTPUT_DIR, timestamp)
os.makedirs(final_output_dir, exist_ok=True)

print("\n✅ Configuration:")
print(f"  Input folder: {INPUT_DIR}")
print(f"  Base output folder: {OUTPUT_DIR}")
print(f"  Timestamped output folder: {final_output_dir}")
print(f"  Image format: {OUTPUT_IMAGE_FORMAT}")
print(f"  Scale factor: {SCALE_FACTOR}\n")

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
# ✅ 3️⃣ Load Accounts for each OU with normalization
# ---------------------------------------
accounts_by_ou = {}

account_files_pattern = os.path.join(INPUT_DIR, "list-accounts-for-parent-*.json")
account_files = glob.glob(account_files_pattern)
print(f"✅ Found {len(account_files)} account list files for OUs.")

for account_file in account_files:
    with open(account_file) as f:
        accounts_data = json.load(f)
    
    filename = os.path.basename(account_file)
    ou_name_raw = filename.replace("list-accounts-for-parent-", "").replace(".json", "")
    ou_name_normalized = normalize(ou_name_raw)
    
    accounts_list = accounts_data.get("Accounts", [])
    accounts_by_ou[ou_name_normalized] = accounts_list
    print(f"✅ Loaded {len(accounts_list)} accounts for OU Name: {ou_name_raw}")

# ---------------------------------------
# ✅ 4️⃣ Generate Mermaid Diagram
# ---------------------------------------
mermaid_lines = []
mermaid_lines.append("graph TD")
mermaid_lines.append(f'  Root["{root_name}"]')

# ✅ Add links from Root to each OU
for ou in ous_list:
    ou_name = ou["Name"]
    clean_ou_name = normalize(ou_name)
    mermaid_lines.append(f'  Root --> {clean_ou_name}')

class_assignments = []

for ou in ous_list:
    ou_name = ou["Name"]
    clean_ou_name = normalize(ou_name)

    mermaid_lines.append(f'  subgraph {clean_ou_name} ["{ou_name}"]')

    accounts = accounts_by_ou.get(clean_ou_name, [])
    if not accounts:
        print(f"⚠️ WARNING: No accounts found for OU '{ou_name}' (normalized key: '{clean_ou_name}')")

    for account in accounts:
        acc_name = account["Name"]
        acc_status = account["Status"]
        node_id = normalize(acc_name)

        if normalize(acc_name) == clean_ou_name:
            print(f"⚠️ Renaming account '{acc_name}' in OU '{ou_name}' to '{acc_name} (Account)' to avoid cycle")
            acc_name_display = f"{acc_name} (Account)"
            node_id = node_id + "Account"
        else:
            acc_name_display = acc_name

        mermaid_lines.append(f'    {node_id}["{acc_name_display} ({acc_status})"]')
        class_assignments.append((node_id, acc_status))

    mermaid_lines.append("  end")

# Add styles
mermaid_lines.append("")
mermaid_lines.append("classDef active fill:#28a745,stroke:#333,stroke-width:1px;")
mermaid_lines.append("classDef suspended fill:#d73a49,stroke:#333,stroke-width:1px;")
mermaid_lines.append("")

for node_id, status in class_assignments:
    if status == "ACTIVE":
        mermaid_lines.append(f'class {node_id} active')
    elif status == "SUSPENDED":
        mermaid_lines.append(f'class {node_id} suspended')

# ---------------------------------------
# ✅ 5️⃣ Write to .mmd output file in timestamped subfolder
# ---------------------------------------
output_mmd_path = os.path.join(final_output_dir, OUTPUT_MMD_FILE)
with open(output_mmd_path, "w") as f:
    f.write("\n".join(mermaid_lines))

print(f"\n✅ Mermaid diagram saved to: {output_mmd_path}")

# ---------------------------------------
# ✅ 6️⃣ Check for mmdc and render PNG/SVG
# ---------------------------------------
mmdc_path = shutil.which("mmdc")
if not mmdc_path:
    print("❗ ERROR: Mermaid CLI (mmdc) not found in PATH.")
    print("✅ Install it with: npm install -g @mermaid-js/mermaid-cli")
    exit(1)

print(f"✅ Mermaid CLI found at: {mmdc_path}")

output_image_path = os.path.join(final_output_dir, OUTPUT_IMAGE_FILE)

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

