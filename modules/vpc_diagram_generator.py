from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, PrivateSubnet, TransitGateway
from diagrams.generic.network import VPN as VPCEndpoint
from diagrams.aws.compute import EC2
import os

def generate_vpc_diagram(account_name: str, vpc_id: str, vpc_name: str, section_tables: dict[str, list[list[str]]], out_dir: str):
    diagram_title = f"{account_name}_{vpc_id}"
    diagram_path = os.path.join(out_dir, f"diagram_{diagram_title}.png")

    with Diagram(diagram_title, filename=diagram_path.replace(".png", ""), outformat="png", show=False, direction="TB"):
        vpc_node = VPC(vpc_name)

        # Track subnets to attach endpoints to
        subnet_nodes = {}

        with Cluster("Subnets"):
            for subnet_row in section_tables.get("subnets", []):
                subnet_id = subnet_row[0]
                subnet_label = f"{subnet_row[1]}\n{subnet_row[2]}"
                sn_node = PrivateSubnet(subnet_label)
                vpc_node >> sn_node

                # Add EC2 placeholder to each subnet
                ec2_node = EC2("EC2")
                sn_node >> ec2_node

                subnet_nodes[subnet_id] = sn_node

        # Endpoints
        for ep_row in section_tables.get("endpoints", []):
            svc = ep_row[0]
            ep_name = ep_row[1]
            subnets_str = ep_row[2]
            subnet_ids = subnets_str.split(", ") if subnets_str else []

            for subnet_id in subnet_ids:
                sn_node = subnet_nodes.get(subnet_id)
                if sn_node:
                    ep_node = VPCEndpoint(f"{ep_name}")
                    sn_node >> ep_node

        # Transit Gateway if present
        notes = section_tables.get("notes", [])
        for row in notes:
            if row[0].lower() == "transit gateway" and "yes" in row[1].lower():
                tgw = TransitGateway("Transit Gateway")
                vpc_node >> tgw
                break

    print(f"   •  Diagrams PNG generated: {diagram_path}")
    return diagram_path
