# How to Setup Galaxy Profile for Another User

If you want to implement this animated galaxy profile for another GitHub account, follow these steps:

### 1. Create the Repository
1.  Log in to the new GitHub account.
2.  Create a new repository named exactly the same as the username (e.g., if the username is `johndoe`, the repo name should be `johndoe`).
3.  Choose **Public** and initialize with a README (optional).

### 2. Copy the Files
1.  Clone this repository to your computer.
2.  Copy all files from this project into the new repository's folder.
3.  **Crucial Files to include**:
    *   `.github/workflows/generate-profile.yml`
    *   `generator/` (entire folder)
    *   `config.yml`
    *   `README.md`
    *   `requirements.txt`

### 3. Configure the New Profile
1.  Open `config.yml` in the new repository.
2.  Change the `username` field to the new GitHub username.
3.  Update the `profile` and `social` sections with the new user's details.

### 4. Enable GitHub Actions Permissions
By default, GitHub Actions might not have permission to commit back to the repo.
1.  Go to the **Settings** tab of the new repository on GitHub.
2.  On the left sidebar, click **Actions** > **General**.
3.  Scroll down to **Workflow permissions**.
4.  Select **Read and write permissions**.
5.  Click **Save**.

### 5. Update README.md
Ensure the `README.md` in the new repo has the correct image links. They should point to `./assets/generated/` which is where the action will save the SVGs.

### 6. Trigger the First Run
1.  Push all your changes to the new repo:
    ```bash
    git add .
    git commit -m "initial: setup galaxy profile"
    git push origin main
    ```
2.  Go to the **Actions** tab in the new GitHub repository.
3.  Click on **Generate Profile SVGs**.
4.  Click **Run workflow** > **Run workflow**.

### 7. Troubleshooting
*   **Permissions**: If you see "Permission denied" in the Action logs, double-check Step 4.
*   **Token**: The workflow uses `${{ secrets.GITHUB_TOKEN }}` which is built-in. You don't need to manually create a secret unless you want to track private contributions (in which case, create a PAT and add it as a secret).
