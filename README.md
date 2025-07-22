# AWS Visualization Toolkit

A modular, CLI-driven utility for converting AWS Organizations and Infrastructure data into **professional diagrams and structured documentation**. This tool helps cloud architects document account hierarchies, organizational units (OUs), service control policies (SCPs), and networking topology using JSON exported from the AWS CLI.

---

## ✨ Features

- ✅ Modular design: plug-and-play modules for Accounts, SCPs, and Networking
- ✅ Interactive CLI with optional scripted automation (in progress)
- ✅ Accepts input from:
  - AWS CLI JSON exports
  - Folder structures with subdirectories
- ✅ Recursively searches for input files
- ✅ Outputs include:
  - Mermaid diagrams (.mmd → PNG/SVG)
  - CSV and DOCX reports
- ✅ Output folders are timestamped for organized audits
- ✅ Per-account VPC deep dives
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
- Summary table of all VPCs across accounts
  - Includes VPC ID, Name, Region, CIDR, Flow Logs, TGW, Endpoints, etc.
- Per-account VPC "deep dive" table with fields like:
  - Subnet counts, IGW/NAT status, Peering, VPN, RAM sharing, and notes
- Automatically parses:
  - `VPCS.json`
  - `subnet.json`
  - `route-tables.json`
  - `flow-logs.json`
  - `transit-gateway-attachments.json`
  - `vpc-endpoints.json`
  - `vpc-peering-connections.json`
  - `VPN-connection.json`
  - `RAM-Resources.json`

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
    Policy-Account-Core.json
    Policy-OU-DevOps.json

Networking/
  Master/
    VPCS.json
    subnet.json
    route-tables.json
    ...
  Non-Prd/
    VPCS.json
    ...
```

All files are discovered recursively.

---

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Node.js (for Mermaid CLI)

### Install Python and Node dependencies

```bash
pip install -r requirements.txt
npm install -g @mermaid-js/mermaid-cli
```

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
aws organizations list-policies-for-target --target-id <account-id> --filter SERVICE_CONTROL_POLICY > Policy-Account-<Name>.json
aws organizations list-policies-for-target --target-id <ou-id> --filter SERVICE_CONTROL_POLICY > Policy-OU-<Name>.json
```

### VPC / Network Data (per region/account)

```bash
aws ec2 describe-vpcs --region <region> > VPCS.json
aws ec2 describe-subnets --region <region> > subnet.json
aws ec2 describe-route-tables --region <region> > route-tables.json
aws ec2 describe-flow-logs --region <region> > flow-logs.json
aws ec2 describe-transit-gateway-attachments --region <region> > transit-gateway-attachments.json
aws ec2 describe-vpc-endpoints --region <region> > vpc-endpoints.json
aws ec2 describe-vpc-peering-connections --region <region> > vpc-peering-connections.json
aws ec2 describe-vpn-connections --region <region> > VPN-connection.json
aws ram get-resource-share-associations --association-type RESOURCE > RAM-Resources.json
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
  VPC_Summary_2025-07-21-101522/
    vpcs_summary.csv
    vpcs_summary.docx
    deepdive_Master_vpc-abc12345.csv
    deepdive_Master_vpc-abc12345.docx
  AWS_Accounts_2025-07-21-095944/
    aws_org_diagram.png
    aws_org_all_accounts.csv
    aws_org_accounts_by_ou.docx
  SCP_Export_2025-07-21-094022/
    scp_accounts.csv
    scp_ous.docx
```

---

## 🧠 Diagram Features

- Top-down or left-right layout (configurable)
- Root → OUs → grouped accounts
- ACTIVE / SUSPENDED status color-coded
- Mermaid source .mmd files
- Export to PNG or SVG (scalable)

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
│   └── network_runner.py
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
- Summary report generator across modules

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

