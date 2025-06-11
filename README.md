# 🐚 ShellMate - Your Gemini-powered CLI Assistant

**ShellMate** is a smart terminal companion that helps you:

* 📄 Read files
* ✍️ Write content to files
* 🔍 Search inside files
* 🌐 Perform Google searches
* 🧠 Review code with AI

---

## ⚙️ Setup Instructions

Follow these steps to get started:

---

### 1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/shellmate.git
cd shellmate
```

---

### 2. **Add API Keys**

Create a `.env` file in the project root and add your API keys:

```
GEMINI_API_KEY=your_google_genai_key_here
google_search_api=your_google_search_api_key_here
search_engine_id=your_custom_search_engine_id_here
```

These are required for Google GenAI and Web Search integrations to work.

---

### 3. **Install Dependencies**

Using **pnpm**:

```bash
pnpm install
```

Or using **npm**:

```bash
npm install
```

---

### 4. **Make the CLI Available Globally**

Using **pnpm**:

```bash
pnpm setup    # Only if not already done
pnpm link
```

Using **npm**:

```bash
npm link
```

---

### ✅ Done!

You can now run `shellmate` from anywhere in your terminal.
