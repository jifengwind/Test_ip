
#!/usr/bin/env python3
"""
将 CIDR 列表展开为完整的 IP 地址列表
"""

import ipaddress
import sys

# 输入输出文件
INPUT_FILE = "ipv4cidr.txt"
OUTPUT_FILE = "iplist_full.txt"

def expand_cidr_file():
    """读取 CIDR 文件，展开为 IP 列表"""
    ips = []
    
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                # 解析 CIDR
                network = ipaddress.ip_network(line, strict=False)
                # 展开所有 IP（排除网络地址和广播地址）
                for ip in network.hosts():
                    ips.append(str(ip))
                print(f"  展开 {line}: {network.num_addresses - 2} 个 IP")
            except Exception as e:
                print(f"  跳过无效 CIDR {line}: {e}")
    
    # 写入文件
    with open(OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(ips))
    
    print(f"\n✅ 共展开 {len(ips)} 个 IP，已保存到 {OUTPUT_FILE}")
    return len(ips)

if __name__ == "__main__":
    print("🔄 开始展开 CIDR 列表...")
    count = expand_cidr_file()
    print(f"📁 完成！共 {count} 个 IP")
