import os
import glob
import json
import datetime
import subprocess
from collections import defaultdict

from common.utils import export_table_csv_docx

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _load(path):
    return json.load(open(path, encoding="utf-8-sig")) if os.path.exists(path) else {}

def _yes_no(flag: bool) -> str:
    return "Yes" if flag else "No"

def _tag_name(tags):
    return {t["Key"]: t["Value"] for t in tags}.get("Name", "(No Name)")


# -------------------------------------------------------------------
# Markdown deep‑dive exporter
# -------------------------------------------------------------------
def export_rich_deep_dive(account_name: str, vpc_id: str,
                          section_tables: dict[str, list[list[str | int]]],
                          out_dir: str):
    """
    Write a multi‑section Markdown deep‑dive report for a single VPC.
    """
    md_lines: list[str] = []
    title = f"## Detailed VPC Deep Dive — {account_name} / {vpc_id}"
    md_lines.append(title)
    md_lines.append("")

    def _table(header, rows):
        md_lines.append("|" + "|".join(header) + "|")
        md_lines.append("|" + "|".join(["---"] * len(header)) + "|")
        for r in rows:
            md_lines.append("|" + "|".join(str(x) for x in r) + "|")
        md_lines.append("")

    # 1️⃣ VPC Config
    md_lines.append("### 🔹 VPC Configuration")
    _table(["Attribute", "Value"], section_tables["config"])

    # 2️⃣ Subnet Layout
    md_lines.append("### 🔹 Subnet Layout")
    _table(
        ["Subnet Name", "CIDR Block", "AZ", "Type", "Public IPs?", "Available IPs"],
        section_tables["subnets"] or [["—", "—", "—", "—", "—", "—"]],
    )

    # 3️⃣ Route Table Summary
    md_lines.append("### 🔹 Route Table Summary")
    _table(
        ["Route Table", "Associated Subnets", "0.0.0.0/0 Target", "Notes"],
        section_tables["routes"] or [["—", "—", "—", "—"]],
    )

    # 4️⃣ VPC Endpoints
    md_lines.append("### 🔹 VPC Endpoints (Interface)")
    _table(
        ["Service", "Endpoint Name", "Subnet(s)", "Private DNS", "Security Group", "Purpose"],
        section_tables["endpoints"] or [["—", "—", "—", "—", "—", "—"]],
    )

    # 5️⃣ Additional Notes
    md_lines.append("### 🔹 Additional Notes")
    _table(["Category", "Details"], section_tables["notes"])

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"deepdive_{account_name}_{vpc_id}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"   •  Markdown deep‑dive saved: {out_path}")


# -------------------------------------------------------------------
# Per‑account parsing
# -------------------------------------------------------------------
def parse_account(acct_dir: str, account: str, region: str):
    """Return (summary_rows, deepdive_dict)."""

    # -- Load JSON blobs -------------------------------------------------
    vpcs      = _load(os.path.join(acct_dir, "VPCS.json")).get("Vpcs", []) or \
                _load(os.path.join(acct_dir, "VPCS.json")).get("VPCs", [])
    subnets   = _load(os.path.join(acct_dir, "subnet.json")).get("Subnets", [])
    routes    = _load(os.path.join(acct_dir, "route-tables.json")).get("RouteTables", [])
    flows     = _load(os.path.join(acct_dir, "flow-logs.json")).get("FlowLogs", [])
    tgw_atts  = _load(os.path.join(acct_dir, "transit-gateway-attachments.json")).get("TransitGatewayAttachments", [])
    endpoints = _load(os.path.join(acct_dir, "vpc-endpoints.json")).get("VpcEndpoints", [])
    peerings  = _load(os.path.join(acct_dir, "vpc-peering-connections.json")).get("VpcPeeringConnections", [])
    vpn_conns = _load(os.path.join(acct_dir, "VPN-connection.json")).get("VpnConnections", [])
    ram_assoc = _load(os.path.join(acct_dir, "RAM-Resources.json")).get("resourceShareAssociations", [])

    # -- Quick look‑ups --------------------------------------------------
    vpc_flow_set = {fl["ResourceId"] for fl in flows}

    tgw_map = defaultdict(list)
    for att in tgw_atts:
        if att.get("ResourceType") == "vpc":
            tgw_map[att["ResourceId"]].append(att["TransitGatewayId"])

    subs_by_vpc = defaultdict(list)
    for sn in subnets:
        subs_by_vpc[sn["VpcId"]].append(sn)

    # Subnet→RouteTable map
    rt_routes = {rt["RouteTableId"]: rt["Routes"] for rt in routes}
    subnet_to_rt = {}
    for rt in routes:
        for assoc in rt.get("Associations", []):
            if assoc.get("SubnetId"):
                subnet_to_rt[assoc["SubnetId"]] = rt["RouteTableId"]

    def subnet_type(subnet_id: str) -> str:
        rt_id = subnet_to_rt.get(subnet_id)
        if not rt_id:
            return "Unknown"
        for r in rt_routes.get(rt_id, []):
            if r.get("GatewayId", "").startswith("igw-"):
                return "Public"
        return "Private"

    # Endpoints by VPC
    ep_map = defaultdict(set)
    for ep in endpoints:
        ep_map[ep["VpcId"]].add(ep["ServiceName"].split(".")[-1])

    peering_set = {p["RequesterVpcInfo"]["VpcId"] for p in peerings} | {
        p["AccepterVpcInfo"]["VpcId"] for p in peerings
    }
    vpn_set = {v.get("VpcId") for v in vpn_conns if v.get("VpcId")}
    ram_set = {a.get("resourceArn", "").split("/")[-1] for a in ram_assoc}

    # -------------------------------------------------------------------
    # Build summary & rich deep dive
    # -------------------------------------------------------------------
    summary_rows = []
    deepdive_dict = {}  # key = vpcId → section dict

    for v in vpcs:
        vid   = v["VpcId"]
        vname = _tag_name(v.get("Tags", []))

        print("DEBUG: TGW Map =", dict(tgw_map))
        print(f"DEBUG: Endpoints for {vid} = {ep_map.get(vid)}")


        # cidr          = v.get("CidrBlock", "")
        # -- Collect ALL CIDR blocks (primary + associations)
        cidr_blocks = [assoc["CidrBlock"] for assoc in v.get("CidrBlockAssociationSet", [])]
        cidr = ", ".join(cidr_blocks) if cidr_blocks else v.get("CidrBlock", "")
        ipv6          = _yes_no(bool(v.get("Ipv6CidrBlockAssociationSet")))
        flow          = _yes_no(vid in vpc_flow_set)
        tgw_attached  = f"Yes ({', '.join(tgw_map[vid])})" if vid in tgw_map else "No"

        # Subnet counts
        pub = pri = 0
        for sn in subs_by_vpc[vid]:
            # (pub if subnet_type(sn["SubnetId"]) == "Public" else pri).__iadd__(1)
            if subnet_type(sn["SubnetId"]) == "Public":
                pub += 1
            else:
                pri += 1
        subnets_txt = f"{pub} Public, {pri} Private" if (pub or pri) else "None"

        # NAT / IGW presence
        nat = igw = False
        for rlist in rt_routes.values():
            for r in rlist:
                gw = r.get("GatewayId", "")
                nat = nat or gw.startswith("nat-")
                igw = igw or gw.startswith("igw-")

        endpoints_txt = ", ".join(sorted(ep_map.get(vid, []))) or "None"

        # --- Summary Row (flat) ----------------------------------------
        summary_rows.append(
            [vid, vname, region, cidr, ipv6, tgw_attached, flow, endpoints_txt, ""]
        )

        # --- Rich Deep Dive Sections ----------------------------------
        vpc_config_rows = [
            ["VPC ID", vid],
            ["VPC Name (tag)", vname],
            ["Region", region],
            ["CIDR Block", cidr],
            ["IPv6 Enabled", ipv6],
            ["DHCP Options", v.get("DhcpOptionsId", "default")],
            ["Default VPC", _yes_no(v.get("IsDefault", False))]
        ]

        subnet_rows = [
            [
                _tag_name(sn.get("Tags", [])),
                sn["CidrBlock"],
                sn["AvailabilityZone"],
                "Public" if subnet_type(sn["SubnetId"]) == "Public" else "Private",
                _yes_no(sn["MapPublicIpOnLaunch"]),
                sn["AvailableIpAddressCount"]
            ]
            for sn in subs_by_vpc[vid]
        ]

        route_summary_rows = []
        for rt in routes:
            assoc = []
            for a in rt.get("Associations", []):
                assoc.append("main" if a.get("Main") else a.get("SubnetId", ""))
            default_route = next(
                (r for r in rt["Routes"] if r.get("DestinationCidrBlock") == "0.0.0.0/0"),
                {},
            )
            route_summary_rows.append([
                rt["RouteTableId"],
                ", ".join(filter(None, assoc)),
                default_route.get("TransitGatewayId") or default_route.get("GatewayId", ""),
                "Has local + default routes"
            ])

        endpoint_rows = [
            [
                ep["ServiceName"].split(".")[-1],
                next((t["Value"] for t in ep.get("Tags", []) if t["Key"] == "Name"), ""),
                ", ".join(ep["SubnetIds"]),
                _yes_no(ep.get("PrivateDnsEnabled", False)),
                ep["Groups"][0]["GroupName"] if ep.get("Groups") else "",
                "Access to AWS service"
            ]
            for ep in endpoints if ep["VpcId"] == vid
        ]

        notes_rows = [
            ["Flow Logs", flow],
            ["Peering / VPN", _yes_no(vid in peering_set or vid in vpn_set)],
            ["Transit Gateway", tgw_attached],
            ["Resource Sharing", _yes_no(vid in ram_set)],
            ["Network Firewall", "No"],  # extend if parsed in future
            [
                "S3 Endpoint Limitation",
                "Private DNS disabled" if (
                    "s3" in endpoints_txt
                    and not any(
                        e.get("PrivateDnsEnabled") for e in endpoints
                        if e["VpcId"] == vid and "s3" in e["ServiceName"]
                    )
                ) else "None"
            ]
        ]

        deepdive_dict[vid] = {
            "config":    vpc_config_rows,
            "subnets":   subnet_rows,
            "routes":    route_summary_rows,
            "endpoints": endpoint_rows,
            "notes":     notes_rows,
        }

    return summary_rows, deepdive_dict


# -------------------------------------------------------------------
# CLI entry‑point
# -------------------------------------------------------------------
def run():
    print("\n🌐  AWS VPC Deep‑Dive Summary")
    net_root = input("Path to 'Networking' folder: ").strip()
    region   = input("Region for report (default us-east-1): ").strip() or "us-east-1"

    ts      = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out_dir = os.path.join("output", f"VPC_Summary_{ts}")
    os.makedirs(out_dir, exist_ok=True)

    summary_headers = [
        "VPC ID", "VPC Name (Tag)", "Region", "CIDR Block",
        "IPv6", "TGW Attached", "Flow Logs", "Endpoints", "Notes",
    ]
    all_summary_rows = []

    # -----------------------------------------------------------------
    # Iterate accounts (each subfolder under Networking root)
    # -----------------------------------------------------------------
    for acct_dir in glob.glob(os.path.join(net_root, "*")):
        if not os.path.isdir(acct_dir):
            continue
        acct_name = os.path.basename(acct_dir)
        print(f"\n🔄 Parsing account: {acct_name}")

        s_rows, deep_dict = parse_account(acct_dir, acct_name, region)
        all_summary_rows.extend(s_rows)

        # Write rich deep‑dives
        for vid, sections in deep_dict.items():
            export_rich_deep_dive(acct_name, vid, sections, out_dir)

    # -----------------------------------------------------------------
    # Export consolidated summary
    # -----------------------------------------------------------------
    if not all_summary_rows:
        print("❗  No VPCs found. Check folder path and filenames.")
        return

    export_table_csv_docx(
        all_summary_rows,
        summary_headers,
        os.path.join(out_dir, "vpcs_summary.csv"),
        os.path.join(out_dir, "vpcs_summary.docx"),
        "AWS VPC Summary (All Accounts)",
    )
    print(f"\n✅  All reports saved in: {out_dir}\n")


# -------------------------------------------------------------------
if __name__ == "__main__":
    run()
