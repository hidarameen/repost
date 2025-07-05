#!/usr/bin/env python3
"""
Configuration Test Script
=========================

This script helps validate your bot configuration before running the main bot.
"""

import sys
import asyncio
from config import Config
from database import Database
from telegraph_manager import TelegraphManager
from telegram import Bot
import requests

async def test_configuration():
    """Test all configuration components"""
    print("🔍 Testing bot configuration...\n")
    
    # Test 1: Basic Configuration
    print("1. Testing basic configuration...")
    if not Config.validate():
        print("❌ Configuration validation failed!")
        return False
    print("✅ Basic configuration is valid\n")
    
    # Test 2: Database
    print("2. Testing database connection...")
    try:
        db = Database()
        db.init_database()
        print("✅ Database connection successful\n")
    except Exception as e:
        print(f"❌ Database error: {e}\n")
        return False
    
    # Test 3: Telegram Bot
    print("3. Testing Telegram bot...")
    try:
        bot = Bot(token=Config.BOT_TOKEN)
        bot_info = await bot.get_me()
        print(f"✅ Telegram bot connected: @{bot_info.username}\n")
    except Exception as e:
        print(f"❌ Telegram bot error: {e}\n")
        return False
    
    # Test 4: Telegraph
    print("4. Testing Telegraph connection...")
    try:
        telegraph_manager = TelegraphManager()
        if telegraph_manager.account_info:
            print("✅ Telegraph connection successful\n")
        else:
            print("⚠️ Telegraph connection failed, but this is optional\n")
    except Exception as e:
        print(f"⚠️ Telegraph error: {e} (This is optional)\n")
    
    # Test 5: Website Access
    print("5. Testing website access...")
    try:
        response = requests.get(Config.WEBSITE_URL, timeout=10)
        if response.status_code == 200:
            print(f"✅ Website is accessible: {Config.WEBSITE_URL}\n")
        else:
            print(f"⚠️ Website returned status code: {response.status_code}\n")
    except Exception as e:
        print(f"❌ Website access error: {e}\n")
        return False
    
    # Test 6: Channel Access
    print("6. Testing channel access...")
    try:
        bot = Bot(token=Config.BOT_TOKEN)
        channel_info = await bot.get_chat(Config.CHANNEL_ID)
        print(f"✅ Channel access successful: {channel_info.title}\n")
    except Exception as e:
        print(f"❌ Channel access error: {e}\n")
        print("Make sure the bot is added to the channel as an admin!\n")
        return False
    
    # Test 7: Admin Access
    print("7. Testing admin access...")
    if Config.ADMIN_IDS:
        print(f"✅ Admin IDs configured: {len(Config.ADMIN_IDS)} admins\n")
    else:
        print("⚠️ No admin IDs configured\n")
    
    # Show configuration summary
    print("📊 Configuration Summary:")
    print(f"  • Website URL: {Config.WEBSITE_URL}")
    print(f"  • Channel ID: {Config.CHANNEL_ID}")
    print(f"  • Check Interval: {Config.CHECK_INTERVAL} seconds")
    print(f"  • Auto Publish: {Config.AUTO_PUBLISH}")
    print(f"  • Text Shortening: {Config.ENABLE_TEXT_SHORTENING}")
    print(f"  • Website Sections: {len(Config.WEBSITE_SECTIONS)}")
    print(f"  • Admin IDs: {len(Config.ADMIN_IDS)}")
    
    print("\n🎉 Configuration test completed successfully!")
    return True

def main():
    """Main function"""
    print("🤖 News Bot Configuration Test\n")
    
    try:
        success = asyncio.run(test_configuration())
        if success:
            print("\n✅ All tests passed! You can now run the bot.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please fix the configuration.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Test cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()