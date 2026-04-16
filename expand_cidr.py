#!/usr/bin/env python3
"""
分层采样：按运营商类型保留 IP，控制输出文件大小在 500KB 左右
"""

import ipaddress
import random
import os

# 输入输出文件
INPUT_FILE = "ipv4cidr.txt"
OUTPUT_FILE = "iplist_full.txt"

# 每类运营商保留的数量（总计约 50000 个 IP，文件大小约 500KB）
SAMPLE_PER_ISP = {
    'telecom': 15000,   # 电信
    'unicom': 15000,    # 联通
    'mobile': 15000,    # 移动
    'other': 5000       # 其他/多线
}

RANDOM_SEED = 42  # 固定随机种子，保证每次结果可复现


def detect_isp(ip):
    """根据 IP 前缀判断运营商"""
    if not ip:
        return 'other'
    
    if (ip.startswith('104.16') or ip.startswith('104.18') or 
        ip.startswith('104.19') or ip.startswith('104.28')):
        return 'mobile'
    
    if (ip.startswith('172.64') or ip.startswith('172.67') or 
        ip.startswith('104.23') or ip.startswith('104.31')):
        return 'unicom'
    
    if (ip.startswith('162.159') or ip.startswith('104.20') or 
        ip.startswith('104.22')):
        return 'telecom'
    
    return 'other'


def expand_and_sample():
    """展开 CIDR 并分层采样"""
    print("🔄 开始展开 CIDR 列表...")
    
    # 分类存储
    ip_pools = {'telecom': [], 'unicom': [], 'mobile': [], 'other': []}
    
    # 读取 CIDR 文件
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 文件不存在: {INPUT_FILE}")
        return 0
    
    with open(INPUT_FILE, 'r') as f:
        lines = f.readlines()
    
    total_cidr = 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        try:
            network = ipaddress.ip_network(line, strict=False)
            total_cidr += 1
            
            # 展开所有 IP
            for ip in network.hosts():
                ip_str = str(ip)
                isp = detect_isp(ip_str)
                ip_pools[isp].append(ip_str)
                
        except Exception as e:
            print(f"   ⚠️ 跳过无效 CIDR {line}: {e}")
    
    print(f"\n📊 CIDR 段数: {total_cidr}")
    print("📊 原始 IP 分布:")
    
    total_raw = 0
    for isp, ips in ip_pools.items():
        print(f"   {isp}: {len(ips)} 个")
        total_raw += len(ips)
    print(f"   总计: {total_raw} 个")
    
    # 分层采样
    print("\n🎲 开始分层采样...")
    random.seed(RANDOM_SEED)
    
    sampled = []
    for isp, target in SAMPLE_PER_ISP.items():
        pool = ip_pools[isp]
        if len(pool) == 0:
            print(f"   {isp}: 无数据，跳过")
            continue
        
        if len(pool) > target:
            selected = random.sample(pool, target)
            sampled.extend(selected)
            print(f"   {isp}: 采样 {target} / {len(pool)}")
        else:
            sampled.extend(pool)
            print(f"   {isp}: 保留全部 {len(pool)}")
    
    # 打乱顺序，避免连续同运营商
    random.shuffle(sampled)
    
    # 写入文件
    with open(OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(sampled))
    
    file_size_kb = len('\n'.join(sampled)) / 1024
    file_size_mb = file_size_kb / 1024
    
    print(f"\n✅ 完成！")
    print(f"📁 输出文件: {OUTPUT_FILE}")
    print(f"📦 文件大小: {file_size_kb:.1f} KB ({file_size_mb:.2f} MB)")
    print(f"🔢 IP 数量: {len(sampled)}")
    
    return len(sampled)


if __name__ == "__main__":
    expand_and_sample()
