


# HiringAgent-AI — A Crew of AI Agents Hiring Smarter 🤖

An **agentic AI-powered resume screening system** that automates the hiring pipeline using a crew of specialized AI agents.  
From scraping job postings to embedding-based filtering, LLM analysis, and interview scheduling, **HiringAgent-AI** makes recruitment faster, smarter, and more objective.

---

##  Features

- **Multi-Agent Workflow (CrewAI)**  
  Scraper → Embedding Filter → LLM Analysis → Decision → (Optional) Google Meet Scheduling
- **Job Posting Scraper** — Extracts job title, skills, and requirements from any provided job URL.
- **Resume Screening** — Reads & parses PDF resumes using PyMuPDF.
- **Semantic Filtering** — Embedding similarity search to quickly filter out irrelevant resumes.
- **LLM Reasoning Agent** — Uses GPT models for deep analysis of candidate-job fit.
- **Automated Decisions** — Pass/fail results with detailed reasoning.
- **Google Meet Scheduling** — For candidates who pass screening.
- **Streamlit UI** — Simple drag-and-drop resume uploads + job URL input.

---

## 🗂 Project Structure

```

HiringAgent-AI/
│
├── config/                  # Configuration files
│   ├── **init**.py
│   └── settings.py
│
├── data\_resumes/            # Sample resumes for testing
│   ├── Abhinav\_yadav\_resume.pdf
│   ├── Akshansh\_Verma\_Resume.pdf
│   ├── GauravResume7.pdf
│   └── resumeWithFineTuning.pdf
│
├── myenv/                   # Virtual environment (not tracked in Git)
│
├── src/
│   ├── agents/              # Agent definitions
│   │   ├── agents.py
│   │   └── interview\_schedule.py
│   ├── services/            # Supporting service modules
│   ├── tools/               # Utility tools for scraping, parsing, embeddings
│   ├── main.py              # Entry point for CLI usage
│   ├── resume\_processor.py  # Core multi-agent orchestration logic
│   └── web\_app.py           # Streamlit front-end
│
├── temp/                    # Temporary files during processing
│
├── templates/               # HTML templates for UI
│   └── index.html
│
├── .env                     # Environment variables (not tracked in Git)
├── .gitignore               # Ignored files & folders
├── credentials.json         # Google API credentials (DO NOT COMMIT)
├── requirements.txt         # Python dependencies
├── token.json               # OAuth tokens (DO NOT COMMIT)
└── token.pickle             # Pickle version of tokens (DO NOT COMMIT)

````

---

## ⚙ Tech Stack

| Component         | Technology Used                     |
|-------------------|-------------------------------------|
| **Frontend**      | Streamlit                           |
| **Agents**        | CrewAI                              |
| **Resume Parsing**| PyMuPDF, pdfminer.six                |
| **Embeddings**    | OpenAI Embeddings / HuggingFace      |
| **Reasoning**     | GPT-3.5                       |
| **Scheduling**    | Google Calendar API (Meet links)     |
| **Storage**       | Local files (sample resumes)         |

---

##  Installation

```bash
# Clone the repository
git clone https://github.com/Gaurav9693089415/HiringAgent-AI---A-crew-of-AI-agents-hiring-smarter-.git
cd HiringAgent-AI---A-crew-of-AI-agents-hiring-smarter-

# Create virtual environment
python -m venv myenv

# Activate virtual environment
# Windows:
myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
````

---

##  Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
RECRUITER_EMAIL=your email id 
```

**Note:**

* Keep `.env`, `credentials.json`, `token.json`, and `token.pickle` out of Git.
* Add them to `.gitignore` to prevent accidental commits.

---

## ▶ Running the App

### **Streamlit UI**

```bash
streamlit run src/web_app.py
```

Then open the displayed local URL in your browser.

### **Command-line Usage**

```bash
python src/main.py --job_url "<job_posting_url>" --resumes "data_resumes/"
```

---

##  How It Works

1. **Job Scraper Agent**
   Scrapes and extracts the key skills & requirements from the provided job posting URL.
2. **Embedding Filter Agent**
   Converts job and resume content into embeddings for quick relevance filtering.
3. **LLM Analysis Agent**
   Performs detailed semantic analysis of matching resumes and generates reasoning.
4. **Decision Agent**
   Scores candidates and decides whether they pass the initial screening.
5. **Interview Scheduling Agent** 
   Uses Google Meet API to set up interviews for passing candidates.

---

##  Security Recommendations

* Never commit secrets or credentials — `.gitignore` is already configured.
* Rotate API keys if you suspect exposure.
* Use environment variables for all sensitive data.

---

##  Contributing

Contributions are welcome!
Fork the repo, make changes, and open a Pull Request.
Please ensure that you do **not commit any secrets**.

---

##  License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

##  Author

**Gaurav**
Building intelligent tools to make hiring more efficient, unbiased, and automated.

```



