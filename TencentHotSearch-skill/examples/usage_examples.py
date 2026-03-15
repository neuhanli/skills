#!/usr/bin/env python3
"""
Example usage of TencentCloud-HotSearch-skill in an agent environment
"""

import sys
import os

# Add the skill directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from tencent_hotsearch import TencentCloudHotSearch


def example_web_search():
    """Example 1: Search across the entire web"""
    
    # Initialize the searcher with config file
    searcher = TencentCloudHotSearch("config.json")
    
    print("=== Example 1: Web-wide Search ===")
    results = searcher.search(
        keywords=["人工智能", "AI技术"],
        site=None,  # None means web-wide search
        limit=5
    )
    print(f"Found {len(results)} results from web-wide search\n")
    
    return results


def example_site_search():
    """Example 2: Search within a specific site (Tencent News)"""
    
    searcher = TencentCloudHotSearch("config.json")
    
    print("=== Example 2: Site-specific Search (Tencent News) ===")
    results = searcher.search(
        keywords=["科技", "创新"],
        site="news.qq.com",
        limit=5
    )
    print(f"Found {len(results)} results from news.qq.com\n")
    
    return results


def example_multiple_sites():
    """Example 3: Search across multiple sites"""
    
    searcher = TencentCloudHotSearch("config.json")
    
    sites = ["qq.com", "news.qq.com", "tech.qq.com"]
    keywords = ["人工智能"]
    
    print("=== Example 3: Search across Multiple Sites ===")
    
    all_results = []
    for site in sites:
        results = searcher.search(
            keywords=keywords,
            site=site,
            limit=3
        )
        print(f"Found {len(results)} results from {site}")
        all_results.extend(results)
    
    print(f"\nTotal results from all sites: {len(all_results)}\n")
    
    return all_results


def example_save_results():
    """Example 4: Save results to file"""
    
    searcher = TencentCloudHotSearch("config.json")
    
    print("=== Example 4: Save Results to File ===")
    
    # Search and save as JSON
    results = searcher.search(
        keywords=["人工智能"],
        site=None,
        limit=10
    )
    searcher.save_results("output/web_search_results.json", format="json")
    print("Results saved to output/web_search_results.json")
    
    # Search and save as CSV
    results = searcher.search(
        keywords=["科技"],
        site="qq.com",
        limit=10
    )
    searcher.save_results("output/site_search_results.csv", format="csv")
    print("Results saved to output/site_search_results.csv\n")
    
    return results


def example_print_results():
    """Example 5: Print results to console"""
    
    searcher = TencentCloudHotSearch("config.json")
    
    print("=== Example 5: Print Results to Console ===")
    
    results = searcher.search(
        keywords=["机器学习"],
        site=None,
        limit=3
    )
    
    searcher.print_results()
    
    return results


def example_agent_integration():
    """
    Example 6: How to integrate TencentCloud-HotSearch in an agent environment
    
    This demonstrates how an agent can use the TencentCloud-HotSearch skill
    to fetch information and use it in its responses.
    """
    
    print("=== Example 6: Agent Integration ===\n")
    
    # Initialize searcher
    searcher = TencentCloudHotSearch("config.json")
    
    # User query
    user_query = "我想了解最新的 AI 技术动态"
    
    # Extract keywords from user query (simplified)
    keywords = ["AI技术", "人工智能"]
    
    # Search for relevant information
    results = searcher.search(
        keywords=keywords,
        site=None,
        limit=5
    )
    
    # Use the results in agent response
    if results:
        response = f"根据腾讯云联网搜索，为您找到了 {len(results)} 条关于 {', '.join(keywords)} 的最新动态：\n\n"
        
        for i, result in enumerate(results[:3], 1):
            response += f"{i}. {result['title']}\n"
            response += f"   {result['summary'][:100]}...\n"
            response += f"   来源: {result['source']}\n"
            response += f"   链接: {result['url']}\n\n"
        
        print(response)
    else:
        print("抱歉，没有找到相关信息。")
    
    return results


def example_news_monitoring():
    """Example 7: Monitor news from specific sources"""
    
    searcher = TencentCloudHotSearch("config.json")
    
    print("=== Example 7: News Monitoring ===\n")
    
    # Monitor tech news from multiple sources
    topics = [
        {"keywords": ["科技", "创新"], "site": "tech.qq.com"},
        {"keywords": ["财经", "股市"], "site": "finance.qq.com"},
        {"keywords": ["体育", "足球"], "site": "sports.qq.com"}
    ]
    
    for topic in topics:
        print(f"Monitoring: {topic['keywords']} from {topic['site']}")
        results = searcher.search(
            keywords=topic['keywords'],
            site=topic['site'],
            limit=3
        )
        print(f"  Found {len(results)} articles\n")
    
    print("News monitoring completed.\n")


def example_topic_research():
    """Example 8: Deep research on a specific topic"""
    
    searcher = TencentCloudHotSearch("config.json")
    
    print("=== Example 8: Topic Research ===\n")
    
    topic = "区块链技术"
    keywords = ["区块链", "Blockchain", "Web3", "加密货币"]
    
    print(f"Researching topic: {topic}\n")
    
    # Web-wide search
    print("1. Web-wide search:")
    web_results = searcher.search(
        keywords=keywords[:2],
        site=None,
        limit=5
    )
    print(f"   Found {len(web_results)} results\n")
    
    # Site-specific search (Tencent News)
    print("2. Site-specific search (Tencent News):")
    site_results = searcher.search(
        keywords=keywords[:2],
        site="news.qq.com",
        limit=5
    )
    print(f"   Found {len(site_results)} results\n")
    
    # Save all results
    all_results = web_results + site_results
    searcher.save_results("output/blockchain_research.json", format="json")
    print(f"3. Saved {len(all_results)} total results to output/blockchain_research.json\n")
    
    return all_results


if __name__ == "__main__":
    print("TencentCloud-HotSearch-skill Usage Examples\n")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Run examples
    try:
        example_web_search()
        example_site_search()
        example_multiple_sites()
        example_save_results()
        example_print_results()
        print("\n" + "=" * 60)
        print("\nAgent Integration Examples:\n")
        example_agent_integration()
        print("\n" + "=" * 60)
        print("\nAdvanced Examples:\n")
        example_news_monitoring()
        example_topic_research()
        
        print("\n" + "=" * 60)
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("\nPlease make sure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Configured Tencent Cloud API keys in config.json")
        print("3. Valid API credentials")
        print("4. Internet connection")
        import traceback
        traceback.print_exc()
