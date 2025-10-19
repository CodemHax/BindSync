# BindSync

A real-time message bridge service that synchronizes communications between Telegram and Discord platforms, with a modern web interface for seamless cross-platform messaging.

## Features

- 🔄 **Bidirectional Message Sync**: Messages sent on Telegram appear on Discord and vice versa
- 💬 **Reply Support**: Reply chains are preserved across both platforms
- 🌐 **Web Interface**: Modern, WhatsApp-inspired UI for sending and viewing messages
- 💾 **Message Persistence**: All messages stored in MongoDB for history and retrieval
- 🔌 **REST API**: Full-featured API for programmatic message management
- 🐳 **Docker Support**: Easy deployment with Docker containerization
- 📱 **Real-time Updates**: Auto-refreshing message feed in the web interface

## Prerequisites

- Python 3.11 or higher
- MongoDB instance (local or cloud)
- Telegram Bot Token ([create one via @BotFather](https://t.me/botfather))
- Discord Bot Token ([create one via Discord Developer Portal](https://discord.com/developers/applications))
- Telegram Chat ID (for the target chat/group)
- Discord Channel ID (for the target channel)

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/CodemHax/BindSync.git
cd BindSync
```

2. Create a `.env` file with your configuration (see Configuration section below)

3. Build and run with Docker:
```bash
docker build -t bindsync .
docker run -d -p 8000:8000 --env-file .env bindsync
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/CodemHax/BindSync.git
cd BindSync
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration (see Configuration section below)

5. Run the application:
```bash
python main.py
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB=bindsync

# API Configuration (Optional)
API_HOST=0.0.0.0
API_PORT=8000
```

### Getting Configuration Values

#### Telegram Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token provided

#### Telegram Chat ID
1. Add your bot to the target group/chat
2. Send a message in the chat
3. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for the `"chat":{"id":` field in the response

#### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token
5. Enable "Message Content Intent" in the bot settings

#### Discord Channel ID
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on the target channel and select "Copy ID"

## Usage

### Web Interface

Once the application is running, open your browser and navigate to:
```
http://localhost:8000
```

The web interface allows you to:
- View all messages from both Telegram and Discord
- Send new messages to both platforms
- Reply to existing messages (replies are preserved across platforms)
- Filter messages by platform
- Monitor connection status

### API Endpoints

#### Get Messages
```bash
GET /messages?limit=100&offset=0
```
Retrieves messages from the database.

**Query Parameters:**
- `limit` (optional, default: 100, max: 200): Number of messages to retrieve
- `offset` (optional, default: 0): Number of messages to skip

**Response:**
```json
{
  "messages": [
    {
      "id": "message_uuid",
      "source": "telegram",
      "username": "John Doe",
      "text": "Hello from Telegram!",
      "timestamp": "2024-10-19T12:00:00",
      "tg_msg_id": 123,
      "dc_msg_id": 456,
      "reply_to_id": null
    }
  ]
}
```

#### Get Specific Message
```bash
GET /messages/{message_id}
```
Retrieves a specific message by its ID.

#### Send Message
```bash
POST /messages
Content-Type: application/json

{
  "username": "WebUser",
  "text": "Hello from the web!",
  "reply_to_id": "optional_message_id"
}
```
Sends a message to both Telegram and Discord.

**Response:**
```json
{
  "id": "message_uuid",
  "tg_msg_id": 123,
  "dc_msg_id": 456
}
```

#### Reply to Message
```bash
POST /messages/{message_id}/reply
Content-Type: application/json

{
  "username": "WebUser",
  "text": "This is a reply!"
}
```
Sends a reply to a specific message on both platforms.

#### Health Check
```bash
GET /health
```
Returns the health status of the service and runtime information.

### Testing

The project includes a comprehensive test suite. Run tests with:

```bash
# Comprehensive test (tests all endpoints)
python test_api.py

# Quick runtime test (checks bot initialization)
python test_api.py quick

# Message sending test
python test_api.py message
```

**Note:** The API must be running for tests to work.

## Project Structure

```
BindSync/
├── frontend/
│   └── index.html          # Web interface
├── src/
│   ├── api/
│   │   └── server.py       # FastAPI server and endpoints
│   ├── bot/
│   │   ├── tg_bot.py      # Telegram bot implementation
│   │   └── dc_bot.py      # Discord bot implementation
│   ├── core/
│   │   ├── forward.py     # Main application logic
│   │   └── models.py      # Pydantic models
│   ├── database/
│   │   ├── database.py    # MongoDB connection
│   │   └── store_functions.py  # Database operations
│   ├── utils/
│   │   └── bridge.py      # Message forwarding utilities
│   └── config.py          # Configuration loader
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
└── test_api.py          # API test suite
```

## How It Works

1. **Message Flow**:
   - When a message is sent on Telegram, the Telegram bot receives it
   - The message is stored in MongoDB and forwarded to Discord
   - The web interface can also send messages, which are forwarded to both platforms
   - Reply chains are tracked and preserved across all platforms

2. **Message Storage**:
   - Each message is assigned a unique ID and stored in MongoDB
   - Platform-specific message IDs (Telegram and Discord) are tracked
   - Reply relationships are maintained for threading

3. **Web Interface**:
   - Built with vanilla JavaScript and modern CSS
   - Auto-refreshes every 3 seconds to show new messages
   - Supports replying to messages with preserved threading
   - Clean, responsive design inspired by modern messaging apps

## Troubleshooting

### Bot not receiving messages
- Ensure the bot has been added to the Telegram group/Discord channel
- Verify that the TELEGRAM_CHAT_ID and DISCORD_CHANNEL_ID are correct
- For Discord, ensure "Message Content Intent" is enabled in the bot settings

### Database connection errors
- Verify MongoDB is running and accessible
- Check the MONGO_URI in your `.env` file
- Ensure the MongoDB user has proper permissions

### Messages not syncing
- Check the application logs (`bridge.log`) for errors
- Verify both bots are online and have proper permissions
- Test the `/health` endpoint to check bot initialization status

### Web interface not loading
- Ensure the application is running on the correct port
- Check if there are any firewall rules blocking the port
- Verify the API_HOST and API_PORT settings in `.env`

## Dependencies

- `python-telegram-bot>=20` - Telegram bot framework
- `discord.py>=2.3` - Discord bot framework
- `fastapi>=0.111` - Web framework for API
- `uvicorn[standard]>=0.30` - ASGI server
- `motor>=3.4.0` - Async MongoDB driver
- `pymongo>=4.6.0` - MongoDB driver
- `python-dotenv>=1.0` - Environment variable management
- `pydantic~=2.11.9` - Data validation
- `requests` - HTTP library

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the [GitHub repository](https://github.com/CodemHax/BindSync).
