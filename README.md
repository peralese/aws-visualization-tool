## AWS Visualization Toolkit

A modular, CLI-driven utility for converting AWS Organizations and Infrastructure data into **professional diagrams and structured documentation**. This tool helps cloud architects document account hierarchies, organizational units (OUs), service control policies (SCPs), and networking topology using JSON exported from the AWS CLI.

---

## ✨ Features

- ✅ Modular design: plug-and-play modules for Accounts, SCPs, and Networking
- ✅ Interactive CLI with optional scripted automation
- ✅ Accepts input from:
  - AWS CLI JSON exports
  - Folder structures with subdirectories
- ✅ Recursively searches for input files
- ✅ Outputs include:
  - Mermaid (optional) and Diagrams (.png) network visuals
  - CSV, DOCX, and Markdown deep dives
- ✅ Output folders are timestamped for organized audits
- ✅ Per-account VPC deep dives with multi-section Markdown reports
- ✅ Network diagrams per VPC rendered with **Diagrams (mingrammer)**
- 🔜 ZIP upload support
- 🔜 Full web interface (Flask prototype available)

---

## 🧩 Supported Modules

### 1. Accounts & OU Visualization
- Mermaid diagram showing Root → OUs → Accounts
- Color-coded ACTIVE / SUSPENDED status
- Master list of all accounts with OU mapping
- Grouped table of accounts per OU

### 2. Service Control Policies (SCP)
- CSV and DOCX reports of SCPs attached to:
  - Individual Accounts
  - Organizational Units (OUs)
- Automatically parses `Policy-Account-*` and `Policy-OU-*` file patterns

### 3. VPC & Networking Summary
- Summary table of all VPCs across accounts:
  - Includes VPC ID, **all associated CIDRs**, IPv6 status, Flow Logs, TGW, Endpoints, etc.
- Per-VPC deep dive:
  - Multi-section **Markdown report** with:
    - VPC Configuration
    - Subnet layout (CIDR, AZ, type, IPs)
    - Route Table Summary
    - VPC Endpoints
    - Notes (flow log status, TGW, VPN/Peering, RAM)
- Automatically parses:
  - `vpcs.json`
  - `subnet.json`
  - `route-tables.json`
  - `flow-logs.json`
  - `transit-gateway-attachments.json`
  - `vpc-endpoints.json`
  - `vpc-peering-connections.json`
  - `vpn-connections.json`
  - `ram-resources.json`

> ✅ All filenames should be lowercase and match expected patterns (e.g., `vpc-endpoints.json`)

---

## 📁 Input Structure

Supports nested or flat folder layout. Examples:

```
input/
  list-roots.json
  list-organizational-units-for-parent.json
  list-accounts.json
  list-accounts-for-parent-OU1.json
  policies/
    policy-account-core.json
    policy-ou-devops.json

Networking/
  Master/
    vpcs.json
    subnet.json
    route-tables.json
    ...
  Non-Prd/
    vpcs.json
    ...
```

All files are discovered recursively.

---

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Node.js (for optional Mermaid diagrams)
- Graphviz (for Diagrams)

### Install Python and Node dependencies

```bash
pip install -r requirements.txt
npm install -g @mermaid-js/mermaid-cli
```

> ⚠️ If using Diagrams for network visuals, you must also install Graphviz:
> - Windows: https://graphviz.org/download/
> - macOS: `brew install graphviz`
> - Linux: `sudo apt install graphviz`

---

## 📤 Exporting AWS Data

### AWS Organizations

```bash
aws organizations list-roots > list-roots.json
aws organizations list-organizational-units-for-parent --parent-id <root-id> > list-organizational-units-for-parent.json
aws organizations list-accounts > list-accounts.json
aws organizations list-accounts-for-parent --parent-id <ou-id> > list-accounts-for-parent-<OU>.json
```

### SCP Attachments

```bash
aws organizations list-policies-for-target --target-id <account-id> --filter SERVICE_CONTROL_POLICY > policy-account-<name>.json
aws organizations list-policies-for-target --target-id <ou-id> --filter SERVICE_CONTROL_POLICY > policy-ou-<name>.json
```

### VPC / Network Data (per region/account)

```bash
aws ec2 describe-vpcs --region <region> > vpcs.json
aws ec2 describe-subnets --region <region> > subnet.json
aws ec2 describe-route-tables --region <region> > route-tables.json
aws ec2 describe-flow-logs --region <region> > flow-logs.json
aws ec2 describe-transit-gateway-attachments --region <region> > transit-gateway-attachments.json
aws ec2 describe-vpc-endpoints --region <region> > vpc-endpoints.json
aws ec2 describe-vpc-peering-connections --region <region> > vpc-peering-connections.json
aws ec2 describe-vpn-connections --region <region> > vpn-connections.json
aws ram get-resource-share-associations --association-type RESOURCE > ram-resources.json
```

---

## 🚀 Running the CLI

### 🔄 Interactive Mode

```bash
python main.py
```

You’ll be prompted to choose a module and specify:
- Input folder
- Output folder
- Image format (PNG or SVG)
- Scale factor (1–5)
- Region (for networking)

---

## 📂 Output Examples

Outputs are written to a timestamped subfolder:
```
output/
  VPC_Summary_2025-07-23-121806/
    vpcs_summary.csv
    vpcs_summary.md                ✅ Markdown summary table
    deepdive_<account>_<vpc>.md    ✅ Multi-section Markdown
    diagram_<account>_<vpc>.png    ✅ Diagrams-based PNG
  AWS_Accounts_2025-07-22-093122/
    aws_org_diagram.png
    aws_org_all_accounts.csv
    aws_org_accounts_by_ou.docx
  SCP_Summary_2025-07-22-094500/
    scp_accounts.csv
    scp_ous.docx
```

---

## 🧠 Diagram Features

- Mermaid-based (optional) diagrams
- Diagrams (mingrammer) for rich AWS network visuals
- Per-VPC PNG network diagrams:
  - VPC → Subnets (clustered)
  - EC2 icons per subnet
  - Interface Endpoints
  - Transit Gateway

---

## 🧱 Project Structure

```
aws-visualization-tool/
├── main.py
├── input/
├── output/
├── common/
│   └── utils.py
├── modules/
│   ├── accounts_runner.py
│   ├── scp_runner.py
│   ├── network_runner.py
│   └── vpc_diagram_generator.py  ✅ New
└── webapp/ (optional Flask prototype)
    ├── app.py
    ├── uploads/
    ├── outputs/
    └── templates/
```

---

## 🔭 Roadmap

### 🔜 Near Term
- Add ZIP support
- Scriptable CLI (e.g. `--input`, `--format`, `--scale`)
- Open image after generation
- Markdown-to-PDF/HTML exporter
- Per-VPC network diagrams (via Mermaid or Diagrams.py)
- **Save all generated tables as Markdown (in addition to DOCX/CSV)**

### 🧩 Future Modules
- EC2 / RDS / Lambda inventory
- IAM policy visualization
- S3 bucket inventory and ACL reporting
- Cost Explorer + CUR-based billing reports

---

## 👨‍💻 Author

**Erick Perales**  
IT Architect, Cloud Migration Specialist  
[https://github.com/peralese](https://github.com/peralese)
