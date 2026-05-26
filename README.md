# Tactical Multiplayer Server ⚡

A lightweight, real-time WebSocket backend built with **FastAPI** to power turn-based multiplayer games.

This server acts as the dedicated matchmaking and routing engine for the Arcade sector of my interactive developer portfolio. It handles live connection pooling, private room routing, and state broadcasting so players can compete in real-time.

## 🎯 Core Features
* **Private Game Lobbies:** Players can spin up isolated, secure game rooms using custom 6-character OP-CODEs.
* **Real-Time Broadcasting:** Fast, asynchronous WebSocket connections for zero-latency move syncing.
* **Auto-Cleanup Engine:** The server intelligently monitors active connections and instantly flushes empty rooms from memory to keep performance lean and optimized.

## 🛠️ Tech Stack
* **Language:** Python
* **Framework:** FastAPI
* **Protocols:** WebSockets

## 🚀 Architecture Overview
The server runs a stateless `ConnectionManager` that maps unique Room IDs to arrays of active WebSocket connections. Because it bypasses traditional HTTP polling in favor of persistent TCP connections, it is heavily optimized for fast-paced, turn-based browser games.
