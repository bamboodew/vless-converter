import urllib.parse
import yaml
import argparse
from typing import Any, Dict, List, Optional

# --- 常量定义 ---
VLESS_PREFIX = "vless://"
DEFAULT_INPUT_FILE = "nodes.txt"
DEFAULT_OUTPUT_FILE = "clash_meta_from_txt.yaml"
NODE_TYPE_VLESS = "vless"
NETWORK_WS = "ws"
NETWORK_GRPC = "grpc"
SECURITY_TLS = "tls"

def parse_vless(vless_url: str) -> Dict[str, Any]:
    """解析单个 VLESS 链接为 Clash.Meta 节点配置"""
    name: Optional[str] = None
    
    if not vless_url.startswith(VLESS_PREFIX):
        raise ValueError(f"不是有效的 VLESS 链接: {vless_url}")

    # 1. 分离并解析节点名称 (fragment)
    if "#" in vless_url:
        vless_url, custom_name = vless_url.split("#", 1)
        name = urllib.parse.unquote(custom_name)
    
    raw = vless_url[len(VLESS_PREFIX):]
    
    # 2. 提取 UUID 和服务器信息
    uuid, rest = raw.split("@", 1)
    
    # 3. 分离服务器地址、端口和查询参数
    if "?" in rest:
        server_port, params_str = rest.split("?", 1)
    else:
        server_port = rest
        params_str = ""
        
    server, port_str = server_port.split(":")
    port = int(port_str)
    
    # 4. 解析查询参数
    query = urllib.parse.parse_qs(params_str)
    security = query.get("security", ["none"])[0]
    network = query.get("type", [NETWORK_WS])[0]
    host = query.get("host", [server])[0]
    path = query.get("path", ["/"])[0]
    
    # 5. 如果链接中没有名称，则使用 host 或 server 作为备用名称
    if not name:
        name = host or server

    # 6. 构建基础节点配置
    node_config = {
        "name": name,
        "type": NODE_TYPE_VLESS,
        "server": server,
        "port": port,
        "uuid": uuid,
        "network": network,
        "tls": security == SECURITY_TLS,
        "udp": True,
        "sni": host,
    }

    # 7. 根据网络类型添加特定配置
    if network == NETWORK_WS:
        node_config["ws-opts"] = {
            "path": path,
            "headers": {"Host": host}
        }
    elif network == NETWORK_GRPC:
        service_name = query.get("serviceName", [""])[0]
        node_config["grpc-opts"] = {
            "grpc-service-name": service_name
        }
        
    return node_config

def vless_txt_to_clash(txt_file: str, output_file: str) -> None:
    """从 txt 文件批量生成 Clash.Meta 配置"""
    proxies: List[Dict[str, Any]] = []
    
    try:
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ 错误: 输入文件 '{txt_file}' 未找到。")
        return

    for idx, line in enumerate(lines, start=1):
        try:
            proxy = parse_vless(line)
            # 如果解析后仍然没有名字（例如，链接中既没有 #name 也没有 host），则使用默认编号
            if not proxy.get("name"):
                proxy["name"] = f"节点_{idx}"
            
            proxies.append(proxy)
        except Exception as e:
            print(f"⚠️ 跳过无效链接: {line}\n   原因: {e}")

    if not proxies:
        print("🤷 未找到任何有效节点，不生成配置文件。")
        return

    proxy_names = [p["name"] for p in proxies]

    config = {
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": "Proxy",
                "type": "select",
                "proxies": proxy_names
            }
        ],
        "rules": [
            "GEOIP,CN,DIRECT",
            "MATCH,Proxy"
        ]
    }

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"✅ 已成功生成 Clash.Meta 配置文件: {output_file}")
    print(f"   共包含 {len(proxies)} 个节点。")

def main() -> None:
    """主函数，处理命令行参数并启动转换"""
    parser = argparse.ArgumentParser(
        description="从包含 VLESS 链接的文本文件生成 Clash.Meta 配置文件。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-i", "--input", 
        default=DEFAULT_INPUT_FILE, 
        help=f"包含 VLESS 链接的输入文件名。\n(默认: {DEFAULT_INPUT_FILE})"
    )
    parser.add_argument(
        "-o", "--output", 
        default=DEFAULT_OUTPUT_FILE, 
        help=f"生成的 Clash.Meta 配置文件的输出路径。\n(默认: {DEFAULT_OUTPUT_FILE})"
    )
    args = parser.parse_args()

    vless_txt_to_clash(txt_file=args.input, output_file=args.output)

if __name__ == "__main__":
    main()
