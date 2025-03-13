import random
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class ChessTeamPairing:
    def __init__(self, members, file_path='pairs2.json'):
        self.members = members
        self.file_path = file_path
        self.past_pairs = self.load_pairs()

    def load_pairs(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return set(tuple(pair) for pair in json.load(file))
        return set()

    def save_pairs(self):
        with open(self.file_path, 'w') as file:
            json.dump(list(self.past_pairs), file)

    def generate_pairs(self):
        if len(self.members) % 2 != 0:
            self.members.append("PASS")
        
        while True:
            random.shuffle(self.members)
            pairs = [(self.members[i], self.members[i+1]) for i in range(0, len(self.members), 2)]
            
            if all((min(pair), max(pair)) not in self.past_pairs for pair in pairs):
                for pair in pairs:
                    self.past_pairs.add((min(pair), max(pair)))
                self.save_pairs()
                return pairs

    def read_members_from_google_sheet(self, sheet_url, sheet_name):
        #google Sheets API connection
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials2.json', scope)
        client = gspread.authorize(creds)
        
        #open spreadsheet 
        sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
        
        #get all the names from the first column
        self.members = sheet.col_values(1)  

    def write_pairs_to_google_sheet(self, sheet_url, sheet_name, pairs):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials2.json', scope)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
        sheet.clear()
        
        data_to_write = [[pair[0], pair[1]] for pair in pairs]
        sheet.update('A1', data_to_write)



#example usage
members = ["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Joe"]
chess_pairings = ChessTeamPairing(members)

try:
    #read members from the Google sheet
    chess_pairings.read_members_from_google_sheet('https://docs.google.com/spreadsheets/blahblahlink', 'Sheet1')
    
    #generate new pairs
    new_pairs = chess_pairings.generate_pairs()
    
    #write new pairs to a different Google sheet
    chess_pairings.write_pairs_to_google_sheet(
        'https://docs.google.com/spreadsheets/blahblahlink', 
        'Sheet1', 
        new_pairs  #pass the generated pairs here
    )

    print("New pairs:", new_pairs)
except ValueError as e:
    print(e)

