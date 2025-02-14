# Communication Agent API

A FastAPI-based communication agent that provides intelligent email response generation and chat capabilities using the DeepScaleR model through Ollama.

## About DeepScaleR

DeepScaleR is a 1.5B parameter language model fine-tuned using distributed reinforcement learning. It excels at:
- Mathematical reasoning and problem-solving
- Precise and accurate responses
- Handling complex queries with structured thinking
- Supporting long context windows (up to 24K tokens)

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running
- DeepScaleR model (yasserrmd/DeepScaleR-1.5B-Preview:latest) pulled in Ollama

## Features

### Core Features
- Advanced email response generation with support agent perspective
- Intelligent tone control system with 5 distinct tones
- Context-aware responses with structured formatting
- Support for various customer inquiry types (technical, billing, urgent, etc.)
- Response cleaning and standardization
- Conversation memory and history
- Performance metrics and execution timing
- Structured JSON output with metadata

### Response Structure
Each email response follows a standardized format:
1. Acknowledgment of the specific issue
2. Immediate action items or workarounds
3. Next steps and timeline
4. Contact information and availability
5. Case reference or ticket number

### Support Agent Guidelines
- Immediate acknowledgment of urgency/priority
- Specific, actionable steps
- Status updates and ETAs for known issues
- Concrete next steps with contact information
- Immediate workarounds for urgent issues
- Timeline expectations
- Department and case reference information

### Technical Features
- RESTful API endpoints with async support
- LangChain integration with OllamaLLM
- Response processing and cleaning
- Structured logging system
- Configuration management
- CORS middleware
- OpenAPI documentation
- Optimized DeepScaleR integration

## Tone System

The API supports five different tones for email responses, each designed for specific use cases:

### Professional (Default)
- Clear, concise, and business-appropriate
- Best for: Standard business communications
- Example: Technical support, general inquiries

### Friendly
- Warm and approachable while maintaining professionalism
- Best for: Customer success, positive feedback
- Example: Feature requests, general assistance

### Formal
- Traditional and respectful with appropriate distance
- Best for: Legal matters, compliance issues
- Example: Documentation requests, regulatory inquiries

### Empathetic
- Understanding and supportive, acknowledging feelings
- Best for: Complaint handling, issue resolution
- Example: Service disruptions, customer concerns

### Direct
- Straightforward and to the point
- Best for: Urgent matters, critical updates
- Example: System outages, security issues

## API Endpoints

### Email Response Generation
- `POST /api/v1/email/respond`: Generate customer email responses
  - Supports tone control
  - Accepts customer context
  - Returns timing metrics
  - Provides structured JSON output

### Chat Interface
- `POST /api/v1/chat`: Chat with the AI agent
- `GET /api/v1/chat/history`: Get conversation history
- `POST /api/v1/chat/clear`: Clear conversation history

### System
- `GET /`: Health check
- `GET /api/v1/status`: Service status

## Example Usage

### Technical Support Issue
```bash
curl -X POST http://localhost:8000/api/v1/email/respond \
  -H "Content-Type: application/json" \
  -d '{
    "customer_message": "The new software update (v2.3.4) keeps crashing when I try to export large files. My deadline is tomorrow morning!",
    "tone": "professional",
    "context": {
      "customer_name": "Dr. Michael Chen",
      "account_type": "Enterprise",
      "priority": "High",
      "department": "Technical Support"
    },
    "max_length": 500
  }'
```

### Urgent System Outage
```bash
curl -X POST http://localhost:8000/api/v1/email/respond \
  -H "Content-Type: application/json" \
  -d '{
    "customer_message": "URGENT: Our production system is down after the latest API update. Losing revenue every hour!",
    "tone": "direct",
    "context": {
      "customer_name": "David Kumar",
      "account_type": "Enterprise Plus",
      "priority": "Critical",
      "department": "Emergency Support",
      "customer_history": "Integration partner"
    },
    "max_length": 500
  }'
```

### Response Format
```json
{
  "message": "Dear [Customer Name],\n\n[Response Body]\n\nBest regards,\n[Agent Name]\n[Department]",
  "status_code": 200,
  "execution_time_ms": 1234.56,
  "metadata": {
    "tone_used": "professional",
    "context_length": 789,
    "generation_settings": {
      "temperature": 0.3,
      "max_tokens": 4096,
      "top_p": 0.9,
      "top_k": 40
    },
    "timestamp": "2024-03-14T12:34:56.789Z"
  }
}
```

## Testing Guidelines

### Test Scenarios
1. Technical Issues
   - Software bugs
   - Integration problems
   - Performance issues

2. Account Management
   - Billing disputes
   - Access problems
   - Configuration issues

3. Urgent Matters
   - System outages
   - Critical bugs
   - Time-sensitive issues

4. General Inquiries
   - Feature requests
   - Documentation needs
   - Product information

### Response Evaluation
- Verify tone appropriateness
- Check for actionable steps
- Confirm timeline inclusion
- Validate contact information
- Review case reference format

## Setup and Configuration

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate

# Verify you're in the virtual environment (should show path to venv)
which python
```

2. Install dependencies in the virtual environment:
```bash
# Make sure you're in the virtual environment (you should see (venv) in your prompt)
pip install --upgrade pip
pip install -r requirements.txt
```

3. Create a `.env` file (optional):
```env
DEBUG=True
LOG_LEVEL=INFO
PORT=8000
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=yasserrmd/DeepScaleR-1.5B-Preview:latest

# Model settings optimized for DeepScaleR
TEMPERATURE=0.3
MAX_TOKENS=4096
TOP_P=0.9
TOP_K=40
```

4. Pull the DeepScaleR model in Ollama:
```bash
ollama pull yasserrmd/DeepScaleR-1.5B-Preview:latest
```

## Running the Application

Make sure you're in the virtual environment (you should see `(venv)` in your prompt), then start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- OpenAPI Spec: http://localhost:8000/api/v1/openapi.json

## Development

### Project Structure
```
communication_agent/
├── app/
│   ├── api/          # API routes and endpoints
│   ├── core/         # Core functionality (config, logging)
│   ├── models/       # Data models and schemas
│   └── services/     # Business logic and services
├── tests/            # Test suite
├── .env             # Environment variables
└── README.md        # Documentation
```

## Model Configuration

The DeepScaleR model is configured with optimized parameters:
- Temperature: 0.3 (for precise responses)
- Max Tokens: 4096
- Top P: 0.9
- Top K: 40

These settings are optimized for:
- Email response generation
- Customer service interactions
- Precise and accurate responses
- Context-aware communication

## Error Handling

The API includes comprehensive error handling:
- Input validation errors (400)
- Internal server errors (500)
- Service unavailability (503)
- Detailed error messages and logging

## License

MIT 