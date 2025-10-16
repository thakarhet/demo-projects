import pandas as pd
import matplotlib.pyplot as plt
import time
from scapy.all import sniff, IP, TCP, UDP

# Process sniffed packets into DataFrame
def process_packets(packets):
    data = []
    for pkt in packets:
        if pkt.haslayer(IP):
            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            proto = pkt[IP].proto
            size = len(pkt)
            timestamp = pd.to_datetime(pkt.time, unit='s')

            src_port = pkt[TCP].sport if pkt.haslayer(TCP) else (pkt[UDP].sport if pkt.haslayer(UDP) else None)
            dst_port = pkt[TCP].dport if pkt.haslayer(TCP) else (pkt[UDP].dport if pkt.haslayer(UDP) else None)

            data.append({
                "timestamp": timestamp,
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "protocol": proto,
                "packet_size": size
            })
    return pd.DataFrame(data)

# Capture packets until threshold or time limit
def capture_until_threshold(threshold_packets=20000, batch_size=500, time_limit=120):
    df = pd.DataFrame()
    total = 0
    start_time = time.time()

    while total < threshold_packets and (time.time() - start_time) < time_limit:
        print(f"📡 Sniffing next {batch_size} packets... (total so far: {total})")
        packets = sniff(count=batch_size, timeout=5)
        new_df = process_packets(packets)
        df = pd.concat([df, new_df], ignore_index=True)
        total = len(df)

    print(f"\n✅ Capture complete. Total {total} packets in {int(time.time() - start_time)} seconds.")
    return df

# Detect anomalies in packet volume
def detect_anomalies(df):
    print("\nAnalyzing traffic patterns...")

    if df.empty:
        print("⚠️ No packets captured!")
        return

    # Summary
    print(f"\n📦 Total packets captured: {len(df)}")
    print(f"📡 Unique source IPs: {df['src_ip'].nunique()}")
    print(f"🎯 Unique destination IPs: {df['dst_ip'].nunique()}")
    print(f"🔌 Unique destination ports: {df['dst_port'].nunique()}")

    print("\nTop 5 source IPs by packet count:")
    print(df['src_ip'].value_counts().head().to_string())

    print("\nTop 5 destination ports by usage:")
    print(df['dst_port'].value_counts().head().to_string())

    # Group by second (packet count, not bytes)
    df['second'] = df['timestamp'].dt.floor('s')
    packets_per_sec = df.groupby('second').size()

    # Anomaly detection (spike threshold)
    threshold = 400 #packets_per_sec.mean() + 3 * packets_per_sec.std()
    anomalies = packets_per_sec[packets_per_sec > threshold]

    print("\n🔴 Traffic spikes detected at:")
    if anomalies.empty:
        print(" None")
    else:
        for t, count in anomalies.items():
            print(f" - {t}: {count} packets")

    # Rare destination ports
    port_counts = df['dst_port'].value_counts()
    rare_ports = port_counts[port_counts < 5]

    print("\n🟡 Rare destination ports:")
    if rare_ports.empty:
        print(" None")
    else:
        for port, count in rare_ports.items():
            print(f" - Port {port} → {count} connections")

    # 📊 Plot: Packets per second
    packets_per_sec.plot(title='Packets Captured per Second')
    plt.axhline(y=threshold, color='red', linestyle='--', label='Anomaly Threshold')
    plt.legend()
    plt.show()


# Example usage
if __name__ == "__main__":
    print("🔍 Capturing live packets until threshold or time limit...")
    df = capture_until_threshold(threshold_packets=20000, batch_size=500, time_limit=120)
    detect_anomalies(df)