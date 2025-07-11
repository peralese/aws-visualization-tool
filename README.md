# AWS Visualization Tool

A utility to visualize your AWS Organizations hierarchy as clear, professional diagrams **and structured documentation tables**.  

It converts AWS CLI JSON exports into **Mermaid** diagrams (PNG/SVG) *and* generates **CSV** and **Word (.docx)** tables summarizing your AWS accounts, Organizational Units, and Service Control Policy (SCP) assignments.

---

## Features

- Inputs:
  - AWS Organizations CLI JSON exports:
    - `list-roots.json`
    - `list-organizational-units-for-parent.json`
    - `list-accounts-for-parent-*.json`
    - `list-accounts.json` *(complete master account list)*
    - `Policy-Account-<Account Name>.json` *(SCPs attached to Accounts)*
    - `Policy-OU-<OU Name>.json` *(SCPs attached to OUs)*
- Outputs:
  - Mermaid `.mmd` diagram source
  - Rendered PNG or SVG diagram
  - Timestamped subfolders for organized history
  - CSV and DOCX tables:
    - **Master Account Table** (all accounts with OU assignment)
    - **OU Breakdown Table** (accounts grouped by OU)
    - **SCP Assignments for Accounts**
    - **SCP Assignments for OUs**
- CLI interface:
  - Interactive prompts
  - Command-line arguments for automation
  - User-defined output format (PNG/SVG) and scale factor
- Webapp interface (Flask):
  - Upload multiple JSON files or a single ZIP bundle
  - Choose output format (PNG/SVG)
  - Specify scale factor (e.g., 1, 2, 3, ...)
  - Flash error handling and user-friendly feedback

---

## Installation & Setup

### Requirements
- Python 3.8+
- Node.js / npm (for Mermaid CLI)

### Install Dependencies
```
pip install Flask python-docx
npm install -g @mermaid-js/mermaid-cli
```

### Export Your AWS Organizations Data
```
aws organizations list-roots > list-roots.json
aws organizations list-organizational-units-for-parent --parent-id <root-id> > list-organizational-units-for-parent.json
aws organizations list-accounts-for-parent --parent-id <ou-id> > list-accounts-for-parent-<OU>.json
aws organizations list-accounts > list-accounts.json
```
### Export Service Control Policy Attachments
For each OU and Account:
```
aws organizations list-policies-for-target --target-id <target-id> --filter SERVICE_CONTROL_POLICY > Policy-OU-<OU Name>.json
aws organizations list-policies-for-target --target-id <target-id> --filter SERVICE_CONTROL_POLICY > Policy-Account-<Account Name>.json
```
Place all resulting JSON files in one folder.

---

## Running the CLI Tool

**Interactive mode:**
```
python main.py
```
You’ll be prompted for:
```
Input folder [input]:
Base output folder [output]:
Image format (png/svg) [png]:
Scale factor [2]:
```

**Command-line arguments:**
```
python main.py --input input --output output --format svg --scale 3
```
Supports automation in scripts and CI/CD pipelines.

---

## Running the Webapp

Start the Flask server:
```
cd webapp
flask run
```
Open in your browser:
```
http://localhost:5000
```
- Upload multiple JSON files or a single ZIP archive
- Choose output format (PNG/SVG)
- Specify scale factor
- Click **Generate Diagram** to receive your downloadable image and tables

---

## Example Project Structure
```
aws_visualizations/
  input/                     ← CLI input files
  output/                    ← CLI results (timestamped folders)
  main.py                    ← CLI entry point
  generator.py               ← Shared generation logic

  webapp/
    app.py                   ← Flask web server
    templates/
      index.html             ← Web upload form
    uploads/                 ← Temporary upload storage
    outputs/                 ← Generated diagrams and tables
```
Example CLI output folder:
```
output/
  2025-07-11-145100/
    aws_org_diagram.mmd
    aws_org_diagram.png
    aws_org_all_accounts.csv
    aws_org_all_accounts.docx
    aws_org_accounts_by_ou.csv
    aws_org_accounts_by_ou.docx
    aws_org_scp_accounts.csv
    aws_org_scp_accounts.docx
    aws_org_scp_ous.csv
    aws_org_scp_ous.docx
```

---

## Outputs

✅ **Mermaid Diagram**  
- Shows Root ➜ OUs ➜ Accounts hierarchy
- Color-coded ACTIVE/SUSPENDED
- Supports PNG and SVG

✅ **Master Account Table**  
- All accounts from list-accounts.json
- Includes OU assignment or “None”
- CSV and DOCX formats

✅ **OU Breakdown Table**  
- Only accounts assigned to OUs
- CSV and DOCX formats

✅ **SCP Assignments for Accounts**  
- All Service Control Policies attached to accounts
- CSV and DOCX formats

✅ **SCP Assignments for OUs**  
- All Service Control Policies attached to OUs
- CSV and DOCX formats

---

## Diagram Features

- Root node explicitly linked to each OU
- OU subgraphs with contained accounts
- Self-referencing accounts automatically renamed to avoid cycles
- Color-coded ACTIVE and SUSPENDED status
- Supports PNG and SVG output formats
- Scalable resolution with `--scale` option
- Clean, timestamped output folders for history and audit

---

## Potential Future Enhancements

- Inline diagram preview in webapp
- Nicer styling with Bootstrap
- Input validation before generation (missing required files check)
- Auto-cleanup of old output folders
- Support for nested OU hierarchies
- Packaging as an installable CLI tool
- Hosting the Flask interface online

---

## Author

Erick Perales  — IT Architect, Cloud Migration Specialist


