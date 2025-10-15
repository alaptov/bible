# CI/CD Setup for Paleo Hebrew Bible

## GitHub Actions Configuration

This repository now has automated deployment set up via GitHub Actions. Every push to the `main` branch will automatically deploy to your server.

## Required Setup

### 1. GitHub Secrets Configuration

You need to add these secrets to your GitHub repository:

1. Go to your repository on GitHub: https://github.com/alaptov/bible
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of these:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `HOST` | Your server's IP address or domain | `123.45.67.89` or `example.com` |
| `USERNAME` | SSH username for the server | `ubuntu` or your username |
| `SSH_PRIVATE_KEY` | Private SSH key for authentication | Contents of `~/.ssh/id_ed25519` |
| `PORT` | SSH port (optional, defaults to 22) | `22` |
| `PROJECT_PATH` | Path to project on server (optional) | `/var/www/paleo-hebrew-bible` |

### 2. SSH Key Setup

If you haven't already set up SSH keys for deployment:

```bash
# 1. Generate SSH key pair (if not already done)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_key

# 2. Copy the public key to your server
ssh-copy-id -i ~/.ssh/deploy_key.pub username@your-server-ip

# 3. Test SSH connection
ssh -i ~/.ssh/deploy_key username@your-server-ip

# 4. Copy the PRIVATE key content for GitHub secrets
cat ~/.ssh/deploy_key
# Copy the entire output and add as SSH_PRIVATE_KEY secret
```

### 3. Server Requirements

Your server needs:
- The project already deployed at `/var/www/paleo-hebrew-bible` (or your chosen path)
- Systemd service named `paleo-hebrew-bible` configured and running
- Python virtual environment at `venv/` in the project directory
- SSH access configured for the deployment user
- Sudo permissions for the deployment user to restart the service

Add this to your server's sudoers file (run `sudo visudo`):
```
your-username ALL=(ALL) NOPASSWD: /bin/systemctl restart paleo-hebrew-bible
your-username ALL=(ALL) NOPASSWD: /bin/systemctl status paleo-hebrew-bible
```

## How It Works

1. **Trigger**: Push to `main` branch or manual workflow dispatch
2. **Checkout**: GitHub Actions checks out your code
3. **Deploy**: Connects to your server via SSH and:
   - Pulls latest changes from git
   - Activates Python virtual environment
   - Installs/updates dependencies
   - Runs database checks
   - Restarts the systemd service
   - Performs health check
4. **Notify**: Reports success or failure

## Testing the Deployment

After setting up secrets, push a small change to test:

```bash
git add .
git commit -m "test: trigger CI/CD deployment"
git push origin main
```

Then check:
1. GitHub Actions tab in your repository to see the workflow running
2. Your server logs: `sudo journalctl -u paleo-hebrew-bible -f`
3. Your website to verify the changes are live

## Manual Deployment

You can also trigger deployment manually:
1. Go to **Actions** tab in GitHub
2. Select **Deploy to Server** workflow
3. Click **Run workflow** → **Run workflow**

## Troubleshooting

### Workflow fails with "Permission denied"
- Check that SSH_PRIVATE_KEY is correct
- Verify the public key is added to server's `~/.ssh/authorized_keys`
- Test SSH connection manually

### Workflow fails at "systemctl restart"
- Check sudoers configuration on server
- Verify service name is correct
- Test restart manually: `sudo systemctl restart paleo-hebrew-bible`

### Health check fails
- Check if service is actually running: `sudo systemctl status paleo-hebrew-bible`
- Check application logs: `sudo journalctl -u paleo-hebrew-bible -n 50`
- Verify nginx is running and configured correctly

## Security Notes

- Never commit SSH private keys to the repository
- Use GitHub secrets for all sensitive information
- Rotate SSH keys periodically
- Use different keys for deployment vs personal access
- Limit sudo permissions to only necessary commands
