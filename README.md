# AWS Visualization Toolkit

A modular, CLI-driven utility for converting AWS Organizations data into **visual diagrams and structured documentation**. This tool helps cloud architects document account hierarchies, organizational units (OUs), and Service Control Policies (SCPs) using input directly exported from the AWS CLI.

---

## ✨ Features

- ✅ Modular design: plug-and-play modules for accounts, SCPs, (networking coming soon)
- ✅ Interactive CLI or scripted automation
- ✅ Accepts input from:
  - AWS CLI JSON exports
  - Folder structures with subdirectories
- ✅ Outputs include:
  - Mermaid diagrams (.mmd → PNG/SVG)
  - CSV and DOCX reports
- ✅ Output folders are timestamped for easy auditing
- 🔜 ZIP upload support (planned)
- 🔜 Web interface support (Flask-based prototype complete)

---

## 🧩 Supported Modules

### 1. Accounts & OU Visualization
- Mermaid diagram showing Root → OUs → Accounts
- Color-coded ACTIVE / SUSPENDED status
- Master list of all accounts with OU mapping
- Grouped table of accounts per OU

### 2. Service Control Policies (SCP)
- CSV and DOCX reports of SCPs attached to:
  - Accounts
  - OUs
- Automatically parses `Policy-Account-*` and `Policy-OU-*` files

---

## 📁 Input Structure

Supports nested folders or flat structure:

```
input/
  list-roots.json
  list-organizational-units-for-parent.json
  list-accounts.json
  list-accounts-for-parent-OU1.json
  list-accounts-for-parent-OU2.json
  policies/
    Policy-Account-Core.json
    Policy-OU-DevOps.json
```

All files are parsed **recursively** — you may organize them freely.

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

### AWS Organizations (Accounts & OUs)
```bash
aws organizations list-roots > list-roots.json
aws organizations list-organizational-units-for-parent --parent-id <root-id> > list-organizational-units-for-parent.json
aws organizations list-accounts > list-accounts.json
aws organizations list-accounts-for-parent --parent-id <ou-id> > list-accounts-for-parent-<OU>.json
```

### SCP Attachments
```bash
aws organizations list-policies-for-target --target-id <target-id> --filter SERVICE_CONTROL_POLICY > Policy-Account-<Name>.json
aws organizations list-policies-for-target --target-id <target-id> --filter SERVICE_CONTROL_POLICY > Policy-OU-<Name>.json
```

---

## 🚀 Running the CLI

### 🔄 Interactive CLI
```bash
python main.py
```

You’ll be prompted to choose a module and specify:
- Input folder
- Output folder
- Image format (PNG or SVG)
- Scale factor (1–5)

### ⚙️ Scriptable CLI (planned)
Command-line arguments like:
```bash
python main.py --module accounts --input input/ --output output/ --format svg --scale 2
```
Coming soon.

---

## 📂 Output Examples

Outputs are stored in a timestamped subfolder:
```
output/2025-07-18-101522/
  aws_org_diagram.mmd
  aws_org_diagram.png
  aws_org_all_accounts.csv
  aws_org_all_accounts.docx
  aws_org_accounts_by_ou.csv
  aws_org_accounts_by_ou.docx
  scp_accounts.csv
  scp_accounts.docx
  scp_ous.csv
  scp_ous.docx
```

---

## 🧠 Diagram Features

- Top-down or left-right layout (configurable)
- Root node links to OUs
- OUs grouped with accounts inside subgraphs
- ACTIVE / SUSPENDED status color-coded
- Prevents cycles for accounts that match OU names
- Scalable image resolution using `--scale`

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
│   └── scp_runner.py
└── webapp/ (optional prototype)
    ├── app.py
    ├── uploads/
    ├── outputs/
    └── templates/
        └── index.html
```

---

## 🔭 Roadmap

### 🔜 Near Term
- Accept `.zip` input (auto-extract to temp dir)
- Command-line args for `--input`, `--output`, `--format`, etc.
- Option to auto-open the diagram after generation

### 🧩 Future Modules
- VPC + Subnet layout diagrams
- EC2 / RDS / Lambda inventory mapping
- IAM policy trust graphing
- Cost by account/OU (CUR parsing)

---

## 👨‍💻 Author

**Erick Perales**  
IT Architect, Cloud Migration Specialist  
[https://github.com/peralese](https://github.com/peralese)





