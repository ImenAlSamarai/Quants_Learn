"""
Simple API Cost Tracker for Testing/Demo
Monitors OpenAI and Anthropic API usage to prevent cost explosions
"""
from datetime import datetime
import json
import os

COST_LOG_FILE = "api_costs.json"

# Estimated costs (approximate)
COSTS = {
    "gpt-4o-mini": {
        "input": 0.15 / 1_000_000,   # $0.15 per 1M input tokens
        "output": 0.60 / 1_000_000   # $0.60 per 1M output tokens
    },
    "gpt-4-turbo-preview": {
        "input": 10.00 / 1_000_000,  # $10 per 1M input tokens
        "output": 30.00 / 1_000_000  # $30 per 1M output tokens
    },
    "gpt-4": {
        "input": 30.00 / 1_000_000,  # $30 per 1M input tokens
        "output": 60.00 / 1_000_000  # $60 per 1M output tokens
    },
    "claude-3-5-sonnet": {
        "input": 3.00 / 1_000_000,   # $3 per 1M input tokens
        "output": 15.00 / 1_000_000  # $15 per 1M output tokens
    }
}


class CostTracker:
    def __init__(self):
        self.log_file = COST_LOG_FILE
        self.daily_budget = float(os.getenv("DAILY_API_BUDGET", "10.0"))  # $10 default

    def log_api_call(self, model: str, input_tokens: int, output_tokens: int, operation: str):
        """Log an API call and calculate cost"""
        if model not in COSTS:
            print(f"⚠️  Unknown model: {model}")
            return

        input_cost = input_tokens * COSTS[model]["input"]
        output_cost = output_tokens * COSTS[model]["output"]
        total_cost = input_cost + output_cost

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "operation": operation,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(total_cost, 4)
        }

        # Append to log file
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(entry)

            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)

            print(f"💰 API Cost: ${total_cost:.4f} ({model} - {operation})")

            # Check if approaching daily budget
            daily_total = self.get_daily_total()
            if daily_total > self.daily_budget * 0.8:
                print(f"⚠️  WARNING: Daily API costs at ${daily_total:.2f} (Budget: ${self.daily_budget})")

        except Exception as e:
            print(f"Error logging cost: {e}")

    def get_daily_total(self) -> float:
        """Get total cost for today"""
        if not os.path.exists(self.log_file):
            return 0.0

        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)

            today = datetime.utcnow().date()
            daily_costs = [
                entry['cost_usd']
                for entry in logs
                if datetime.fromisoformat(entry['timestamp']).date() == today
            ]

            return sum(daily_costs)
        except Exception as e:
            print(f"Error calculating daily total: {e}")
            return 0.0

    def get_stats(self) -> dict:
        """Get usage statistics"""
        if not os.path.exists(self.log_file):
            return {
                "total_calls": 0,
                "total_cost": 0.0,
                "daily_cost": 0.0,
                "by_model": {},
                "by_operation": {}
            }

        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)

            today = datetime.utcnow().date()
            daily_logs = [
                entry for entry in logs
                if datetime.fromisoformat(entry['timestamp']).date() == today
            ]

            # Aggregate by model
            by_model = {}
            for entry in daily_logs:
                model = entry['model']
                if model not in by_model:
                    by_model[model] = {"calls": 0, "cost": 0.0}
                by_model[model]["calls"] += 1
                by_model[model]["cost"] += entry['cost_usd']

            # Aggregate by operation
            by_operation = {}
            for entry in daily_logs:
                op = entry['operation']
                if op not in by_operation:
                    by_operation[op] = {"calls": 0, "cost": 0.0}
                by_operation[op]["calls"] += 1
                by_operation[op]["cost"] += entry['cost_usd']

            return {
                "total_calls": len(logs),
                "total_cost": sum(e['cost_usd'] for e in logs),
                "daily_cost": sum(e['cost_usd'] for e in daily_logs),
                "daily_calls": len(daily_logs),
                "daily_budget": self.daily_budget,
                "budget_remaining": self.daily_budget - sum(e['cost_usd'] for e in daily_logs),
                "by_model": by_model,
                "by_operation": by_operation
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}


# Global instance
cost_tracker = CostTracker()
