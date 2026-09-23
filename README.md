# Hotel Guest Assistant

A full-stack AI-powered hotel guest assistant built with React, FastAPI, and a hotel knowledge base.

## Features

- Hotel information and FAQ support
- Room and amenity information
- Check-in and check-out information
- Hotel policy questions
- Room availability checking
- Follow-up conversation support
- Room availability cards
- Safe fallback for unsupported questions
- Backend API
- Automated backend tests
- Responsive chat interface

## Architecture

The application follows a simple full-stack architecture:

React Frontend  
↓  
FastAPI Backend  
↓  
Hotel Knowledge Base + Availability Logic  
↓  
Safe AI/Fallback Response

### Frontend

- React
- Vite
- Responsive chat interface
- Calls the backend API
- Displays messages, loading states, errors, and room cards

### Backend

- Python
- FastAPI
- Pydantic request/response validation
- Hotel knowledge base stored in JSON
- Deterministic room availability logic
- Conversation history support
- Safe fallback for unsupported questions

### Data Flow

1. Guest enters a question in the React chat interface.
2. Frontend sends the question and conversation history to the FastAPI backend.
3. Backend checks the hotel knowledge base and request type.
4. Availability requests are handled using deterministic business logic.
5. Hotel information is returned from verified hotel data.
6. Unsupported questions receive a safe fallback response.
7. Backend response is displayed in the chat interface.

## API

### Health Check

**GET**

`/health`

Example response:

```json
{
  "status": "ok"
}


### Chat

**POST**

`/api/chat`

Request:

```json
{
  "message": "Do you have rooms available?",
  "history": []
}