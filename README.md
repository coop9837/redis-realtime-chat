# Redis Real-Time Chat Application

A production-ready chatbot demonstrating Redis Pub/Sub messaging, Docker containerization, and real-time data processing.

## Overview

This project implements a multi-channel chat system using Redis as a message broker, showcasing proficiency in:
- **Redis Pub/Sub patterns** for real-time messaging
- **Docker containerization** with multi-service orchestration
- **Concurrent programming** with Python threading
- **External API integration** for dynamic content

## Architecture

### Technology Stack
- **Backend:** Python 3.9
- **Database:** Redis (in-memory data store)
- **Infrastructure:** Docker & Docker Compose
- **APIs:** OpenWeather API for live weather data
- **Libraries:** redis-py, requests, threading

### System Design
- **Redis Pub/Sub:** Channel-based message distribution to multiple subscribers
- **Multi-threading:** Concurrent channel listening while maintaining interactive CLI
- **Data Persistence:** User profiles stored in Redis hashes, message history in Redis lists
- **Docker Networking:** Isolated containers with bridge network communication

## Features

### Core Messaging
- **Multi-channel support** with concurrent subscriptions
- **Message persistence** with full channel history
- **Real-time delivery** using Redis Pub/Sub
- **User identification** with profile storage

### Interactive Commands
```
!join <channel>    - Subscribe to a channel and view message history
!send             - Publish messages to any channel
!leave <channel>  - Unsubscribe from a channel
!whoami           - View user profile information
!weather          - Get live weather data for user's location
!fact             - Retrieve random interesting facts
!joke             - Get programming jokes
!help             - Display all available commands
```

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- OpenWeather API key (free at openweathermap.org)

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd redis-chatbot
```

2. **Configure environment variables**
```bash
# Create .env file
echo "OPENWEATHER_API_KEY=your_api_key_here" > .env
```

3. **Start the application**
```bash
# Launch containers
docker-compose up -d

# Enter Python container
docker exec -it slim_python bash

# Run the chatbot
python Chatbot.py
```

## Usage Example
```
Hello! My Name is C-bot! I am your friendly neighborhood chatbot!

Please identify yourself: cooper, 28, male, nashville
Hello cooper, you have been saved into the system!

You: !join tech-news
cooper has joined the channel: tech-news
Previous messages in tech-news:
alice: Anyone see the new Python 3.12 features?
bob: The f-string improvements are amazing!

You: !send
What channel would you like to send a message to?: tech-news
What would you like to say?: Just joined, excited to discuss!
Message sent to tech-news: Just joined, excited to discuss!

You: !weather
The current weather in Nashville is 72°F with clear sky.
```

## Technical Highlights

### Redis Implementation
- **Hashes** for structured user data storage
- **Lists** for ordered message history (FIFO with RPUSH)
- **Pub/Sub** for real-time message distribution
- **Key patterns** for organized data namespacing

### Concurrency Model
- **Threading library** enables simultaneous channel listening
- **Daemon threads** for background message reception
- **Thread-safe Redis operations** using redis-py client

### Docker Architecture
```yaml
Services:
  - redis: Message broker and data store
  - python-app: Client application with dependencies

Networks:
  - app-network: Bridge network for inter-container communication

Volumes:
  - Project directory mounted for live code updates
```

## Redis Monitoring

Monitor real-time database operations:
```bash
docker exec -it my-redis redis-cli
> MONITOR
```

**Example operations:**
- `HSET user:cooper name "Cooper"` - User profile creation
- `RPUSH channel_history:tech-news "{...}"` - Message persistence
- `PUBLISH tech-news "{...}"` - Message broadcast

## Project Structure
```
redis-chatbot/
├── Chatbot.py           # Main application code
├── docker-compose.yml   # Container orchestration
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not tracked)
├── .gitignore          # Git exclusions
└── README.md           # This file
```

## Future Enhancements
- User authentication with password hashing
- Private messaging between users
- Message persistence to disk (Redis persistence config)
- Web-based UI using Flask/FastAPI
- Rate limiting for API calls
- Emoji and markdown support in messages

## Technical Skills Demonstrated
- NoSQL database design (Redis)
- Real-time systems architecture
- Docker containerization
- API integration
- Concurrent programming
- CLI application development

## Project Context
Built as part of Vanderbilt University's NoSQL course (DS5760), enhanced for production-ready portfolio demonstration.

## License
MIT License - Feel free to use this project as a learning resource.
```

---

## **Upload Checklist (5 minutes after cleanup)**

Create GitHub repo: `redis-realtime-chat` or `redis-pubsub-chatbot`

Upload these files:
- ✅ `Chatbot.py` (cleaned)
- ✅ `docker-compose.yml` (fixed paths)
- ✅ `requirements.txt` (new)
- ✅ `README.md` (professional version)
- ✅ `.gitignore` (new)
- ❌ `.env` (do NOT upload this)

---

## **Your Resume Entry Gets Updated To:**
```
Real-Time Chat Application (Redis Pub/Sub)
- Architected multi-channel messaging system using Redis Pub/Sub for real-time communication
- Implemented concurrent message handling with Python threading for simultaneous channel subscriptions
- Dockerized application with multi-container orchestration (Redis + Python services)
- Integrated external APIs with error handling and environment-based configuration
- Technologies: Redis, Python, Docker, Pub/Sub patterns, threading, API integration

GitHub: github.com/[username]/redis-realtime-chat
