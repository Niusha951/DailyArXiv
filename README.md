# 📚 arxiv-gemini-slack-bot

A lightweight Python bot that searches arXiv papers based on keyword and subject-based queries. It uses Google's **Gemini 1.5 Flash** model to summarize the most recent papers and posts the results directly to a specified Slack channel.

Ideal for research groups, astronomers, physicists, or developers who want to stay updated on the latest literature in their field — without leaving Slack.

---

## ✨ Features

- 🔍 Search recent arXiv papers by **keywords** and/or **subject category**
- 🤖 Summarize abstracts using **Gemini 1.5 Flash** with optimized token usage
- 🧵 Send well-formatted messages to Slack channels via a bot
- 🧪 Built-in batching support for querying multiple topics
- ✅ Fallback to saving results locally as Markdown if Slack fails

---

## 📦 Installation

Clone the repo and create a virtual environment:

```bash
git clone https://github.com/Niusha951/DailyArXiv.git
cd DailyArXiv

# Create and activate a virtual environment
python3.9 -m venv venv
source venv/bin/activate   

# Install dependencies
pip install -r requirements.txt
```
## ⚙️ Configuration

Create a `.env` file in the project root to store your API credentials:

```
GEMINI_API_KEY=your_google_gemini_api_key
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_CHANNEL_ID=your_channel_id
```

Make sure your Slack bot has permission to post to the specified channel.

## 🚀 Usage

Run the bot with your desired topic and keywords:

```
python simple_arxiv_search.py --subject "astro-ph.GA" --keywords "dwarf galaxies Milky Way"
```
You’ll receive a summarized update of the most recent arXiv papers directly in your Slack channel.

## 🛠️ Customization

You can tweak the following options:

- `max_results`: Number of papers to fetch (default: 3)
- `subject`: Restrict search to a specific arXiv category (e.g., `astro-ph.GA`)
- `keywords`: Use multiple keywords (space-separated)

## 🧪 Dependencies

See `requirements.txt` for full list. 

## 🤝 Acknowledgments

- [arXiv API](https://info.arxiv.org/help/api/index.html)
- [Google Gemini Models](https://ai.google.dev/)
- [Slack Web API](https://api.slack.com/)
