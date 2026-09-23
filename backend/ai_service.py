import os


def generate_ai_response(message: str, hotel_data: dict) -> str:
    """
    Optional AI response layer.

    If an LLM API key is configured later, this function can be
    connected to an LLM. For now, it provides a safe fallback
    using the hotel's verified knowledge base.
    """

    message_lower = message.lower()

    if "restaurant" in message_lower or "food" in message_lower:
        return (
            "Yes. Our hotel has a restaurant, and room service is also available."
        )

    if "parking" in message_lower:
        return "Yes. Free parking is available at the hotel."

    if "fitness" in message_lower or "gym" in message_lower:
        return "Yes. The hotel has a fitness center."

    if "children" in message_lower or "kids" in message_lower:
        return hotel_data["policies"]["children"]

    if "location" in message_lower or "where are you" in message_lower:
        return (
            f"Our hotel is located in {hotel_data['hotel']['location']}."
        )

    return (
        "I can help with information about our rooms, amenities, "
        "hotel policies, check-in/check-out, and availability."
    )