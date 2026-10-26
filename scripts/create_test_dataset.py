"""
Script to create sample computer networking dataset (data/test_networking.parquet).
Covering:
1. Firewall
2. DNS (Domain Name System)
3. TCP versus UDP
4. The OSI Model

This script creates data/test_networking.parquet without modifying or overwriting
existing training datasets in data/.
"""

import os
import pandas as pd

def create_test_dataset(output_path: str = "data/test_networking.parquet") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    records = [
        {
            "question": "What is a firewall and what are its primary types and functions in network security?",
            "answer": (
                "A firewall is a network security system that monitors, filters, and controls incoming "
                "and outgoing network traffic based on predetermined security rules. It establishes a protective "
                "barrier between a trusted internal network and untrusted external networks such as the Internet. "
                "The primary types of firewalls include: "
                "1. Packet filtering firewalls: inspect packet headers including source/destination IP addresses and port numbers. "
                "2. Stateful inspection firewalls: track the state of active network connections and determine which packets are allowed. "
                "3. Application-level gateways (proxy firewalls): operate at Layer 7 to inspect payload content for specific protocols. "
                "4. Next-Generation Firewalls (NGFW): integrate deep packet inspection, intrusion prevention systems (IPS), and application awareness."
            ),
            "expected_concepts": (
                "Traffic filtering and barrier between trusted and untrusted networks; "
                "Predefined security rules; "
                "Packet filtering based on IP and port numbers; "
                "Stateful inspection tracking connection states; "
                "Application layer proxies / Next-Generation Firewalls"
            ),
            "keywords": "firewall, packet filtering, stateful inspection, proxy, security rules, port numbers, ip address, trusted network",
            "max_marks": 5.0,
            "rubric": "1 mark for definition and purpose; 1 mark for security rules; 1 mark for packet filtering; 1 mark for stateful inspection; 1 mark for application proxy/NGFW."
        },
        {
            "question": "Explain the Domain Name System (DNS), its architecture, and the step-by-step resolution process.",
            "answer": (
                "The Domain Name System (DNS) is a hierarchical, distributed naming system that translates human-friendly "
                "domain names (such as www.example.com) into numerical IP addresses (such as 192.0.2.1) required for routing. "
                "DNS predominantly operates over UDP port 53 for queries, and TCP port 53 for zone transfers or large responses. "
                "The DNS hierarchy consists of: "
                "1. Root DNS servers: at the top of the hierarchy, directing queries to TLD servers. "
                "2. Top-Level Domain (TLD) servers: manage extensions like .com, .org, or country codes. "
                "3. Authoritative DNS servers: hold the actual resource records (A, AAAA, CNAME, MX) for specific domains. "
                "The resolution process involves a local recursive resolver querying the Root server, then the TLD server, "
                "and finally the Authoritative server, which returns the IP address to be cached by the resolver."
            ),
            "expected_concepts": (
                "Translating human-readable domain names to numerical IP addresses; "
                "Hierarchical and distributed architecture (Root, TLD, Authoritative servers); "
                "Recursive resolver query workflow; "
                "Use of UDP port 53 for standard queries; "
                "Resource records (A, AAAA, CNAME, MX) and caching"
            ),
            "keywords": "DNS, domain name, IP address, root server, TLD server, authoritative server, recursive resolver, UDP port 53, caching",
            "max_marks": 5.0,
            "rubric": "1 mark for definition and translation role; 1 mark for hierarchical server structure; 1 mark for recursive lookup steps; 1 mark for UDP port 53 usage; 1 mark for caching and record types."
        },
        {
            "question": "Compare and contrast TCP and UDP protocols at the Transport Layer.",
            "answer": (
                "Transmission Control Protocol (TCP) and User Datagram Protocol (UDP) are core Transport Layer protocols "
                "with distinct characteristics and tradeoffs: "
                "1. Connection state: TCP is a connection-oriented protocol that establishes a connection using a three-way "
                "handshake (SYN, SYN-ACK, ACK) before data transfer. UDP is connectionless and sends datagrams without prior setup. "
                "2. Reliability: TCP guarantees reliable delivery through acknowledgments (ACKs), sequence numbers, and retransmission "
                "of lost packets. UDP is unreliable, providing best-effort delivery without acknowledgments or retransmission. "
                "3. Flow and Congestion Control: TCP implements sliding window flow control and congestion avoidance mechanisms; "
                "UDP has no flow or congestion control. "
                "4. Header overhead: TCP has a larger header (20-60 bytes) due to control flags, whereas UDP has a lightweight 8-byte header. "
                "5. Use cases: TCP is used where data accuracy is critical (HTTP/HTTPS, FTP, SSH, SMTP). UDP is used where speed "
                "and low latency are paramount (VoIP, DNS queries, live video streaming, online gaming)."
            ),
            "expected_concepts": (
                "TCP is connection-oriented (three-way handshake) while UDP is connectionless; "
                "TCP provides guaranteed reliability with acknowledgments and retransmissions, UDP is best-effort; "
                "Flow and congestion control present in TCP and absent in UDP; "
                "Header overhead comparison (TCP 20-60 bytes vs UDP 8 bytes); "
                "Appropriate use cases (TCP for web/file transfer, UDP for real-time streaming/VoIP/DNS)"
            ),
            "keywords": "TCP, UDP, connection-oriented, connectionless, three-way handshake, reliability, acknowledgment, retransmission, sliding window, header overhead, low latency",
            "max_marks": 5.0,
            "rubric": "1 mark for connection-oriented vs connectionless (handshake); 1 mark for reliability and retransmission; 1 mark for flow and congestion control; 1 mark for header overhead; 1 mark for use case contrast."
        },
        {
            "question": "Describe the 7 layers of the OSI reference model and the primary function of each layer.",
            "answer": (
                "The Open Systems Interconnection (OSI) model is a conceptual 7-layer framework developed by ISO to standardize "
                "network communications from hardware to application software: "
                "1. Layer 1 - Physical Layer: Transmits raw bitstreams over a physical medium (cables, radio frequencies, connectors, hubs). "
                "2. Layer 2 - Data Link Layer: Handles node-to-node frame delivery, MAC addressing, framing, and error detection (Ethernet, switches). "
                "3. Layer 3 - Network Layer: Responsible for packet routing, logical IP addressing, and path determination across subnets (Routers, IP, ICMP). "
                "4. Layer 4 - Transport Layer: Manages end-to-end communication, segmentation, flow control, and error recovery (TCP, UDP). "
                "5. Layer 5 - Session Layer: Establishes, manages, and terminates communication sessions between applications (RPC, NetBIOS). "
                "6. Layer 6 - Presentation Layer: Handles data translation, character encoding, compression, and encryption/decryption (SSL/TLS, ASCII, JPEG). "
                "7. Layer 7 - Application Layer: Provides network services directly to end-user software applications (HTTP, FTP, DNS, SMTP)."
            ),
            "expected_concepts": (
                "Conceptual 7-layer framework by ISO; "
                "Layer 1 Physical: raw bitstream transmission and hardware signals; "
                "Layer 2 Data Link: framing, MAC addressing, switch operations; "
                "Layer 3 Network: logical IP addressing and packet routing across networks; "
                "Layer 4 Transport: end-to-end transport, segmentation, TCP/UDP; "
                "Layer 5 Session: session establishment and termination; "
                "Layer 6 Presentation: data formatting, encryption, compression; "
                "Layer 7 Application: direct interface to user applications (HTTP, SMTP, DNS)"
            ),
            "keywords": "OSI model, Physical layer, Data Link layer, Network layer, Transport layer, Session layer, Presentation layer, Application layer, MAC address, IP routing, TCP, UDP",
            "max_marks": 7.0,
            "rubric": "1 mark for general definition and ISO structure; 1 mark per layer group/function accurately explained."
        }
    ]

    df = pd.DataFrame(records)
    df.to_parquet(output_path, index=False)
    print(f"Successfully created test dataset with {len(df)} records at: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_dataset()
