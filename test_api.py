#!/usr/bin/env python
import requests
import json

BASE_URL = "http://localhost:8000"
print(f"Testing API at {BASE_URL}")

# Test 1: Get all messages
print("\n1. GET /messages - Getting all messages")
response = requests.get(f"{BASE_URL}/messages")
if response.status_code == 200:
    data = response.json()
    messages = data.get("messages", [])
    print(f"✓ Success! Found {len(messages)} messages")

    # Get first message ID for later tests
    first_message_id = messages[0]["id"] if messages else None
    if first_message_id:
        print(f"  First message ID: {first_message_id}")
else:
    print(f"✗ Failed. Status: {response.status_code}")
    first_message_id = None

# Test 2: Create a new message
print("\n2. POST /messages - Creating a new message")
payload = {
    "text": "Test message from simple script",
    "username": "Tester"
}
response = requests.post(f"{BASE_URL}/messages", json=payload)
if response.status_code == 200:
    result = response.json()
    new_message_id = result.get("id")
    print(f"✓ Success! Created message with ID: {new_message_id}")
else:
    print(f"✗ Failed. Status: {response.status_code}")
    print(f"  Response: {response.text}")
    new_message_id = None

# Test 3: Reply to a message (using reply_to_id parameter)
if new_message_id:
    print("\n3. POST /messages - Replying to a message with reply_to_id")
    payload = {
        "text": "This is a reply",
        "username": "Tester",
        "reply_to_id": new_message_id
    }
    response = requests.post(f"{BASE_URL}/messages", json=payload)
    if response.status_code == 200:
        result = response.json()
        reply_id = result.get("id")
        print(f"✓ Success! Created reply with ID: {reply_id}")
    else:
        print(f"✗ Failed. Status: {response.status_code}")
        print(f"  Response: {response.text}")

# Test 4: Reply using dedicated endpoint
if new_message_id:
    print("\n4. POST /messages/{id}/reply - Using dedicated reply endpoint")
    payload = {
        "text": "This is a reply using dedicated endpoint",
        "username": "Tester"
    }
    response = requests.post(f"{BASE_URL}/messages/{new_message_id}/reply", json=payload)
    if response.status_code == 200:
        result = response.json()
        reply_id = result.get("id")
        print(f"✓ Success! Created reply with ID: {reply_id}")
    else:
        print(f"✗ Failed. Status: {response.status_code}")
        print(f"  Response: {response.text}")

print("\nAll tests completed!")
