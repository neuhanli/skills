#!/usr/bin/env python3
"""
TencentCloud HotSearch - Online search tool using Tencent Cloud API
Supports web-wide search and site-specific search (e.g., qq.com, news.qq.com)
API Version: 2025-05-08
API Endpoint: wsa.tencentcloudapi.com
"""

import json
import os
import sys
import hashlib
import hmac
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import urllib.request
import urllib.parse


class TencentCloudHotSearch:
    """Main class for searching news and articles using Tencent Cloud API."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize TencentCloudHotSearch with configuration."""
        self.config = self._load_config(config_path)
        self.results = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                "Please create a config.json file with your Tencent Cloud API credentials."
            )
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _sign_request(self, params: Dict, secret_id: str, secret_key: str) -> Dict:
        """Sign the request using Tencent Cloud signature method."""
        from datetime import datetime
        
        # Get current timestamp
        timestamp = int(time.time())
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
        
        # Build canonical request
        service = "wsa"
        host = f"{service}.tencentcloudapi.com"
        action = "SearchPro"
        version = "2025-05-08"
        region = ""
        
        # Build request payload
        payload = json.dumps(params)
        payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        
        # Build canonical headers
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        canonical_headers = f"content-type:application/json\nhost:{host}\n"
        signed_headers = "content-type;host"
        
        canonical_request = (http_request_method + "\n" +
                            canonical_uri + "\n" +
                            canonical_querystring + "\n" +
                            canonical_headers + "\n" +
                            signed_headers + "\n" +
                            payload_hash)
        
        # Build string to sign
        algorithm = "TC3-HMAC-SHA256"
        credential_scope = date + "/" + service + "/" + "tc3_request"
        string_to_sign = (algorithm + "\n" +
                         str(timestamp) + "\n" +
                         credential_scope + "\n" +
                         hashlib.sha256(canonical_request.encode('utf-8')).hexdigest())
        
        # Calculate signature
        secret_date = hmac.new(("TC3" + secret_key).encode('utf-8'), date.encode('utf-8'), hashlib.sha256).digest()
        secret_service = hmac.new(secret_date, service.encode('utf-8'), hashlib.sha256).digest()
        secret_signing = hmac.new(secret_service, "tc3_request".encode('utf-8'), hashlib.sha256).digest()
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Build authorization header
        authorization = (algorithm + " " +
                        "Credential=" + secret_id + "/" + credential_scope + ", " +
                        "SignedHeaders=" + signed_headers + ", " +
                        "Signature=" + signature)
        
        return {
            "host": host,
            "timestamp": timestamp,
            "authorization": authorization,
            "payload": payload
        }
    
    def search(self, keywords: List[str], site: Optional[str] = None, 
               mode: int = 0, limit: int = 10,
               from_time: Optional[int] = None, to_time: Optional[int] = None,
               industry: Optional[str] = None) -> List[Dict]:
        """
        Search for articles/news based on keywords using Tencent Cloud API.
        
        Args:
            keywords: List of 1-5 search keywords
            site: Optional site filter (e.g., 'qq.com', 'news.qq.com')
            mode: Result type (0-natural search, 1-multimodal VR, 2-mixed)
            limit: Number of results to return (default: 10, max: 50)
            from_time: Start time filter (Unix timestamp in seconds)
            to_time: End time filter (Unix timestamp in seconds)
            industry: Industry filter (gov/news/acad/finance)
            
        Returns:
            List of search results with title, summary, source, date, url, score, etc.
        """
        if not keywords or len(keywords) < 1 or len(keywords) > 5:
            raise ValueError("Keywords must be a list of 1-5 items")
        
        if limit < 1 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")
        
        if mode not in [0, 1, 2]:
            raise ValueError("Mode must be 0 (natural), 1 (multimodal VR), or 2 (mixed)")
        
        # Set default time range: from yesterday to current time
        if mode != 1:  # Time parameters are only valid for mode != 1
            if from_time is None:
                # Calculate yesterday's timestamp (24 hours ago)
                from_time = int(time.time()) - 24 * 3600
            if to_time is None:
                # Current time
                to_time = int(time.time())
        
        query = ' '.join(keywords)
        results = self._search_tencent_cloud(query, site, mode, limit, from_time, to_time, industry)
        
        self.results = results
        return results
    
    def _search_tencent_cloud(self, query: str, site: Optional[str], mode: int,
                              limit: int, from_time: Optional[int], 
                              to_time: Optional[int], industry: Optional[str]) -> List[Dict]:
        """Search using Tencent Cloud Online Search API (SearchPro)."""
        
        secret_id = self.config.get('secret_id')
        secret_key = self.config.get('secret_key')
        
        if not secret_id or not secret_key:
            raise ValueError("Tencent Cloud API credentials (secret_id and secret_key) not found in config.json")
        
        try:
            # Build request parameters
            params = {
                "Query": query,
                "Mode": mode
            }
            
            # Add optional parameters
            if site and mode != 1:  # Site 参数在 mode=1 时无效
                params["Site"] = site
            
            # Use valid limit value
            if limit in [10, 20, 30, 40, 50]:
                params["Cnt"] = limit
            else:
                params["Cnt"] = 10  # Default to 10 if invalid limit
            
            if from_time and mode != 1:
                params["FromTime"] = from_time
            
            if to_time and mode != 1:
                params["ToTime"] = to_time
            
            if industry and industry in ['gov', 'news', 'acad', 'finance']:
                params["Industry"] = industry
            
            # Sign the request
            signed_request = self._sign_request(params, secret_id, secret_key)
            
            # Build HTTP request
            url = f"https://{signed_request['host']}"
            headers = {
                "Content-Type": "application/json",
                "Host": signed_request['host'],
                "X-TC-Action": "SearchPro",
                "X-TC-Version": "2025-05-08",
                "X-TC-Timestamp": str(signed_request['timestamp']),
                "Authorization": signed_request['authorization']
            }
            
            req = urllib.request.Request(
                url,
                data=signed_request['payload'].encode('utf-8'),
                headers=headers,
                method="POST"
            )
            
            # Send request
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = json.loads(response.read().decode('utf-8'))
            
            results = []
            
            # Parse response
            if 'Response' in response_data:
                response_body = response_data['Response']
                pages = response_body.get('Pages', [])
                
                for page_str in pages:
                    try:
                        page = json.loads(page_str)
                        results.append({
                            "title": page.get('title', ''),
                            "summary": page.get('passage', ''),
                            "dynamic_summary": page.get('content', ''),  # 尊享版字段
                            "source": page.get('site', ''),
                            "publishTime": page.get('date', ''),
                            "url": page.get('url', ''),
                            "score": page.get('score', 0),
                            "images": page.get('images', []),
                            "favicon": page.get('favicon', '')
                        })
                    except json.JSONDecodeError:
                        continue
            
            return results
            
        except Exception as e:
            print(f"Error searching Tencent Cloud: {e}")
            return []
    
    def save_results(self, output_path: str, format: str = "md"):
        """
        Save search results to a file.
        
        Args:
            output_path: Path to save the results
            format: Output format - 'json', 'csv', 'txt', or 'md' (default: md)
        """
        if not self.results:
            print("No results to save. Please run a search first.")
            return
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "results": self.results,
                    "total": len(self.results),
                    "timestamp": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            print(f"Results saved to: {output_file}")
            
        elif format == "csv":
            try:
                import pandas as pd
            except ImportError:
                raise ImportError(
                    "Please install pandas for CSV export: pip install pandas"
                )
            
            df = pd.DataFrame(self.results)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"Results saved to: {output_file}")
            
        elif format == "txt":
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Search Results\n")
                f.write(f"Total results: {len(self.results)}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, result in enumerate(self.results, 1):
                    f.write(f"[{i}] {result['title']}\n")
                    f.write(f"摘要: {result['summary']}\n")
                    if result.get('dynamic_summary'):
                        f.write(f"动态摘要: {result['dynamic_summary']}\n")
                    f.write(f"来源: {result['source']}\n")
                    f.write(f"时间: {result['publishTime']}\n")
                    f.write(f"链接: {result['url']}\n")
                    if result.get('score'):
                        f.write(f"相关度: {result['score']:.4f}\n")
                    f.write("-" * 80 + "\n\n")
            print(f"Results saved to: {output_file}")
            
        elif format == "md":
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Search Results\n\n")
                f.write(f"**Total results:** {len(self.results)}\n")
                f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                
                for i, result in enumerate(self.results, 1):
                    f.write(f"## {i}. {result['title']}\n\n")
                    f.write(f"**摘要:** {result['summary']}\n\n")
                    if result.get('dynamic_summary'):
                        f.write(f"**动态摘要:** {result['dynamic_summary']}\n\n")
                    f.write(f"**来源:** {result['source']}\n\n")
                    f.write(f"**时间:** {result['publishTime']}\n\n")
                    f.write(f"**链接:** [{result['url']}]({result['url']})\n\n")
                    if result.get('score'):
                        f.write(f"**相关度:** {result['score']:.4f}\n\n")
                    if result.get('images') and len(result['images']) > 0:
                        f.write(f"**图片:** {', '.join(result['images'])}\n\n")
                    f.write("---\n\n")
            print(f"Results saved to: {output_file}")
            
        else:
            raise ValueError("Format must be 'json', 'csv', 'txt', or 'md'")
    
    def print_results(self):
        """Print search results to console."""
        if not self.results:
            print("No results to display.")
            return
        
        print(f"\nFound {len(self.results)} results:\n")
        for i, result in enumerate(self.results, 1):
            print(f"[{i}] {result['title']}")
            print(f"    摘要: {result['summary'][:100]}...")
            if result.get('dynamic_summary'):
                print(f"    动态摘要: {result['dynamic_summary'][:100]}...")
            print(f"    来源: {result['source']}")
            print(f"    时间: {result['publishTime']}")
            print(f"    链接: {result['url']}")
            if result.get('score'):
                print(f"    相关度: {result['score']:.4f}")
            print()


def main():
    """Command-line interface for TencentCloudHotSearch."""
    parser = argparse.ArgumentParser(
        description="TencentCloud HotSearch - Online search tool using Tencent Cloud API"
    )
    parser.add_argument(
        "keywords",
        nargs="+",
        help="Search keywords (1-5 keywords)"
    )
    parser.add_argument(
        "-s", "--site",
        help="Specify search site (e.g., qq.com, news.qq.com). If not specified, searches the entire web."
    )
    parser.add_argument(
        "-m", "--mode",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="Search mode: 0-natural search (default), 1-multimodal VR, 2-mixed"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=10,
        help="Number of results (default: 10, max: 50, options: 10/20/30/40/50)"
    )
    parser.add_argument(
        "--from-time",
        type=int,
        help="Start time filter (Unix timestamp in seconds)"
    )
    parser.add_argument(
        "--to-time",
        type=int,
        help="End time filter (Unix timestamp in seconds)"
    )
    parser.add_argument(
        "--industry",
        choices=["gov", "news", "acad", "finance"],
        help="Industry filter: gov/news/acad/finance (premium only)"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to config file (default: config.json)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (e.g., results.json, results.md, results.txt)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv", "txt", "md"],
        default="md",
        help="Output format (default: md)"
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print results to console"
    )
    
    args = parser.parse_args()
    
    try:
        searcher = TencentCloudHotSearch(args.config)
        results = searcher.search(
            keywords=args.keywords,
            site=args.site,
            mode=args.mode,
            limit=args.limit,
            from_time=args.from_time,
            to_time=args.to_time,
            industry=args.industry
        )
        
        if args.print:
            searcher.print_results()
        
        if args.output:
            searcher.save_results(args.output, args.format)
        else:
            # 如果未指定输出路径，使用配置文件中的默认路径
            config = searcher.config
            default_output_dir = config.get('output_dir', './output')
            default_filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}"
            default_output_path = os.path.join(default_output_dir, default_filename)
            searcher.save_results(default_output_path, args.format)
        
        site_info = f" in {args.site}" if args.site else ""
        mode_info = f" (mode: {args.mode})"
        print(f"\n✅ Successfully retrieved {len(results)} results from Tencent Cloud{site_info}{mode_info}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
