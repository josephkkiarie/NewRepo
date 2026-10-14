class EventAnalyzer:
    def get_joiners_multiple_meetings_method(self, events: list[dict]) -> list[dict]:
        joiners: dict[str, dict] = {}

        for event in events:
            seen_in_event: set[str] = set()
            for joiner in event.get("joiners") or []:
                email = joiner["email"].strip().lower()
                if email in seen_in_event:
                    continue
                seen_in_event.add(email)

                if email not in joiners:
                    joiners[email] = {
                        "full_name": joiner["name"],
                        "email": joiner["email"],
                        "meetings_attended": 0,
                    }
                joiners[email]["meetings_attended"] += 1

        return [joiner for joiner in joiners.values() if joiner["meetings_attended"] >= 2]
