
import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional

class BindSyncTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_health_check(self) -> Dict[str, Any]:

        print("🔍 Testing health check endpoint...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Health check successful!")
                    print(f"   Runtime state: {json.dumps(data['runtime'], indent=2)}")
                    return data
                else:
                    print(f"❌ Health check failed with status: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return {"error": f"HTTP {response.status}", "response": text}
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return {"error": str(e)}

    async def test_get_messages(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:

        print(f"📖 Testing get messages (limit={limit}, offset={offset})...")
        try:
            async with self.session.get(f"{self.base_url}/messages?limit={limit}&offset={offset}") as response:
                if response.status == 200:
                    data = await response.json()
                    message_count = len(data.get('messages', []))
                    print(f"✅ Retrieved {message_count} messages successfully!")
                    return data
                else:
                    print(f"❌ Get messages failed with status: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return {"error": f"HTTP {response.status}", "response": text}
        except Exception as e:
            print(f"❌ Get messages error: {e}")
            return {"error": str(e)}

    async def test_send_message(self, username: str = "TestUser", text: str = "Hello from test script!", reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """Test sending a message through the API"""
        print(f"📤 Testing send message (user: {username}, text: '{text[:30]}...')...")

        payload = {
            "username": username,
            "text": text
        }

        # Only include reply_to_id if it's not None
        if reply_to_id is not None:
            payload["reply_to_id"] = reply_to_id

        try:
            async with self.session.post(f"{self.base_url}/messages", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Message sent successfully!")
                    print(f"   Message ID: {data.get('id')}")
                    print(f"   Telegram ID: {data.get('tg_msg_id')}")
                    print(f"   Discord ID: {data.get('dc_msg_id')}")
                    return data
                else:
                    print(f"❌ Send message failed with status: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return {"error": f"HTTP {response.status}", "response": text}
        except Exception as e:
            print(f"❌ Send message error: {e}")
            return {"error": str(e)}

    async def test_reply_to_message(self, message_id: str, username: str = "TestUser", text: str = "This is a test reply!") -> Dict[str, Any]:
        """Test replying to a message"""
        print(f"💬 Testing reply to message {message_id}...")

        payload = {
            "username": username,
            "text": text
        }

        try:
            async with self.session.post(f"{self.base_url}/messages/{message_id}/reply", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Reply sent successfully!")
                    print(f"   Reply ID: {data.get('id')}")
                    print(f"   Telegram ID: {data.get('tg_msg_id')}")
                    print(f"   Discord ID: {data.get('dc_msg_id')}")
                    return data
                else:
                    print(f"❌ Reply failed with status: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return {"error": f"HTTP {response.status}", "response": text}
        except Exception as e:
            print(f"❌ Reply error: {e}")
            return {"error": str(e)}

    async def test_get_specific_message(self, message_id: str) -> Dict[str, Any]:
        """Test getting a specific message by ID"""
        print(f"🔍 Testing get specific message {message_id}...")
        try:
            async with self.session.get(f"{self.base_url}/messages/{message_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Retrieved message successfully!")
                    print(f"   Text: {data.get('text', '')[:50]}...")
                    return data
                elif response.status == 404:
                    print(f"⚠️  Message not found (404)")
                    return {"error": "Message not found"}
                else:
                    print(f"❌ Get message failed with status: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return {"error": f"HTTP {response.status}", "response": text}
        except Exception as e:
            print(f"❌ Get message error: {e}")
            return {"error": str(e)}

    async def test_frontend(self) -> Dict[str, Any]:
        """Test the frontend endpoint"""
        print("🌐 Testing frontend endpoint...")
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'html' in content_type:
                        print("✅ Frontend HTML served successfully!")
                        return {"status": "success", "content_type": content_type}
                    else:
                        data = await response.json()
                        print(f"✅ Frontend response: {data}")
                        return data
                else:
                    print(f"❌ Frontend failed with status: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return {"error": f"HTTP {response.status}", "response": text}
        except Exception as e:
            print(f"❌ Frontend error: {e}")
            return {"error": str(e)}

async def run_comprehensive_test():
    """Run all tests in sequence"""
    print("🚀 Starting BindSync API Comprehensive Test")
    print("=" * 50)

    async with BindSyncTester() as tester:
        # Test 1: Health check (most important for debugging)
        health_result = await tester.test_health_check()
        print()

        # Analyze health check results
        if "runtime" in health_result:
            runtime = health_result["runtime"]
            all_initialized = all([
                runtime.get("tbot_initialized", False),
                runtime.get("dbot_initialized", False),
                runtime.get("config_loaded", False),
                runtime.get("maps_initialized", False)
            ])

            if all_initialized:
                print("🎉 All runtime components are properly initialized!")
            else:
                print("⚠️  Some runtime components are not initialized:")
                for key, value in runtime.items():
                    if key.endswith("_initialized") and not value:
                        print(f"   ❌ {key}: {value}")
            print()

        # Test 2: Frontend
        await tester.test_frontend()
        print()

        # Test 3: Get existing messages
        messages_result = await tester.test_get_messages()
        print()

        # Test 4: Send a test message
        send_result = await tester.test_send_message(
            username="TestScript",
            text=f"Test message sent at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print()

        # Test 5: If message was sent successfully, test getting it and replying
        if "id" in send_result:
            message_id = send_result["id"]

            # Get the specific message
            await tester.test_get_specific_message(message_id)
            print()

            # Reply to the message
            await tester.test_reply_to_message(
                message_id,
                username="TestReply",
                text=f"Reply to test message at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print()

        # Test 6: Get messages again to see new ones
        print("📖 Getting updated message list...")
        await tester.test_get_messages(limit=5)

    print("=" * 50)
    print("✨ Comprehensive test completed!")

async def run_quick_test():
    """Run a quick test focusing on runtime initialization"""
    print("⚡ Quick Runtime Test")
    print("=" * 30)

    async with BindSyncTester() as tester:
        health_result = await tester.test_health_check()

        if "runtime" in health_result:
            runtime = health_result["runtime"]
            print("\n📊 Runtime Status Summary:")
            print(f"   Telegram Bot: {'✅' if runtime.get('tbot_initialized') else '❌'}")
            print(f"   Discord Bot: {'✅' if runtime.get('dbot_initialized') else '❌'}")
            print(f"   Config Loaded: {'✅' if runtime.get('config_loaded') else '❌'}")
            print(f"   Maps Initialized: {'✅' if runtime.get('maps_initialized') else '❌'}")
            print(f"   Telegram Chat ID: {runtime.get('telegram_chat_id', 'Not set')}")
            print(f"   Discord Channel ID: {runtime.get('discord_channel_id', 'Not set')}")

async def run_message_test():
    """Test only message sending functionality"""
    print("📤 Message Sending Test")
    print("=" * 25)

    async with BindSyncTester() as tester:
        # Quick health check
        await tester.test_health_check()
        print()

        # Send test message
        result = await tester.test_send_message(
            username="QuickTest",
            text="Quick message test - checking bot connectivity"
        )

        # Analyze the result
        if "error" not in result:
            tg_sent = result.get("tg_msg_id") is not None
            dc_sent = result.get("dc_msg_id") is not None

            print(f"\n📊 Message Delivery Summary:")
            print(f"   Telegram: {'✅ Sent' if tg_sent else '❌ Failed'}")
            print(f"   Discord: {'✅ Sent' if dc_sent else '❌ Failed'}")

            if not tg_sent and not dc_sent:
                print("\n⚠️  No messages were sent to either platform!")
                print("   Check the server console output for detailed error messages.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "quick":
            asyncio.run(run_quick_test())
        elif test_type == "message":
            asyncio.run(run_message_test())
        else:
            print("Available test types: quick, message, or no argument for comprehensive")
            asyncio.run(run_comprehensive_test())
    else:
        asyncio.run(run_comprehensive_test())
