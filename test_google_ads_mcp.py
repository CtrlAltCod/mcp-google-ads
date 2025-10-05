import asyncio
import json
import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import your MCP server module
import google_ads_server

def test_format_customer_id():
    """Test the format_customer_id function with various input formats."""
    test_cases = [
        # Regular ID
        ("9873186703", "9873186703"),
        # ID with dashes
        ("987-318-6703", "9873186703"),
        # ID with quotes
        ('"9873186703"', "9873186703"),
        # ID with escaped quotes
        ('\"9873186703\"', "9873186703"),
        # ID with leading zeros
        ("0009873186703", "9873186703"),
        # Short ID that needs padding
        ("12345", "0000012345"),
        # ID with other non-digit characters
        ("{9873186703}", "9873186703"),
    ]
    
    print("\n=== Testing format_customer_id with various formats ===")
    for input_id, expected in test_cases:
        result = google_ads_server.format_customer_id(input_id)
        print(f"Input: {input_id}")
        print(f"Result: {result}")
        print(f"Expected: {expected}")
        print(f"Test {'PASSED' if result == expected else 'FAILED'}")
        print("-" * 50)

async def test_mcp_tools():
    """Test Google Ads MCP tools directly."""
    # Get a list of available customer IDs first
    print("=== Testing list_accounts ===")
    accounts_result = await google_ads_server.list_accounts_by_api()
    print(accounts_result)

    # hardcode managercustomer ID
    manager_customer_id = "2857151978"
    
    # Parse the accounts to extract a customer ID for further tests
    non_manager_customer_ids = []
    for line in accounts_result.split('\n'):
        if line.startswith("Account ID:"):
            non_manager_customer_id = line.replace("Account ID:", "").strip()
            if non_manager_customer_id != manager_customer_id:
                non_manager_customer_ids.append(non_manager_customer_id)

    
    print(f"\nUsing manager customer ID: {manager_customer_id} for testing\n")
    print(f"\nUsing non-manager customer IDs: {non_manager_customer_ids} for testing\n")

    # Test list accounts by gaql
    print("\n=== Testing list_customer_accounts_by_gaql ===")
    accounts_result = await google_ads_server.list_customer_accounts_by_gaql(manager_customer_id)
    print(accounts_result)

    # Test list campaigns for a customer account
    print("\n=== Testing list_customer_campaigns_by_gaql ===")
    customer_account_id = "9711179739"
    campaigns_result = await google_ads_server.list_customer_campaigns_by_gaql(customer_account_id)
    print(campaigns_result)
    
    # # # Test list campaigns
    # # print("\n=== Testing list_campaigns ===")
    # # campaigns_result = await google_ads_server.list_campaigns_by_qaql(manager_customer_id)
    # # # campaigns_result = await google_ads_server.list_campaigns_by_qaql("9711179739")
    # # print(campaigns_result)

    # # Test campaign performance
    # print("\n=== Testing get_campaign_performance ===")
    # campaign_result = await google_ads_server.get_campaign_performance(manager_customer_id, days=7)
    # print(campaign_result)
    
    # # Test ad performance
    # print("\n=== Testing get_ad_performance ===")
    # ad_result = await google_ads_server.get_ad_performance(manager_customer_id, days=7)
    # print(ad_result)
    
    # # Test ad creatives
    # print("\n=== Testing get_ad_creatives ===")
    # creatives_result = await google_ads_server.get_ad_creatives(manager_customer_id)
    # print(creatives_result)
    
    # # Test custom GAQL query
    # print("\n=== Testing run_gaql ===")
    # query = """
    #     SELECT 
    #         campaign.id, 
    #         campaign.name, 
    #         campaign.status 
    #     FROM campaign 
    #     LIMIT 5
    # """
    # gaql_result = await google_ads_server.run_gaql(manager_customer_id, query, format="json")
    # print(gaql_result)


async def test_asset_methods():
    """Test Asset-related MCP tools directly."""
    # Get a list of available customer IDs first
    print("=== Testing Asset Methods ===")
    accounts_result = await google_ads_server.list_accounts_by_api()

    # hardcode managercustomer ID
    manager_customer_id = "2857151978"
    
    # Parse the accounts to extract a customer ID for further tests
    non_manager_customer_ids = []
    for line in accounts_result.split('\n'):
        if line.startswith("Account ID:"):
            non_manager_customer_id = line.replace("Account ID:", "").strip()
            if non_manager_customer_id != manager_customer_id:
                non_manager_customer_ids.append(non_manager_customer_id)
    
    print(f"\nUsing manager customer ID: {manager_customer_id} for testing asset methods\n")
    print(f"Using non-manager customer IDs: {non_manager_customer_ids} for testing asset methods\n")
    
    # Test get_image_assets
    print("\n=== Testing get_image_assets ===")
    image_assets_result = await google_ads_server.get_image_assets(manager_customer_id, limit=10)
    print(image_assets_result)
    
    # Extract an asset ID for further testing if available
    asset_id = None
    for line in image_assets_result.split('\n'):
        if line.startswith("1. Asset ID:"):
            asset_id = line.replace("1. Asset ID:", "").strip()
            break
    
    # Use a smaller number of days for testing to avoid the INVALID_VALUE_WITH_DURING_OPERATOR error
    days_to_test = 30  # Use 30 instead of 90
    
    # Test get_asset_usage if we found an asset ID
    if asset_id:
        print(f"\n=== Testing get_asset_usage with asset ID: {asset_id} ===")
        try:
            asset_usage_result = await google_ads_server.get_asset_usage(manager_customer_id, asset_id=asset_id, asset_type="IMAGE")
            print(asset_usage_result)
        except Exception as e:
            print(f"Error in get_asset_usage: {str(e)}")
    else:
        print("\nNo asset ID found to test get_asset_usage")
    
    # Test analyze_image_assets with a valid date range
    print(f"\n=== Testing analyze_image_assets with {days_to_test} days ===")
    try:
        analyze_result = await google_ads_server.analyze_image_assets(manager_customer_id, days=days_to_test)
        print(analyze_result)
    except Exception as e:
        print(f"Error in analyze_image_assets: {str(e)}")

if __name__ == "__main__":
    # Run format_customer_id tests first
    # test_format_customer_id()
    
    # Setup environment variables if they're not already set
    if not os.environ.get("GOOGLE_ADS_CREDENTIALS_PATH"):
        # Set environment variables for testing (comment out if already set in your environment)
        os.environ["GOOGLE_ADS_CREDENTIALS_PATH"] = "google_ads_token.json"
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "YOUR_DEVELOPER_TOKEN"  # Replace with placeholder
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "YOUR_CLIENT_ID"  # Replace with placeholder
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "YOUR_CLIENT_SECRET"  # Replace with placeholder
    
    # Run the MCP tools test (uncomment to run full tests)
    asyncio.run(test_mcp_tools())
    
    # Run the asset methods test (uncomment to run full tests)
    # asyncio.run(test_asset_methods())
