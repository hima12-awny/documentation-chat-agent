# Documentation Agent - Chat with Any Repo 🤖

An AI-powered assistant that allows you to chat with any GitHub repository. Clone, vector-index, and query any codebase directly through a streamlined interface.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/ibrahim-awny/)
[![Gmail](https://img.shields.io/badge/Gmail-Email-red?logo=gmail)](mailto:hima12awny@gmail.com)


![Documentation Agent Demo](https://github.com/hima12-awny/documentation-chat-agent/blob/df9e49b7118e54411dbcb3cbbf8ec074fb65228d/ss/chat_pic.png)

## 🌟 Features

- **Clone any GitHub repository**: Easily import any public GitHub repo for analysis
- **Vector database indexing**: Automatically processes and indexes repository content
- **AI-powered chat interface**: Ask questions about the codebase and get intelligent responses
- **Source attribution**: All AI responses reference the specific source files used
- **RAG (Retrieval Augmented Generation)**: Combines knowledge retrieval with generative AI
- **Interactive UI**: Built with Streamlit for a smooth user experience

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: Google Gemini (primary reasoning model)
- **Embeddings**: Cohere (vectorization and search)
- **Vector Storage**: Local disk-based vector storage
- **Repository Management**: GitPython

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Git installed on your system
- API keys for Gemini and Cohere

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/hima12-awny/documentation-chat-agent
   cd documentation-chat-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Enter your API keys in the sidebar when prompted

### Usage

1. **Data Preparation Tab**:
   - Enter a GitHub repository URL to clone
   - Or select from previously cloned repositories
   - View repository information and structure

2. **Chat Tab**:
   - Ask questions about the codebase
   - Get AI-powered responses with source references
   - The agent automatically retrieves relevant context when needed

## 📁 Project Structure

```
├── app.py                      # Main application entry point
├── data_prep_app.py            # Repository Data Preparation interface
├── chat_app.py                 # Chat interface
├── chat_ui_handler.py          # Chat UI components and logic
├── repo_cloner.py              # GitHub repository management
├── source_component.py         # Source attribution UI component
├── requirements.txt            # Project dependencies
├── agent/
│   ├── doc_agent.py            # Documentation agent implementation
│   ├── response_formatter.py   # Response formatting utilities
│   └── sys_prompt2.md          # System prompt template
└── vecdb_modules/
    └── vecdbv2.py              # Vector database implementation
```

## 🔧 How It Works

1. **Repository Management**:
   - The system clones GitHub repositories locally
   - Maintains metadata about cloned repositories

2. **Vectorization**:
   - Processes code files using language-specific text splitters, for text or Code.
   - Creates embeddings using Cohere's embedding models
   - Stores vector indices locally for persistence

3. **Query Process**:
   - User questions are analyzed by the AI
   - If needed, a search query is generated to retrieve context
   - Relevant code snippets are fetched from the vector database
   - The AI formulates a response using the retrieved context

4. **Response Generation**:
   - Responses include direct references to source files
   - Source attribution includes file names, last updated times, and URLs

## 🔑 API Keys

You'll need API keys for:
- **Google Gemini**: For AI reasoning and response generation
- **Cohere**: For text embeddings and semantic search

Enter these in the sidebar when you first run the application.

## 📧 Contact

For questions or feedback, please open an issue on this repository.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/ibrahim-awny/)
[![Gmail](https://img.shields.io/badge/Gmail-Email-red?logo=gmail)](mailto:hima12awny@gmail.com)


---

*Made with ❤️ for developers who want to understand codebases faster*
