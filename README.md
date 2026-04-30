# 🤖 frame-forge-backend - Real-time AI backend for FrameForge

[![Download FrameForge Backend](https://img.shields.io/badge/Download-FrameForge%20Backend-blue?style=for-the-badge)](https://github.com/unimpressionable-laconian269/frame-forge-backend/releases)

## 🖥️ What this is

Frame Forge Backend is the server part of FrameForge. It runs on your computer and handles the work behind the scenes.

It:
- takes in prompts
- sends them through an AI pipeline
- keeps track of the conversation
- streams results back to the app
- separates explanation text from React code
- saves the chat history in MongoDB

Use this if you want the FrameForge app to generate code and answer in real time on Windows.

## 📦 What you need

Before you install it, check that you have:

- Windows 10 or Windows 11
- A stable internet connection
- A web browser
- MongoDB running locally or in the cloud
- An OpenRouter account and API key
- Enough free disk space for the app and logs

If you plan to run it with Docker, you also need Docker Desktop for Windows

## ⬇️ Download it

Visit this page to download the latest release for Windows:

[Download FrameForge Backend](https://github.com/unimpressionable-laconian269/frame-forge-backend/releases)

On that page, look for the latest release and download the file made for Windows. If there are several files, pick the one that matches your system.

## 🪟 Install on Windows

### 1. Download the release file
Open the releases page and download the Windows file.

### 2. Open the download
Go to your Downloads folder and find the file you just downloaded.

### 3. Run the app
If the release gives you an `.exe` file, double-click it.

If the release gives you a `.zip` file, right-click it, choose Extract All, then open the extracted folder and run the app file inside.

### 4. Allow access if Windows asks
Windows may ask for permission to run the file. Choose Run or More info, then Run anyway if you trust the source.

### 5. Keep the app open
Leave the backend running while you use the FrameForge frontend.

## ⚙️ Set up your environment

FrameForge Backend needs a few settings before it can work well.

You may need to set these values in a `.env` file or in your app settings:

- `OPENROUTER_API_KEY` for AI requests
- `MONGODB_URI` for saving chat data
- `PORT` for the local server port
- `HOST` for the address the app listens on

A common setup looks like this:
- OpenRouter API key: from your OpenRouter account
- MongoDB URI: `mongodb://localhost:27017`
- Port: `8000`

If you use a cloud MongoDB service, place that connection string in the same MongoDB field

## 🧠 What the backend does

The backend handles the full flow from prompt to answer.

It:
- receives the user prompt
- rebuilds thread context from stored messages
- sends the request into a multi-agent AI flow
- uses OpenRouter in streaming mode
- returns output as it is generated
- separates plain explanation from React code
- stores the final conversation in MongoDB

This helps the frontend show live updates instead of waiting for a full response

## 🔌 How it connects to the frontend

The frontend sends a request to this backend when the user starts a chat or asks for code.

The backend then:
- keeps the chat thread in order
- sends updates as NDJSON or streamed chunks
- returns the final result when the AI task ends
- stores the message history for later use

If the frontend stops and starts again, the backend can use the saved thread context to continue the same conversation

## 🗂️ Data stored by the app

Frame Forge Backend stores conversation data in MongoDB. This can include:

- prompts
- AI replies
- thread IDs
- timestamps
- agent output
- code blocks
- audit logs

This makes it easier to review what happened during a session

## 🚨 If the app does not start

Try these checks in order:

1. Make sure the release file finished downloading
2. Confirm that Windows blocked the file
3. Check that MongoDB is running
4. Make sure your OpenRouter API key is valid
5. Confirm that nothing else is using the same port
6. Restart the app after changing any settings

If the app opens but the frontend cannot connect, check the backend address and port first

## 🧪 For local testing

You can test the backend on your own machine before using it with the frontend.

Common checks:
- open the server URL in your browser
- verify that the health route responds
- send a test prompt from the frontend
- confirm that the response streams in chunks
- check that messages appear in MongoDB

This helps confirm that the API, database, and AI connection all work together

## 🐳 Run with Docker

If you prefer Docker, you can run Frame Forge Backend in a container.

Typical steps:
1. Install Docker Desktop
2. Download or clone the project
3. Set your environment values
4. Start the container
5. Make sure MongoDB is reachable from the container

Docker works well if you want the same setup on more than one machine

## 🔐 API and connection details

The backend uses a FastAPI server and exposes endpoints that the frontend calls in real time.

Common parts of the setup:
- REST endpoints for prompt handling
- streamed responses for live output
- NDJSON for event-based updates
- database access through Motor
- request models handled with Pydantic

You do not need to manage these parts by hand when you run the release, but they are part of how the app works

## 🛠️ Common files and folders

If you open the project files, you may see folders and files for:

- API routes
- database code
- AI orchestration
- streaming handlers
- config values
- tests
- logs

These parts help the backend manage chat flow, code generation, and persistence

## 📋 Basic use flow

1. Start MongoDB
2. Start the Frame Forge Backend
3. Open the frontend app
4. Enter a prompt
5. Watch the response stream in real time
6. Save or review the generated result

## 🧩 Works best with

This backend fits well with:
- a React frontend
- OpenRouter models
- MongoDB
- local development on Windows
- streaming chat-based code generation

## 📎 Release page

Use this page to get the latest Windows build:

[Go to releases](https://github.com/unimpressionable-laconian269/frame-forge-backend/releases)

