# ArXiv Paper Processor - Modular Design

A modular, efficient arXiv paper processor that fetches recent papers, summarizes them using Google's Gemini AI, and sends concise summaries to Slack. Designed for cost and speed optimization with efficient batching.

## Features

- **Modular Design**: Clean separation of concerns with reusable components
- **Efficient Batching**: Process papers in batches to minimize token usage and costs
- **Slack Integration**: Send formatted summaries directly to Slack channels
- **Error Handling**: Robust error handling with retry logic
- **File Management**: Save results to organized files with timestamps
- **Multi-subject Support**: Process multiple arXiv subjects simultaneously
- **Cost Optimization**: Token usage monitoring and batch size optimization

## Architecture

The application is built with a modular design consisting of:

- **`config.py`**: Centralized configuration management
- **`arxiv_client.py`**: ArXiv API client with retry logic
- **`gemini_processor.py`**: Gemini AI processor with efficient batching
- **`slack_notifier.py`**: Slack integration with message formatting
- **`file_manager.py`**: File management and organization
- **`arxiv_processor.py`**: Main orchestrator class
- **`main.py`**: Command-line interface

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

**Option 1: Using .env file (Recommended)**

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API keys:
   ```bash
   # Edit .env file with your actual API keys
   GEMINI_API_KEY=your_actual_gemini_api_key
   SLACK_BOT_TOKEN=xoxb-your_actual_slack_bot_token
   SLACK_CHANNEL_ID=C1234567890
   ```

**Option 2: Using environment variables**

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export SLACK_BOT_TOKEN="your-slack-bot-token"
export SLACK_CHANNEL_ID="your-channel-id"
```

### 3. Get API Keys

- **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Slack Bot Token**: Create a Slack app and get the bot token
- **Slack Channel ID**: The channel where you want to send messages

## Usage

### Basic Usage

Process papers for the default subject (astro-ph.GA):

```bash
python main.py
```

### Process Multiple Subjects

```bash
python main.py --subjects astro-ph.GA quant-ph cond-mat.mtrl-sci
```

### Customize Results

```bash
python main.py --subjects astro-ph.GA --max-results 15 --min-results 0
```

### Test Connections

```bash
python main.py --test-connections
```

### Show Statistics

```bash
python main.py --stats
```

### Save to File Only (No Slack)

```bash
python main.py --no-slack
```

### Send to Slack Only (No File)

```bash
python main.py --no-file
```

## Configuration

Edit `config.py` to customize:

- **Batch Size**: Number of papers processed together (default: 5)
- **Max Tokens per Batch**: Token limit for cost optimization (default: 4000)
- **Default Subject**: Default arXiv category (default: astro-ph.GA)
- **Slack Message Length**: Maximum message length for Slack (default: 3000)

## Cost Optimization Features

1. **Efficient Batching**: Papers are processed in batches to reduce API calls
2. **Token Estimation**: Rough token estimation to prevent exceeding limits
3. **Abstract Truncation**: Long abstracts are truncated to save tokens
4. **Batch Size Control**: Configurable batch sizes for optimal cost/speed balance

## Error Handling

- **Retry Logic**: Automatic retries with exponential backoff
- **Connection Testing**: Test all external services before processing
- **Error Notifications**: Send error alerts to Slack
- **Graceful Degradation**: Continue processing even if some components fail

## File Organization

Results are saved in the `output/` directory with timestamps:

```
output/
├── astro_ph_GA_2024-01-15_14-30-25.md
├── quant_ph_2024-01-15_14-35-10.md
└── multi_subject_arxiv_2024-01-15_14-40-00.md
```

## Slack Integration

The Slack integration includes:

- **Message Formatting**: Convert markdown to Slack-compatible format
- **Link Handling**: Proper link formatting for arXiv papers
- **Message Splitting**: Split long messages to fit Slack limits
- **Error Notifications**: Send error alerts to Slack
- **Connection Testing**: Test Slack connectivity

## Performance Monitoring

The system provides:

- **Processing Time**: Track how long operations take
- **Token Usage**: Monitor API token consumption
- **File Statistics**: Track saved files and disk usage
- **Connection Status**: Monitor external service connectivity

## Examples

### Process Recent Astrophysics Papers

```bash
python main.py --subjects astro-ph.GA astro-ph.CO --max-results 10
```

### Process Quantum Computing Papers

```bash
python main.py --subjects quant-ph --max-results 20
```

### Process Multiple Physics Categories

```bash
python main.py --subjects cond-mat.mtrl-sci cond-mat.soft physics.optics --max-results 5
```

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Set all required environment variables
2. **Slack Permission Errors**: Ensure your Slack bot has permission to post to the channel
3. **Rate Limiting**: The system includes retry logic, but you may need to reduce batch sizes
4. **Token Limits**: Adjust `MAX_TOKENS_PER_BATCH` in config.py if you hit limits

### Testing

```bash
# Test all connections
python main.py --test-connections

# Test with minimal data
python main.py --subjects astro-ph.GA --max-results 1 --no-slack
```

## Contributing

The modular design makes it easy to extend:

1. **Add New Processors**: Create new processor classes in separate modules
2. **Add New Notifiers**: Implement new notification channels
3. **Add New File Formats**: Extend the file manager for new formats
4. **Add New Subjects**: Simply pass new arXiv categories to the processor

## License

This project is open source and available under the MIT License. 