import pandas as pd

class InvestigationTracker:
    def __init__(self):
        self.investigations = {}

    def get_investigations(self, events):
        # Return DataFrame with status/notes for each event
        records = []
        for _, row in events.iterrows():
            eid = row['Event_ID']
            status = self.investigations.get(eid, {}).get('status', 'Not reviewed')
            notes = self.investigations.get(eid, {}).get('notes', '')
            records.append({**row, 'Status': status, 'Notes': notes})
        return pd.DataFrame(records)

    def add_note(self, event_id, note):
        if event_id not in self.investigations:
            self.investigations[event_id] = {}
        self.investigations[event_id]['notes'] = note

    def get_notes(self, event_id):
        return self.investigations.get(event_id, {}).get('notes', '')

    def set_status(self, event_id, status):
        if event_id not in self.investigations:
            self.investigations[event_id] = {}
        self.investigations[event_id]['status'] = status
