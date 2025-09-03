# Technology Stack

This document provides an overview of the technologies, frameworks, and tools used in the Meal Planner application.

## Backend Technologies

*   **Language:** Python 3.9
*   **Framework:** Flask
    *   *Description:* A lightweight WSGI web application framework used to build the backend API and server-rendered pages.
*   **PDF Generation:** fpdf2
    *   *Description:* A Python library used for generating PDF documents, intended for the "Export to PDF" feature.

## Frontend Technologies

*   **Core Library:** React (v18.2.0)
    *   *Description:* A JavaScript library for building modern, interactive user interfaces. Used for the new UI at the `/ui/` endpoint.
*   **DOM Rendering:** React DOM (v18.2.0)
    *   *Description:* The companion library to React that renders components in the web browser.
*   **Templating (Legacy):** Jinja2
    *   *Description:* A templating engine for Python, used by Flask to render the traditional server-side pages of the application.

## Styling

*   **CSS Framework:** Tailwind CSS (v3.0.0)
    *   *Description:* A utility-first CSS framework used for styling both the Jinja2 templates and the React components.
*   **CSS Processing:** PostCSS / Autoprefixer
    *   *Description:* Tools used to process and add vendor prefixes to the CSS for better browser compatibility.

## Build Tools & Package Management

*   **Backend Package Manager:** pip
    *   *Description:* The standard package manager for Python, used to install dependencies defined in `pyproject.toml`.
*   **Frontend Build Tool:** Vite (v4.4.5)
    *   *Description:* A modern frontend build tool that provides a fast development server (with Hot Module Replacement) and bundles the React application for production.
*   **JavaScript Package Manager:** npm
    *   *Description:* The Node Package Manager, used to manage all JavaScript dependencies for both the React application and the build tools.
*   **Code Linting:**
    *   **Pylint:** For Python code quality.
    *   **ESLint:** For JavaScript and React code quality.

## Development & Deployment Environment

*   **Containerization:** Docker
    *   *Description:* The application is configured to run inside a Docker container, ensuring a consistent and reproducible environment.
*   **Base OS:** Debian (via `python:3.9-slim` image)
    *   *Description:* The Docker container is built on top of a slim version of the Debian Linux distribution.
*   **Runtime:** Node.js (v18.x)
    *   *Description:* The JavaScript runtime required for installing dependencies and running all build tools (Vite, Tailwind CSS, etc.).
*   **Web Server:** Flask Development Server
    *   *Description:* The built-in development server provided by Flask is used to serve the application from within the container.

## Technology Recommendations for New Features

This section provides suggestions for libraries and tools that could be used to implement the new features outlined in the requirements document.

### Automatic Recipe Discovery

*   **Web Searching (for Search-Based Discovery):**
    *   **Recommendation:** Use a dedicated search engine API like the **Google Custom Search JSON API**. This is more reliable and robust than attempting to scrape search engine result pages directly. There are Python client libraries available to simplify its use.
*   **Web Crawling/Scraping (for URL-Based Extraction):**
    *   **Recommendation:** A combination of **Requests** (for fetching page HTML) and **BeautifulSoup4** (for parsing the HTML). This stack is simple and effective for extracting data from single pages.
    *   **Alternative:** For more complex scenarios involving asynchronous crawling or following links, **Scrapy** is a powerful framework to consider.
*   **AI-Powered Data Extraction (NLP):**
    *   **Recommendation:** Use a pre-trained Named Entity Recognition (NER) model from a library like **spaCy** or **Hugging Face Transformers**. These models can be fine-tuned to recognize entities like `INGREDIENT`, `QUANTITY`, `UNIT`, and `INSTRUCTION` from raw recipe text, which is more robust than using simple regular expressions.
