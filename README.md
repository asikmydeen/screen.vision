<div align="center">

# Screen Vision

### Get a guided tour for anything, right on your screen.

</div>

![Screen Vision Demo](demo.gif)

## How It Works

The system is straightforward:

1. **You describe your goal** — "I want to set up two-factor authentication on my Google account" or "Help me configure my Git SSH keys"

2. **You share your screen** — The app uses your browser's built-in screen sharing (the same tech used for video calls)

3. **AI analyzes what it sees** — Vision language models look at your screen and figure out the current state

4. **You get one instruction at a time** — No information overload. Just "Click the blue Settings button in the top right" or "Scroll down to find Security"

5. **Automatic progress detection** — When you complete a step, Screen Vision notices the screen changed and automatically gives you the next instruction

## Models Used

| Model                     | Provider        | Purpose                                                                                |
| ------------------------- | --------------- | -------------------------------------------------------------------------------------- |
| **Claude Sonnet 4**       | AWS Bedrock     | Primary reasoning: generates step-by-step instructions and answers follow-up questions |
| **Claude 3.5 Haiku**      | AWS Bedrock     | Step verification: compares before/after screenshots to confirm action completion      |
| **Claude Sonnet 4**       | AWS Bedrock     | Coordinate detection: locates specific UI elements on screen using vision capabilities |

## Privacy & Security

Screen Vision is designed to process your data securely without retaining it.

- **Zero Data Retention**: No images or screen recordings are stored on the server. All processing happens in real-time, and data is discarded immediately after analysis.
- **Secure AI Processing**: Screenshots are sent to AWS Bedrock (Amazon's managed AI service) solely for analysis. AWS Bedrock adheres to strict data handling policies and does not store or use your data to train models.
  - [AWS Bedrock Data Protection](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)

## Tech Stack

- **Frontend**: Next.js 13, React 18, Tailwind CSS, Zustand
- **Backend**: FastAPI, Python
- **AI**: AWS Bedrock (Claude Sonnet 4, Claude 3.5 Haiku)
- **UI**: Radix primitives, Framer Motion, Lucide icons

**Frontend (Next.js + React)**

- Handles screen capture via the MediaDevices API
- Runs change detection by comparing scaled-down frames
- Manages the PiP window for always-on-top instructions
- Masks its own window from screenshots (so the AI doesn't see itself)

**Backend (FastAPI + Python)**

- `/api/step` — Given a goal and screenshot, returns the next single instruction
- `/api/check` — Compares before/after screenshots to verify if a step was completed
- `/api/help` — Answers follow-up questions about what's on screen
- `/api/coordinates` — Locates specific UI elements when needed

## Self-Hosting

### Prerequisites

- Node.js 18+
- Python 3.10+
- pnpm (or npm/yarn)

### Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/bullmeza/screen.vision.git
cd screen.vision

# Frontend
pnpm install

# Backend
pip install -r requirements.txt
```

### Configuration

Create a `.env.local` file in the root directory:

```bash
# AWS Credentials for Bedrock
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
```

The app uses AWS Bedrock with Claude models for all AI operations. You'll need an AWS account with Bedrock access enabled in your region. You can configure AWS credentials either through environment variables (as shown above) or through standard AWS credential methods (IAM roles, AWS profiles, etc.).

### Running Locally

Start both the frontend and backend with a single command:

```bash
npm run dev
```

This runs:

- Next.js dev server on `http://localhost:3000`
- FastAPI server on `http://localhost:8000`

Open your browser to `http://localhost:3000` and you're good to go.

### Running in Production

For production deployments:

```bash
# Build the frontend
npm run build

# Start the frontend
npm run start

# Run the API separately
uvicorn api.index:app --host 0.0.0.0 --port 8000
```

Or use the included `Procfile` for platforms like Railway or Heroku.
