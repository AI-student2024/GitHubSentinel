import json

class SubscriptionManager:
    def __init__(self, subscriptions_file):
        self.subscriptions_file = subscriptions_file
        self.subscriptions = self.load_subscriptions()
    
    def load_subscriptions(self):
        with open(f'../{self.subscriptions_file}', 'r') as f: # subcriptions.json位于脚本文件的上级目录中
            return json.load(f)
    
    def save_subscriptions(self):
        with open(f'../{self.subscriptions_file}', 'w') as f: # subcriptions.json位于脚本文件的上级目录中
            json.dump(self.subscriptions, f, indent=4)
    
    def list_subscriptions(self):
        return self.subscriptions
    
    def add_subscription(self, repo):
        if repo not in self.subscriptions:
            self.subscriptions.append(repo)
            self.save_subscriptions()
    
    def remove_subscription(self, repo):
        if repo in self.subscriptions:
            self.subscriptions.remove(repo)
            self.save_subscriptions()