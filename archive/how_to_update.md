# How to Update Your Galaxy Profile

This guide explains how to update your `config.yml` and `README.md` files to change your profile information or featured projects.

## Method 1: Using the GitHub Web Interface

This is the easiest way to make quick changes without using any terminal commands.

1.  **Navigate to your repository** on GitHub.
2.  **Edit `config.yml`**:
    *   Click on `config.yml`.
    *   Click the **Pencil icon** (Edit this file) at the top right.
    *   Modify your name, tagline, tech stack, or projects.
    *   Click **Commit changes...** at the top right.
    *   Enter a commit message (e.g., `update: change tagline`) and click **Commit changes**.
3.  **Edit `README.md`**:
    *   Navigate back to the main page of your repo.
    *   Click on `README.md`.
    *   Click the **Pencil icon**.
    *   Update the "More about me" section or social links.
    *   Click **Commit changes...** and save your changes.

> [!NOTE]
> Once you commit changes to `config.yml`, the GitHub Action will automatically run and update your SVGs within a few minutes!

---

## Method 2: Using VS Code (Local Clone)

Use this method if you prefer working on your computer.

### 1. Open the Project
Open your cloned `galaxy-profile` folder in VS Code.

### 2. Make Changes
*   Open `config.yml` and update your data.
*   Open `README.md` and update your text.

### 3. Commit and Push via Terminal
Open the integrated terminal in VS Code (Ctrl + `) and run these commands:

```bash
# 1. Stage the changes
git add config.yml README.md

# 2. Create a commit
git commit -m "update: profile information and projects"

# 3. Push to GitHub
git push origin main
```

---

## What happens next?
After you push or commit your changes, look at the **Actions** tab in your GitHub repository. You will see a workflow named **Generate Profile SVGs** starting automatically. Once it finishes (takes about 20-30 seconds), your profile README will show the new data and refreshed galaxy animations!
