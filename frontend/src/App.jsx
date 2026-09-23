import { useState } from "react";
import "./App.css";
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! 👋 Welcome to our hotel. How can I help you today? You can ask me about rooms, amenities, policies, or availability.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const message = input.trim();

    if (!message || loading) return;

    const userMessage = {
      role: "user",
      content: message,
    };

    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          history: updatedMessages,
        }),
      });

      if (!response.ok) {
        throw new Error("Server error");
      }

      const data = await response.json();

      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: data.reply,
          rooms: data.rooms,
        },
      ]);
    } catch (error) {
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content:
            "Sorry, I'm unable to connect to the hotel assistant right now. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <header className="chat-header">
          <div>
            <h1>🏨 Hotel Guest Assistant</h1>
            <p>How can we help you today?</p>
          </div>
          <span className="status">● Online</span>
        </header>

        <main className="messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message-row ${message.role}`}
            >
              <div className="message">
                <div>{message.content}</div>

                {message.rooms && message.rooms.length > 0 && (
                  <div className="room-cards">
                    {message.rooms.map((room, roomIndex) => (
                      <div className="room-card" key={roomIndex}>
                        <h3>🏨 {room.type}</h3>

                        <p>
                          <strong>Capacity:</strong> {room.capacity} guests
                        </p>

                        <p>
                          <strong>Price:</strong> ${room.price_per_night} / night
                        </p>

                        <p>
                          <strong>Available rooms:</strong> {room.available_rooms}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row assistant">
              <div className="message typing">
                Assistant is typing...
              </div>
            </div>
          )}
        </main>

        <div className="quick-actions">
          <button onClick={() => setInput("What rooms do you have?")}>
            🛏️ Rooms
          </button>

          <button onClick={() => setInput("What amenities are available?")}>
            🏊 Amenities
          </button>

          <button
            onClick={() =>
              setInput("Do you have rooms available for my dates?")
            }
          >
            📅 Availability
          </button>
        </div>

        <div className="input-area">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about rooms, amenities, policies, or availability..."
            rows="2"
            disabled={loading}
          />

          <button
            className="send-button"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>

        <p className="footer-text">
          Hotel Guest Assistant • AI-powered guest support
        </p>
      </div>
    </div>
  );
}

export default App;