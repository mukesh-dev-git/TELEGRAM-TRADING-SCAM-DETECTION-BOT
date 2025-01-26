import csv

file_path = r"C:\Users\USER\Desktop\TELE_BOT_UP_ENV\flagged_messages.csv"

with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Channel Name", "Message", "Risk Score", "Flags", "Explanations"]) 
print(f"Flagged messages file at '{file_path}' has been cleared.")
