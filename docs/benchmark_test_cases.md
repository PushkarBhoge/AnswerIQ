# AnswerIQ – Performance Rating and Natural-language Intelligent Text Assessment
### Benchmark Computer Networking Test Cases

This document contains **10 benchmark test cases** spanning different mark allocations (**2, 3, 4, 5, 7, and 10 marks**). All questions, concepts, and answers are grounded in the local `data/train-00000-of-00001.parquet` dataset.

Use these test cases to evaluate AnswerIQ in the web interface at `http://127.0.0.1:5000`.

---

## Table of Contents

1. [ARP (Address Resolution Protocol) — 2 Marks](#1-arp-address-resolution-protocol--2-marks)
2. [CSMA/CD vs. CSMA/CA — 3 Marks](#2-csmacd-vs-csmaca--3-marks)
3. [DHCP DORA Process — 4 Marks](#3-dhcp-dora-process--4-marks)
4. [VLANs and 802.1Q Trunking — 4 Marks](#4-vlans-and-8021q-trunking--4-marks)
5. [NAT and PAT (Network Address Translation) — 5 Marks](#5-nat-and-pat-network-address-translation--5-marks)
6. [OSPF vs. RIP (Link-State vs. Distance-Vector) — 5 Marks](#6-ospf-vs-rip-link-state-vs-distance-vector--5-marks)
7. [TCP Three-Way Handshake & Connection Teardown — 5 Marks](#7-tcp-three-way-handshake--connection-teardown--5-marks)
8. [Subnetting, CIDR, and VLSM — 5 Marks](#8-subnetting-cidr-and-vlsm--5-marks)
9. [Spanning Tree Protocol (STP IEEE 802.1D) — 7 Marks](#9-spanning-tree-protocol-stp-ieee-8021d--7-marks)
10. [End-to-End Packet Lifecycle Across the OSI Model — 10 Marks](#10-end-to-end-packet-lifecycle-across-the-osi-model--10-marks)

---

### 1. ARP (Address Resolution Protocol) — 2 Marks

* **Question:**
  ```text
  What is the Address Resolution Protocol (ARP) and what is its primary role in local network communication?
  ```
* **Maximum Marks:** `2.0`
* **Student's Answer:**
  ```text
  The Address Resolution Protocol (ARP) is a Network Layer/Data Link Layer protocol used to dynamically resolve a known Layer 3 logical IP address into its corresponding Layer 2 physical MAC address on a local Ethernet segment. When a host needs to transmit a packet to an IP on the local subnet, it broadcasts an ARP Request ("Who has IP X.X.X.X? Tell MAC Y"). The target device recognizes its IP and returns a unicast ARP Reply containing its hardware MAC address, which the sending host stores in its local ARP cache table to avoid continuous broadcast overhead.
  ```
* **Expected Result:** High Score (~2.0/2.0). Matches concept on Layer 2 MAC resolution and broadcast request/unicast reply.

---

### 2. CSMA/CD vs. CSMA/CA — 3 Marks

* **Question:**
  ```text
  Compare Carrier Sense Multiple Access with Collision Detection (CSMA/CD) and Collision Avoidance (CSMA/CA).
  ```
* **Maximum Marks:** `3.0`
* **Student's Answer:**
  ```text
  CSMA/CD and CSMA/CA are medium access control methods designed for shared media:
  1. Medium & Standards: CSMA/CD is used in legacy half-duplex wired Ethernet (IEEE 802.3), whereas CSMA/CA is used in wireless networks (IEEE 802.11 Wi-Fi) where transceivers cannot transmit and listen simultaneously.
  2. Operational Mechanism: In CSMA/CD, devices listen to the wire while transmitting; if a voltage spike indicates a collision, transmission halts immediately, a jam signal is sent, and devices wait for a random backoff time using truncated binary exponential backoff. In CSMA/CA, collisions cannot be reliably detected over radio frequencies, so devices attempt to avoid collisions beforehand using Interframe Spaces (DIFS/SIFS), random backoff counters, and optional RTS/CTS (Request to Send / Clear to Send) reservation frames.
  ```
* **Expected Result:** Full marks (~3.0/3.0). Accurately distinguishes wired collision detection and wireless collision avoidance.

---

### 3. DHCP DORA Process — 4 Marks

* **Question:**
  ```text
  Explain the step-by-step DORA process used by DHCP to dynamically allocate IP configuration to client hosts.
  ```
* **Maximum Marks:** `4.0`
* **Student's Answer:**
  ```text
  Dynamic Host Configuration Protocol (DHCP) operates over UDP ports 67 (server) and 68 (client) through a four-step handshake known as DORA:

  1. Discover (DHCPDISCOVER): A newly joined client broadcasts a message with source IP 0.0.0.0 and destination IP 255.255.255.255 to locate any available DHCP servers on the local subnet.
  2. Offer (DHCPOFFER): Receiving DHCP servers reserve an available IP address from their configured pool and send an offer containing the proposed IP, subnet mask, lease duration, default gateway, and DNS servers.
  3. Request (DHCPREQUEST): The client selects one server's offer and broadcasts a formal request announcing its choice, simultaneously releasing any alternative offers back to other servers.
  4. Acknowledge (DHCPACK): The chosen server confirms the lease by transmitting a DHCPACK unicast or broadcast packet containing the final binding parameters. The client commits the IP to its network interface and begins normal IP communication.
  ```
* **Expected Result:** Full marks (~4.0/4.0). All four DORA steps clearly detailed with UDP port usage and IP configuration parameters.

---

### 4. VLANs and 802.1Q Trunking — 4 Marks

* **Question:**
  ```text
  What is a Virtual LAN (VLAN), and how does the IEEE 802.1Q standard achieve inter-switch trunking?
  ```
* **Maximum Marks:** `4.0`
* **Student's Answer:**
  ```text
  A Virtual LAN (VLAN) is a logical partitioning of a physical Layer 2 switch into multiple distinct broadcast domains. Devices grouped in the same VLAN communicate as if they were on an isolated switch, reducing broadcast radiation, enhancing security, and simplifying network administration without altering physical cabling.

  When traffic spans multiple switches, an 802.1Q trunk port multiplexes frames from different VLANs across a single physical link. The IEEE 802.1Q standard inserts a 4-byte tag into the standard Ethernet frame header (between the Source MAC and EtherType fields). This tag contains a 12-bit VLAN Identifier (VID), allowing up to 4,094 distinct VLANs. The receiving switch inspects the 802.1Q tag, identifies the source VLAN, removes the tag (untags), and switches the frame exclusively to access ports belonging to that specific VLAN. Untagged frames traversing a trunk link are automatically assigned to the designated Native VLAN (default VLAN 1).
  ```
* **Expected Result:** High Score (~3.8 - 4.0/4.0). Covers broadcast isolation, 4-byte 802.1Q header tag, 12-bit VID (4094 limit), and native VLAN.

---

### 5. NAT and PAT (Network Address Translation) — 5 Marks

* **Question:**
  ```text
  Explain Network Address Translation (NAT) and Port Address Translation (PAT), including their operational types and benefits.
  ```
* **Maximum Marks:** `5.0`
* **Student's Answer:**
  ```text
  Network Address Translation (NAT) is a technique standardized to preserve the depleting IPv4 address space by translating private, non-routable IP addresses (defined in RFC 1918) into globally routable public IP addresses:

  1. Static NAT: Provides a consistent 1-to-1 mapping between a private IP and an assigned public IP. Primarily used for hosting internal servers (such as public web or email servers) that need to be reachable from the external Internet.
  2. Dynamic NAT: Maps private IPs to a pool of available public IP addresses on a first-come, first-served basis. When the session terminates, the public IP returns to the pool for reuse.
  3. Port Address Translation (PAT / NAT Overload): The most prevalent implementation where multiple internal private hosts share a single public IP address. The router differentiates concurrent connections by assigning unique Layer 4 source port numbers (from the ephemeral port range 1024-65535) in its NAT translation table.
  4. Key Benefits: Extends IPv4 operational longevity, hides internal network topology from external inspection providing a baseline security boundary, and prevents extensive IP renumbering when switching internet service providers (ISPs).
  ```
* **Expected Result:** Full marks (~4.8 - 5.0/5.0). Explains Static NAT, Dynamic NAT, PAT / Overload port mapping, and IPv4 preservation.

---

### 6. OSPF vs. RIP (Link-State vs. Distance-Vector) — 5 Marks

* **Question:**
  ```text
  Compare OSPF (Open Shortest Path First) and RIP (Routing Information Protocol) in terms of algorithm, metric, convergence, and scalability.
  ```
* **Maximum Marks:** `5.0`
* **Student's Answer:**
  ```text
  OSPF and RIP represent two fundamental interior gateway routing protocol architectures:

  1. Algorithm: RIP uses the distance-vector Bellman-Ford algorithm, where routers know only the distance and direction to destinations reported by immediate neighbors. OSPF is a link-state protocol that uses Dijkstra’s Shortest Path First (SPF) algorithm, allowing every router in an area to construct an identical topological map of the entire network.
  2. Routing Metric: RIP relies solely on hop count, arbitrarily capping paths at a maximum of 15 hops (16 is unreachable). OSPF calculates path cost inversely proportional to link bandwidth (Cost = Reference Bandwidth / Interface Bandwidth), accurately favoring faster Gigabit links over slow serial lines.
  3. Convergence & Updates: RIP periodically broadcasts or multicasts its complete routing table every 30 seconds, resulting in slow convergence and vulnerability to routing loops. OSPF uses triggered, incremental Link-State Advertisements (LSAs) sent to multicast addresses 224.0.0.5 and 224.0.0.6 only when topology changes occur, converging within milliseconds.
  4. Scalability & Hierarchy: RIP is limited to flat, small networks with fewer than 15 hops. OSPF scales across enterprise networks by supporting a two-tier hierarchical design consisting of a central Backbone Area 0 and attached non-backbone areas to localize LSA flooding.
  ```
* **Expected Result:** Full marks (~5.0/5.0). Contrast on all 4 dimensions (Bellman-Ford vs Dijkstra, Hop count vs Cost, periodic vs triggered LSAs, hierarchy Area 0).

---

### 7. TCP Three-Way Handshake & Connection Teardown — 5 Marks

* **Question:**
  ```text
  Describe the TCP Three-Way Handshake connection establishment and the Four-Way Handshake connection termination processes.
  ```
* **Maximum Marks:** `5.0`
* **Student's Answer:**
  ```text
  Transmission Control Protocol (TCP) provides reliable, connection-oriented communication through explicit connection state transitions:

  1. Three-Way Handshake (Connection Establishment):
     - Step 1 (SYN): The client selects an Initial Sequence Number (ISN_c) and sends a TCP segment with the SYN flag enabled to the server, transitioning to the SYN-SENT state.
     - Step 2 (SYN-ACK): The server receives the SYN, allocates connection buffers, chooses its own sequence number (ISN_s), and responds with SYN and ACK flags set (acknowledging ISN_c + 1), entering SYN-RECEIVED.
     - Step 3 (ACK): The client receives the SYN-ACK and returns an ACK segment acknowledging ISN_s + 1. Both endpoints are now in the ESTABLISHED state and full-duplex data transfer begins.

  2. Four-Way Handshake (Connection Teardown):
     - Step 1 (FIN): When an endpoint finishes sending data, it transmits a segment with the FIN flag set and moves to the FIN-WAIT-1 state.
     - Step 2 (ACK): The receiver acknowledges the FIN with an ACK segment and enters the CLOSE-WAIT state, while the sender moves to FIN-WAIT-2.
     - Step 3 (FIN): Once the receiving application finishes draining its pending transmission buffers, it sends its own FIN segment and enters LAST-ACK.
     - Step 4 (ACK): The original sender returns a final ACK segment and enters the TIME-WAIT state (typically lasting 2 * Maximum Segment Lifetime / 2MSL) to ensure the final ACK was delivered and to allow lingering duplicate packets to expire before closing the socket.
  ```
* **Expected Result:** High marks (~4.8 - 5.0/5.0). Details SYN, SYN-ACK, ACK, and FIN-ACK sequences along with TCP states (ESTABLISHED, TIME-WAIT).

---

### 8. Subnetting, CIDR, and VLSM — 5 Marks

* **Question:**
  ```text
  Explain Classless Inter-Domain Routing (CIDR) and Variable-Length Subnet Masking (VLSM), including their advantages over classful addressing.
  ```
* **Maximum Marks:** `5.0`
* **Student's Answer:**
  ```text
  Classless Inter-Domain Routing (CIDR) and Variable-Length Subnet Masking (VLSM) replaced legacy classful addressing (Class A, B, and C) to optimize IP address allocation:

  1. Classful Inefficiencies: Classful addressing imposed rigid 8, 16, or 24-bit network boundaries (/8, /16, /24), leading to massive address waste (e.g., assigning a Class B network with 65,534 host addresses to an organization requiring only 500 hosts).
  2. CIDR (RFC 1519): Eliminates fixed class boundaries by pairing an IP address with an arbitrary prefix length (e.g., 192.168.1.0/27). CIDR introduces route summarization (supernetting), allowing multiple contiguous routing prefixes to be consolidated into a single route entry in global internet routing tables, preventing route table explosion.
  3. VLSM: Enables network engineers to apply different subnet mask lengths across subnets within the same classful network space. For instance, assigning a /24 subnet to a department with 200 users while allocating a /30 subnet (offering exactly 2 usable host IPs) to point-to-point router links, minimizing unused IP waste.
  4. Protocol Requirements: VLSM and CIDR require classless routing protocols (such as RIPv2, OSPF, EIGRP, and BGP) that include the subnet mask alongside the network address inside routing update advertisements.
  ```
* **Expected Result:** High marks (~4.7 - 5.0/5.0). Clear contrast with classful addressing, prefix notation (/27, /30), and route aggregation.

---

### 9. Spanning Tree Protocol (STP IEEE 802.1D) — 7 Marks

* **Question:**
  ```text
  Describe the Spanning Tree Protocol (STP IEEE 802.1D), the problems it prevents in switched networks, its port states, and the Root Bridge election process.
  ```
* **Maximum Marks:** `7.0`
* **Student's Answer:**
  ```text
  The Spanning Tree Protocol (STP, standardized under IEEE 802.1D) is a Layer 2 link-management protocol that provides path redundancy while preventing fatal network loops in bridged Ethernet topologies.

  1. Problems Prevented:
     - Broadcast Storms: In looped Layer 2 topologies without STP, broadcast frames (such as ARP Requests) circulate endlessly, consuming switch CPU cycles and saturating link bandwidth until network collapse.
     - Multiple Frame Copies: Unicast frames with unlearned destination MACs are repeatedly duplicated and delivered to destination hosts multiple times.
     - MAC Database Instability (Flapping): Switches repeatedly overwrite their CAM tables with conflicting port mappings as identical source MAC frames arrive on multiple interfaces.

  2. Root Bridge Election:
     Switches exchange Bridge Protocol Data Units (BPDUs) every 2 seconds. The switch with the lowest Bridge ID (BID) is elected Root Bridge. The BID consists of a Bridge Priority (default 32768, configurable in increments of 4096) combined with the switch's base MAC address. If priorities tie, the lowest MAC address breaks the tie.

  3. Port Roles:
     - Root Port (RP): One port on each non-root switch with the lowest root path cost to the Root Bridge.
     - Designated Port (DP): One port per network segment with the best path cost forwarding traffic onto that segment.
     - Non-Designated / Blocking Port: Ports that receive BPDUs but are placed into a blocking state to break the loop.

  4. IEEE 802.1D Port States:
     - Blocking: Receives BPDUs only; drops user data frames to prevent loops.
     - Listening (15s): Prepares to forward; processes BPDUs to determine topology, but does not learn MAC addresses or forward user data.
     - Learning (15s): Populates the MAC address table from incoming source frames, but does not yet forward user data.
     - Forwarding: Normal operational state; learns MAC addresses and forwards user data frames.
     - Disabled: Administratively shut down.
  ```
* **Expected Result:** High marks (~6.5 - 7.0/7.0). Thorough coverage of loop hazards (broadcast storms, MAC flapping), Root Bridge election (BID, priority 32768, MAC tiebreak), port roles (RP, DP, Blocking), and 5 IEEE 802.1D port states with timer durations.

---

### 10. End-to-End Packet Lifecycle Across the OSI Model — 10 Marks

* **Question:**
  ```text
  Trace the complete end-to-end lifecycle of a web request when a client accesses "http://www.example.com", detailing data encapsulation and decapsulation across all 7 layers of the OSI model and all intermediate network devices.
  ```
* **Maximum Marks:** `10.0`
* **Student's Answer:**
  ```text
  The transmission of an HTTP request involves multi-layer protocol coordination, encapsulation, routing, and decapsulation from client to server:

  1. Application Layer (Layer 7):
     The client's browser formats an HTTP GET request message specifying the target URI and headers.

  2. DNS Resolution (Layers 7, 4, 3, 2):
     Before transmitting the HTTP request, the client must resolve "www.example.com" to an IP address. The OS checks its local cache and hosts file. If absent, the client constructs a DNS query encapsulated in a UDP datagram directed to destination port 53 of its configured DNS resolver, which recursively resolves and returns the server's public IP (e.g., 93.184.216.34).

  3. Transport Layer (Layer 4):
     The client opens a reliable connection via the TCP Three-Way Handshake. The Transport Layer encapsulates the HTTP data into a TCP segment, assigning a random client ephemeral source port (e.g., 51234) and destination port 80 (HTTP), while managing sequence numbers, acknowledgment numbers, and window sizing.

  4. Network Layer (Layer 3):
     The TCP segment is passed to the Network Layer and encapsulated into an IP packet. The IP header specifies the client's private IP as the Source IP and 93.184.216.34 as the Destination IP, along with a Time-To-Live (TTL) counter and protocol flag 6 (TCP).

  5. Data Link Layer (Layer 2) & ARP:
     The client determines that the destination IP is on a remote subnet by comparing it against its local subnet mask. Therefore, the packet must be forwarded to the Default Gateway router. The client checks its ARP cache for the gateway's IP; if missing, an ARP broadcast resolves the gateway's MAC address. The IP packet is then encapsulated into an Ethernet frame with the client's NIC as Source MAC and the Gateway's interface as Destination MAC. A Frame Check Sequence (FCS) cyclic redundancy check is appended.

  6. Physical Layer (Layer 1):
     The Ethernet frame is converted into electrical, optical, or radio bitstream signals and transmitted over the physical medium (twisted-pair Cat6 or Wi-Fi).

  7. Intermediate Switching & Routing:
     - Local Switch (Layer 2): Receives bits, checks FCS integrity, inspects Destination MAC, consults its CAM table, and forwards the frame out the specific port connected to the gateway router.
     - Gateway Router (Layer 3): Receives the frame, strips Layer 2 framing (decapsulation), checks the IP packet header, decrements the TTL, inspects its routing table for the best matching route prefix, and performs NAT translation (translating client private IP to its public WAN IP). It then re-encapsulates the packet into a new Layer 2 frame with the next-hop router's MAC address. This hop-by-hop re-encapsulation repeats across internet backbone routers.

  8. Server Receiving, Decapsulation, and Response:
     The web server receives the bitstream at Layer 1, verifies FCS and strips Ethernet headers at Layer 2, verifies destination IP at Layer 3, decapsulates the TCP segment and reorders sequences at Layer 4, and passes the reconstructed HTTP payload to the web server daemon at Layer 7. The server processes the GET request and generates an HTTP 200 OK response, which travels back along the reverse path through identical encapsulation steps.
  ```
* **Expected Result:** High marks (~9.0 - 10.0/10.0). Exhaustive end-to-end explanation tracing DNS lookup (UDP 53), TCP handshake, Layer 3 IP addressing, Layer 2 ARP & MAC encapsulation, Layer 1 signaling, intermediate Layer 2 switch forwarding & Layer 3 NAT routing, and server decapsulation.
