# GitHub setup for RealityCheck

The private repo owner is Akshat3004 and the intended name is `RealityCheck`.

## 1. Create the remote repository

Open https://github.com/new, choose Akshat3004 as owner, name `RealityCheck`, set visibility to **Private**, and leave README, .gitignore and license uninitialized. Click **Create repository**.

## 2. Upload the prepared project using Terminal on macOS

Download and unzip `RealityCheck_GitHub_Starter.zip` (from the chat that created it). Then:

```bash
cd ~/Downloads/RealityCheck
git init -b main
git add .
git commit -m 'Initialize RealityCheck research project'
git remote add origin https://github.com/Akshat3004/RealityCheck.git
git push -u origin main
```

If `git` reports your name/email are missing, configure them first with `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"` (use your actual GitHub-associated email, not the placeholder). GitHub may ask you to sign in using your browser or credential manager; never send passwords or access tokens in chat.

## 3. Invite collaborators

Open repository **Settings > Collaborators** (sometimes **Collaborators and teams**), invite Jane and Arjun using their GitHub usernames, and have them accept the invitations. Keep visibility private unless your group chooses otherwise.

## 4. Each collaborator clones and branches

```bash
git clone https://github.com/Akshat3004/RealityCheck.git
cd RealityCheck
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[llm]'
python -m unittest discover -s tests -v
```

Use `git switch -c feat/dataset-pilot` or another task-specific branch. Push the branch and open a pull request to main. Pull the latest main branch before starting a new task.

## 5. EOD milestone focus

- Create the independently annotated pilot set and save evidence provenance, with adjudication notes.
- Run B1 on that pilot and record model, prompt version and outputs.
- Implement pairwise applicability judgments for S1 and compare against B1.
- Add S2 provenance-aware aggregation if time remains.
- Write the milestone report using only measured results; list unfinished work explicitly.

Do not commit API keys or report synthetic smoke tests as benchmark accuracy.
