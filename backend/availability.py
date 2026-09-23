from datetime import date


ROOMS = [
    {
        "type": "Standard Room",
        "capacity": 2,
        "price_per_night": 100,
        "available_rooms": 3
    },
    {
        "type": "Deluxe Room",
        "capacity": 3,
        "price_per_night": 150,
        "available_rooms": 2
    },
    {
        "type": "Family Suite",
        "capacity": 4,
        "price_per_night": 220,
        "available_rooms": 1
    }
]


def check_availability(check_in: str, check_out: str, adults: int):
    """
    Deterministic mock room availability checker.

    Args:
        check_in: Check-in date in YYYY-MM-DD format.
        check_out: Check-out date in YYYY-MM-DD format.
        adults: Number of adult guests.

    Returns:
        A dictionary containing available rooms or an error.
    """

    try:
        check_in_date = date.fromisoformat(check_in)
        check_out_date = date.fromisoformat(check_out)
    except ValueError:
        return {
            "success": False,
            "error": "Please provide dates in YYYY-MM-DD format."
        }

    if check_out_date <= check_in_date:
        return {
            "success": False,
            "error": "Check-out date must be after check-in date."
        }

    if adults < 1:
        return {
            "success": False,
            "error": "Number of adults must be at least 1."
        }

    available_rooms = []

    for room in ROOMS:
        if room["capacity"] >= adults and room["available_rooms"] > 0:
            available_rooms.append({
                "type": room["type"],
                "capacity": room["capacity"],
                "price_per_night": room["price_per_night"],
                "available_rooms": room["available_rooms"]
            })

    return {
        "success": True,
        "check_in": check_in,
        "check_out": check_out,
        "adults": adults,
        "rooms": available_rooms
    }