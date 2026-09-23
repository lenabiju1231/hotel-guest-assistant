import json
import re
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from availability import check_availability
from ai_service import generate_ai_response


# ---------------------------------------------------------
# Load hotel knowledge base
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "hotel_data.json", "r", encoding="utf-8") as file:
    HOTEL_DATA = json.load(file)


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Hotel Guest Assistant API",
    description="Backend API for the Hotel Guest Assistant",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    rooms: Optional[list] = None


# ---------------------------------------------------------
# Detect availability questions
# ---------------------------------------------------------

def is_availability_question(message: str) -> bool:
    message_lower = message.lower()

    availability_phrases = [
        "room availability",
        "rooms available",
        "room available",
        "availability",
        "vacancy",
        "book a room",
        "book rooms",
        "reserve a room",
        "reserve rooms",
        "room for",
        "rooms for",
        "check availability"
    ]

    return any(
        phrase in message_lower
        for phrase in availability_phrases
    )


# ---------------------------------------------------------
# Detect date messages
# ---------------------------------------------------------

def contains_dates(message: str) -> bool:
    dates = re.findall(
        r"\b\d{4}-\d{2}-\d{2}\b",
        message
    )

    return len(dates) >= 1


# ---------------------------------------------------------
# Detect guest count messages
# ---------------------------------------------------------

def contains_guest_count(message: str) -> bool:
    patterns = [
        r"\d+\s+adults?",
        r"\d+\s+guests?",
        r"for\s+\d+\s+people",
        r"\d+\s+people"
    ]

    message_lower = message.lower()

    return any(
        re.search(pattern, message_lower)
        for pattern in patterns
    )


# ---------------------------------------------------------
# Extract check-in and check-out dates
# ---------------------------------------------------------

def extract_date_range(message: str):
    dates = re.findall(
        r"\b\d{4}-\d{2}-\d{2}\b",
        message
    )

    if len(dates) >= 2:
        return dates[0], dates[1]

    return None, None


# ---------------------------------------------------------
# Extract number of adults
# ---------------------------------------------------------

def extract_adults(message: str):
    patterns = [
        r"(\d+)\s+adults?",
        r"(\d+)\s+guests?",
        r"for\s+(\d+)\s+people",
        r"(\d+)\s+people"
    ]

    message_lower = message.lower()

    for pattern in patterns:
        match = re.search(
            pattern,
            message_lower
        )

        if match:
            return int(match.group(1))

    return None


# ---------------------------------------------------------
# Extract information from conversation history
# ---------------------------------------------------------

def extract_from_history(history: List[ChatMessage]):
    all_text = " ".join(
        item.content
        for item in history
    )

    check_in, check_out = extract_date_range(all_text)
    adults = extract_adults(all_text)

    return check_in, check_out, adults


# ---------------------------------------------------------
# Hotel knowledge-base responses
# ---------------------------------------------------------

def hotel_information_reply(message: str):
    message_lower = message.lower()

    if "check-in" in message_lower or "check in" in message_lower:
        return (
            f"Check-in starts at "
            f"{HOTEL_DATA['hotel']['check_in_time']}."
        )

    if "check-out" in message_lower or "check out" in message_lower:
        return (
            f"Check-out is until "
            f"{HOTEL_DATA['hotel']['check_out_time']}."
        )

    if "wifi" in message_lower or "wi-fi" in message_lower:
        return (
            "Yes. Free Wi-Fi is available throughout the hotel."
        )

    if "pool" in message_lower or "swimming" in message_lower:
        return (
            "Yes. The hotel has a swimming pool."
        )

    if "pet" in message_lower:
        return HOTEL_DATA["policies"]["pets"]

    if "smoking" in message_lower:
        return HOTEL_DATA["policies"]["smoking"]

    if "cancel" in message_lower:
        return HOTEL_DATA["policies"]["cancellation"]

    if "amenit" in message_lower:
        amenities = ", ".join(
            HOTEL_DATA["amenities"]
        )

        return (
            f"Our hotel amenities include: {amenities}."
        )

    if "room" in message_lower:
        room_lines = []

        for room in HOTEL_DATA["rooms"]:
            room_lines.append(
                f"{room['type']} - "
                f"capacity {room['capacity']}, "
                f"${room['price_per_night']} per night."
            )

        return (
            "Our room options are:\n"
            + "\n".join(room_lines)
        )

    return None


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "hotel-guest-assistant"
    }


# ---------------------------------------------------------
# Chat API
# ---------------------------------------------------------

@app.post(
    "/api/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:
        return ChatResponse(
            reply=(
                "Please enter a question "
                "so I can help you."
            )
        )

    # -----------------------------------------------------
    # Determine whether this belongs to availability flow
    # -----------------------------------------------------

    availability_context = (
        is_availability_question(message)
        or contains_dates(message)
        or contains_guest_count(message)
    )

    # Also check conversation history
    if request.history:
        history_text = " ".join(
            item.content.lower()
            for item in request.history
        )

        if (
            "room availability" in history_text
            or "rooms available" in history_text
            or "room available" in history_text
            or "availability" in history_text
            or "book a room" in history_text
            or "reserve a room" in history_text
        ):
            availability_context = True

    # -----------------------------------------------------
    # Availability flow
    # -----------------------------------------------------

    if availability_context:

        check_in, check_out = extract_date_range(message)
        adults = extract_adults(message)

        # Look at previous conversation if current message
        # does not contain all required information.
        history_check_in, history_check_out, history_adults = (
            extract_from_history(request.history)
        )

        if not check_in:
            check_in = history_check_in

        if not check_out:
            check_out = history_check_out

        if not adults:
            adults = history_adults

        # Ask for dates
        if not check_in or not check_out:
            return ChatResponse(
                reply=(
                    "I'd be happy to check room availability. "
                    "Please provide your check-in and check-out "
                    "dates in YYYY-MM-DD format."
                )
            )

        # Ask for guest count
        if not adults:
            return ChatResponse(
                reply=(
                    "Great, I have your check-in and check-out "
                    "dates. How many adults will be staying?"
                )
            )

        # Check availability
        result = check_availability(
            check_in,
            check_out,
            adults
        )

        if not result["success"]:
            return ChatResponse(
                reply=result["error"]
            )

        # No rooms
        if not result["rooms"]:
            return ChatResponse(
                reply=(
                    f"Sorry, there are no available rooms "
                    f"for {adults} adults for those dates."
                )
            )

        # Format rooms
        room_lines = []

        for room in result["rooms"]:
            room_lines.append(
                f"• {room['type']} — "
                f"${room['price_per_night']} per night "
                f"(capacity {room['capacity']})"
            )

        reply = (
            f"Good news! Rooms are available from "
            f"{check_in} to {check_out} "
            f"for {adults} adults:\n\n"
            + "\n".join(room_lines)
        )

        return ChatResponse(
            reply=reply,
            rooms=result["rooms"]
        )

    # -----------------------------------------------------
    # Hotel knowledge-base flow
    # -----------------------------------------------------

    reply = hotel_information_reply(message)

    if reply:
        return ChatResponse(
            reply=reply
        )

    # -----------------------------------------------------
    # AI / safe fallback
    # -----------------------------------------------------

    ai_reply = generate_ai_response(
        message,
        HOTEL_DATA
    )

    return ChatResponse(
        reply=ai_reply
    )