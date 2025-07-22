import os
import json
import glob
import datetime
from collections import defaultdict
from common.utils import export_table_csv_docx


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _load(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}


def _yes_no(flag: bool) -> str:
    return "Yes" if flag else "No"


def _tag_name(tags):
    return {t["Key"]: t["Value"] for t in tags}.get("Name", "(No Name)")


# -------------------------------------------------------------------
# Per‑account parsing
# -------------------------------------------------------------------
def parse_account(acct_dir: str, account: str, region: str):
    """Return (summary_rows, deep_dive_rows_per_vpc)."""
    # ----------------------------------------------------------------
    # Load JSON blobs
    # ----------------------------------------------------------------
    vpcs = _load(os.path.join(acct_dir, "VPCS.json")).get("Vpcs", []) or \
           _load(os.path.join(acct_dir, "VPCS.json")).get("VPCs", [])

    subnets = _load(os.path.join(acct_dir, "subnet.json")).get("Subnets", [])
    routes = _load(os.path.join(acct_dir, "route-tables.json")).get("RouteTables", [])
    flows = _load(os.path.join(acct_dir, "flow-logs.json")).get("FlowLogs", [])
    tgw_atts = _load(os.path.join(acct_dir, "transit-gateway-attachments.json")).get(
        "TransitGatewayAttachments", []
    )
    endpoints = _load(os.path.join(acct_dir, "vpc-endpoints.json")).get("VpcEndpoints", [])
    peerings = _load(os.path.join(acct_dir, "vpc-peering-connections.json")).get(
        "VpcPeeringConnections", []
    )
    vpn_conns = _load(os.path.join(acct_dir, "VPN-connection.json")).get("VpnConnections", [])
    ram_assoc = _load(os.path.join(acct_dir, "RAM-Resources.json")).get(
        "resourceShareAssociations", []
    )

    # Quick look‑ups
    vpc_flow_set = {fl["ResourceId"] for fl in flows}
    tgw_map = defaultdict(list)
    for att in tgw_atts:
        if att.get("ResourceType") == "vpc":
            tgw_map[att["ResourceId"]].append(att["TransitGatewayId"])

    subs_by_vpc = defaultdict(list)
    for sn in subnets:
        subs_by_vpc[sn["VpcId"]].append(sn)

    # Route‑table helpers
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

    ep_map = defaultdict(set)
    for ep in endpoints:
        ep_map[ep["VpcId"]].add(ep["ServiceName"].split(".")[-1])

    peering_set = {p["RequesterVpcInfo"]["VpcId"] for p in peerings} | {
        p["AccepterVpcInfo"]["VpcId"] for p in peerings
    }
    vpn_set = {v.get("VpcId") for v in vpn_conns if v.get("VpcId")}
    ram_set = {a.get("resourceArn", "").split("/")[-1] for a in ram_assoc}

    summary_rows = []
    deepdive_dict = {}  # key = vpcId, value=list[[field,val], ... ]

    for v in vpcs:
        vid = v["VpcId"]
        vname = _tag_name(v.get("Tags", []))

        cidr = v.get("CidrBlock", "")
        ipv6 = _yes_no(bool(v.get("Ipv6CidrBlockAssociationSet")))
        flow = _yes_no(vid in vpc_flow_set)
        tgw_attached = (
            f"Yes ({', '.join(tgw_map[vid])})" if vid in tgw_map else "No"
        )

        # Subnet counts
        pub = pri = 0
        for sn in subs_by_vpc[vid]:
            if subnet_type(sn["SubnetId"]) == "Public":
                pub += 1
            else:
                pri += 1
        subnets_txt = f"{pub} Public, {pri} Private" if pub or pri else "None"

        # NAT / IGW presence
        nat = igw = False
        for rlist in rt_routes.values():
            for r in rlist:
                gw = r.get("GatewayId", "")
                if gw.startswith("nat-"):
                    nat = True
                if gw.startswith("igw-"):
                    igw = True

        endpoints_txt = ", ".join(sorted(ep_map.get(vid, []))) or "None"

        # --- Summary Row (flat) ---
        summary_rows.append(
            [
                vid,
                vname,
                region,
                cidr,
                ipv6,
                tgw_attached,
                flow,
                endpoints_txt,
                "",  # notes blank
            ]
        )

        # --- Deep Dive (vertical) ---
        deep_rows = [
            ["VPC ID", vid],
            ["VPC Name (tag)", vname],
            ["CIDR Block", cidr],
            ["IPv6 Enabled", ipv6],
            ["Flow Logs Enabled", flow],
            ["TGW Attached", tgw_attached],
            ["Subnets", subnets_txt],
            ["NAT Gateway", _yes_no(nat)],
            ["Internet Gateway", _yes_no(igw)],
            ["VPC Endpoints", endpoints_txt],
            ["Peering Connections", _yes_no(vid in peering_set)],
            ["VPN/DX Connectivity", _yes_no(vid in vpn_set)],
            ["RAM Shared Resources", _yes_no(vid in ram_set)],
            ["Notes", ""],
        ]
        deepdive_dict[vid] = deep_rows

    return summary_rows, deepdive_dict, account


# -------------------------------------------------------------------
# Entry‑point (called from main menu)
# -------------------------------------------------------------------
def run():
    print("\n🌐  AWS VPC Deep‑Dive Summary")
    net_root = input("Path to 'Networking' folder: ").strip()
    region = input("Region for report (default us-east-1): ").strip() or "us-east-1"

    ts = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out_dir = os.path.join("output", f"VPC_Summary_{ts}")
    os.makedirs(out_dir, exist_ok=True)

    summary_headers = [
        "VPC ID",
        "VPC Name (Tag)",
        "Region",
        "CIDR Block",
        "IPv6",
        "TGW Attached",
        "Flow Logs",
        "Endpoints",
        "Notes",
    ]
    all_summary_rows = []

    for acct_dir in glob.glob(os.path.join(net_root, "*")):
        if not os.path.isdir(acct_dir):
            continue
        acct_name = os.path.basename(acct_dir)
        s_rows, deep_dict, _ = parse_account(acct_dir, acct_name, region)
        all_summary_rows.extend(s_rows)

        # Write deep‑dive per VPC
        for vid, rows in deep_dict.items():
            export_table_csv_docx(
                rows,
                ["Field", "Value"],
                os.path.join(out_dir, f"deepdive_{acct_name}_{vid}.csv"),
                os.path.join(out_dir, f"deepdive_{acct_name}_{vid}.docx"),
                f"VPC Deep Dive – {acct_name} / {vid}",
            )

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

    print(f"✅  Reports saved in: {out_dir}\n")



