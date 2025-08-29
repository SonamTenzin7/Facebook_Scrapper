"""
Smart Notification System
Sends notifications when new posts are detected or when scraper runs
"""

import smtplib
import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationSystem:
    def __init__(self):
        config = self.load_notification_config()
        if not isinstance(config, dict):
            print("⚠️ Notification config is not a dict, using default config.")
            config = {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "",
                    "sender_password": "",
                    "recipient_email": "",
                    "app_password": ""
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "discord_webhook": "",
                    "slack_webhook": ""
                }
            }
        self.config = config
    
    def load_notification_config(self):
        """Load notification configuration"""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "recipient_email": "",
                "app_password": ""
            },
            "webhook": {
                "enabled": False,
                "url": "",
                "discord_webhook": "",
                "slack_webhook": ""
            }
        }
        config_file = "notification_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                if isinstance(config, dict):
                    return {**default_config, **config}
                else:
                    print("⚠️ notification_config.json is not a dict, using default config.")
            except Exception as e:
                print(f"⚠️  Failed to load notification config: {e}")
        # Create default config file if missing or invalid
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"📝 Created default notification config: {config_file}")
            print("💡 Edit the config file to enable notifications")
        except Exception as e:
            print(f"⚠️ Could not create default notification config: {e}")
        return default_config
    
    def send_email_notification(self, subject, message):
        """Send email notification"""
        email_cfg = self.config.get("email", {})
        if not email_cfg.get("enabled", False):
            return False
        try:
            msg = MIMEMultipart()
            msg['From'] = email_cfg.get("sender_email", "")
            msg['To'] = email_cfg.get("recipient_email", "")
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            server = smtplib.SMTP(
                email_cfg.get("smtp_server", "smtp.gmail.com"),
                email_cfg.get("smtp_port", 587)
            )
            server.starttls()
            password = (email_cfg.get("app_password") or email_cfg.get("sender_password"))
            server.login(email_cfg.get("sender_email", ""), password)
            text = msg.as_string()
            server.sendmail(
                email_cfg.get("sender_email", ""),
                email_cfg.get("recipient_email", ""),
                text
            )
            server.quit()
            print("✅ Email notification sent successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_webhook_notification(self, message):
        """Send webhook notification (Discord/Slack)"""
        webhook_cfg = self.config.get("webhook", {})
        if not webhook_cfg.get("enabled", False):
            return False
        import requests
        webhooks = [
            webhook_cfg.get("discord_webhook", ""),
            webhook_cfg.get("slack_webhook", ""),
            webhook_cfg.get("url", "")
        ]
        for webhook_url in webhooks:
            if not webhook_url:
                continue
            try:
                payload = {"content": message} if "discord" in webhook_url else {"text": message}
                response = requests.post(webhook_url, json=payload, timeout=10)
                if response.status_code == 200:
                    print("✅ Webhook notification sent successfully")
                    return True
            except Exception as e:
                print(f"❌ Failed to send webhook: {e}")
        return False
    
    def send_desktop_notification(self, title, message):
        """Send desktop notification (macOS)"""
        try:
            os.system(f"""
                osascript -e 'display notification "{message}" with title "{title}"'
            """)
            print("✅ Desktop notification sent")
            return True
        except Exception as e:
            print(f"❌ Failed to send desktop notification: {e}")
            return False
    
    def notify_new_posts_detected(self, post_count=0):
        """Notify when new posts are detected"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if post_count > 0:
            subject = f"🆕 Kuensel: {post_count} New Post(s) Found"
            message = f"""
New Kuensel posts detected at {timestamp}

📊 New posts found: {post_count}
🤖 Scraper has been automatically triggered
📱 Check your API endpoints for updated content

---
Kuensel Facebook Scraper
            """
        else:
            subject = "🔍 Kuensel: New Activity Detected"
            message = f"""
Potential new content detected at {timestamp}

🔄 Scraper has been triggered to check for updates
📱 This could be new posts, comments, or page updates

---
Kuensel Facebook Scraper
            """
        
        # Send notifications via all enabled methods
        self.send_email_notification(subject, message)
        self.send_webhook_notification(f"**{subject}**\n{message}")
        self.send_desktop_notification(subject, f"{post_count} new posts detected" if post_count > 0 else "New activity detected")
    
    def notify_scraper_completed(self, success=True, posts_found=0, errors=None):
        """Notify when scraper completes"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if success:
            subject = f"✅ Kuensel: Scraper Completed Successfully"
            message = f"""
Scraping completed successfully at {timestamp}

📊 Total posts in database: {posts_found}
🔄 Static API files updated
📱 All endpoints are now current

---
Kuensel Facebook Scraper
            """
        else:
            subject = "❌ Kuensel: Scraper Failed"
            message = f"""
Scraping failed at {timestamp}

❌ Errors encountered: {errors or 'Unknown error'}
🔧 Manual intervention may be required

---
Kuensel Facebook Scraper
            """
        
        # Send notifications
        self.send_email_notification(subject, message)
        self.send_webhook_notification(f"**{subject}**\n{message}")
        self.send_desktop_notification(subject, "Scraping completed" if success else "Scraping failed")
    
    def test_notifications(self):
        """Test all notification methods"""
        print("🧪 Testing notification systems...")
        
        subject = "🧪 Kuensel Scraper: Test Notification"
        message = f"Test notification sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        email_success = self.send_email_notification(subject, message)
        webhook_success = self.send_webhook_notification(f"**{subject}**\n{message}")
        desktop_success = self.send_desktop_notification(subject, "Test notification")
        
        print(f"\n📧 Email: {'✅' if email_success else '❌'}")
        print(f"🔗 Webhook: {'✅' if webhook_success else '❌'}")
        print(f"🖥️  Desktop: {'✅' if desktop_success else '❌'}")

def test_notifications():
    """Test the notification system"""
    notifier = NotificationSystem()
    notifier.test_notifications()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_notifications()
    else:
        # Example usage
        notifier = NotificationSystem()
        notifier.notify_new_posts_detected(post_count=2)
