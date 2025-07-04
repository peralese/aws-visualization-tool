import os
import json
import subprocess
import shutil

# --------------- CONFIG ----------------
INPUT_DIR = "input"
INPUT_FILE = "org.json"

OUTPUT_DIR = "output"
OUTPUT_MMD_FILE = "aws_org_diagram.mmd"
OUTPUT_IMAGE_FILE = "aws_org_diagram.png"
# To use SVG instead, just swap this:
# OUTPUT_IMAGE_FILE = "aws_org_diagram.svg"
# ---------------------------------------

# ✅ Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Construct input file path
input_path = os.path.join(INPUT_DIR, INPUT_FILE)
if not os.path.isfile(input_path):
    print(f"❗ ERROR: Input file not found: {input_path}")
    exit(1)

print(f"✅ Reading input file: {input_path}")

# ✅ Load AWS Organizations JSON
with open(input_path) as f:
    data = json.load(f)

accounts = data.get("Accounts", [])
if not accounts:
    print("❗ ERROR: No accounts found in input JSON.")
    exit(1)

# ✅ Identify the Management Account (INVITED)
master_account = None
for account in accounts:
    if account.get("JoinedMethod") == "INVITED":
        master_account = account
        break

if not master_account:
    print("❗ ERROR: No Management (INVITED) account found in input.")
    exit(1)

master_name = master_account["Name"]
master_status = master_account["Status"]

# ✅ Build Mermaid diagram text
lines = []
lines.append("graph TD")
lines.append(f'  Master["{master_name} ({master_status})"]')

for account in accounts:
    if account == master_account:
        continue
    name = account["Name"]
    status = account["Status"]
    # Sanitize node ID for Mermaid
    node_id = name.replace(" ", "").replace("-", "")
    lines.append(f'  Master --> {node_id}["{name} ({status})"]')

# ✅ Write Mermaid .mmd file to output
output_mmd_path = os.path.join(OUTPUT_DIR, OUTPUT_MMD_FILE)
with open(output_mmd_path, "w") as f:
    f.write("\n".join(lines))

print(f"✅ Mermaid .mmd file created at: {output_mmd_path}")

# ✅ Check for Mermaid CLI (mmdc) in PATH
mmdc_path = shutil.which("mmdc")
if not mmdc_path:
    print("❗ ERROR: Mermaid CLI (mmdc) not found in PATH.")
    print("✅ Install it with: npm install -g @mermaid-js/mermaid-cli")
    exit(1)

print(f"✅ Mermaid CLI found: {mmdc_path}")

# ✅ Call Mermaid CLI to render PNG/SVG
output_image_path = os.path.join(OUTPUT_DIR, OUTPUT_IMAGE_FILE)

try:
    subprocess.run([
        mmdc_path,
        "-i", output_mmd_path,
        "-o", output_image_path
    ], check=True)
    print(f"✅ Diagram image generated at: {output_image_path}")

except subprocess.CalledProcessError as e:
    print("❗ ERROR: Mermaid CLI failed to generate diagram.")
    print(e)
    exit(1)
