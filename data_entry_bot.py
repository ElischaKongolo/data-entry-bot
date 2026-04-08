# Complete Data Entry Bot - Fixed Version for Jupyter Notebook
# Run this entire cell to launch the Data Entry Bot

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import re
import random
import time
import sys

# Check if running in Jupyter
try:
    from IPython import get_ipython
    in_jupyter = 'IPKernelApp' in get_ipython().config
except:
    in_jupyter = False

# Try to import tkinter (may fail in some Jupyter environments)
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Warning: tkinter not available. Using command line interface only.")

# Try selenium for web automation (optional)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    WEB_AUTOMATION_AVAILABLE = True
except ImportError:
    WEB_AUTOMATION_AVAILABLE = False

# ==================== DATA ENTRY BOT CLASS ====================
class DataEntryBot:
    def __init__(self, data_file='data_entries.json'):
        self.data_file = data_file
        self.data = self.load_data()
        
    def load_data(self):
        """Load existing data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def export_to_csv(self, filename='data_export.csv'):
        """Export data to CSV"""
        if self.data:
            df = pd.DataFrame(self.data)
            df.to_csv(filename, index=False)
            return f"✓ Exported {len(self.data)} records to {filename}"
        return "✗ No data to export"
    
    def import_from_csv(self, filename):
        """Import data from CSV"""
        try:
            df = pd.read_csv(filename)
            records_before = len(self.data)
            self.data.extend(df.to_dict('records'))
            self.save_data()
            return f"✓ Imported {len(df)} new records (total: {len(self.data)})"
        except Exception as e:
            return f"✗ Error importing: {str(e)}"
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone):
        """Validate phone number"""
        if not phone:
            return True
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))
    
    def add_entry(self, entry_data):
        """Add a new data entry"""
        # Validate required fields
        if not entry_data.get('name'):
            return False, "✗ Name is required"
        if not entry_data.get('email'):
            return False, "✗ Email is required"
        
        # Validate email
        if not self.validate_email(entry_data['email']):
            return False, "✗ Invalid email format"
        
        # Validate phone if provided
        if entry_data.get('phone') and not self.validate_phone(entry_data['phone']):
            return False, "✗ Invalid phone format (9-15 digits)"
        
        # Add timestamp
        entry_data['timestamp'] = datetime.now().isoformat()
        
        self.data.append(entry_data)
        self.save_data()
        return True, f"✓ Added: {entry_data['name']}"
    
    def search_entries(self, keyword, field='name'):
        """Search entries by keyword"""
        if not keyword:
            return []
        results = []
        for entry in self.data:
            if field in entry and keyword.lower() in str(entry[field]).lower():
                results.append(entry)
        return results
    
    def get_statistics(self):
        """Get statistics about the data"""
        if not self.data:
            return {"Total Entries": 0}
        
        df = pd.DataFrame(self.data)
        stats = {
            'Total Entries': len(self.data),
            'Unique Names': df['name'].nunique() if 'name' in df else 0,
            'Unique Emails': df['email'].nunique() if 'email' in df else 0,
        }
        if 'timestamp' in df:
            stats['First Entry'] = df['timestamp'].min()[:10]
            stats['Last Entry'] = df['timestamp'].max()[:10]
        
        return stats
    
    def batch_import(self, data_list):
        """Import multiple entries at once"""
        success_count = 0
        for entry in data_list:
            success, _ = self.add_entry(entry)
            if success:
                success_count += 1
        return f"✓ Imported {success_count} out of {len(data_list)} entries"
    
    def get_all_entries(self, limit=50):
        """Get all entries (with limit)"""
        return self.data[-limit:] if self.data else []
    
    def delete_entry(self, index):
        """Delete an entry by index"""
        if 0 <= index < len(self.data):
            deleted = self.data.pop(index)
            self.save_data()
            return True, f"✓ Deleted: {deleted.get('name', 'Unknown')}"
        return False, "✗ Invalid index"

# ==================== DATA GENERATOR ====================
class DataGenerator:
    @staticmethod
    def generate_sample_data(num_records=10):
        """Generate sample data for testing"""
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'James', 'Lisa', 'Robert', 'Maria']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        departments = ['Sales', 'Marketing', 'IT', 'HR', 'Finance', 'Operations']
        
        sample_data = []
        for i in range(min(num_records, 100)):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            entry = {
                'name': f"{first_name} {last_name}",
                'email': f"{first_name.lower()}.{last_name.lower()}{random.randint(1,999)}@example.com",
                'phone': f"+1{random.randint(200,999)}{random.randint(200,999)}{random.randint(1000,9999)}",
                'age': str(random.randint(22, 65)),
                'department': random.choice(departments)
            }
            sample_data.append(entry)
        
        return sample_data

# ==================== COMMAND LINE INTERFACE ====================
class DataEntryCLI:
    def __init__(self, bot):
        self.bot = bot
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def run(self):
        """Run command line interface"""
        while True:
            self.print_header("🤖 DATA ENTRY BOT - Main Menu")
            print("\n📋 Current Records:", len(self.bot.data))
            print("\nOptions:")
            print("  1. ➕ Add New Entry")
            print("  2. 📋 View All Entries")
            print("  3. 🔍 Search Entries")
            print("  4. 📊 Export to CSV")
            print("  5. 📁 Import from CSV")
            print("  6. 📈 Show Statistics")
            print("  7. 🎲 Generate Sample Data")
            print("  8. 🗑️  Delete Entry")
            print("  9. 🚪 Exit")
            
            choice = input("\n👉 Enter choice (1-9): ").strip()
            
            if choice == '1':
                self.add_entry()
            elif choice == '2':
                self.view_entries()
            elif choice == '3':
                self.search_entries()
            elif choice == '4':
                self.export_data()
            elif choice == '5':
                self.import_data()
            elif choice == '6':
                self.show_stats()
            elif choice == '7':
                self.generate_sample()
            elif choice == '8':
                self.delete_entry()
            elif choice == '9':
                print("\n👋 Goodbye! Thanks for using Data Entry Bot!\n")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    
    def add_entry(self):
        """Add a new entry"""
        self.print_header("➕ ADD NEW ENTRY")
        print("(Press Enter to skip optional fields)\n")
        
        name = input("Name (required): ").strip()
        if not name:
            print("❌ Name is required!")
            return
        
        email = input("Email (required): ").strip()
        if not email:
            print("❌ Email is required!")
            return
        
        phone = input("Phone (optional): ").strip()
        age = input("Age (optional): ").strip()
        department = input("Department (optional): ").strip()
        
        entry = {
            'name': name,
            'email': email,
            'phone': phone,
            'age': age,
            'department': department
        }
        
        success, message = self.bot.add_entry(entry)
        print(f"\n{message}")
    
    def view_entries(self):
        """View all entries"""
        entries = self.bot.get_all_entries(30)
        
        if not entries:
            print("\n📭 No entries found")
            return
        
        self.print_header(f"📋 RECORDS (Showing last {len(entries)} of {len(self.bot.data)})")
        
        for i, entry in enumerate(reversed(entries), 1):
            print(f"\n{'─'*50}")
            print(f"#{i}")
            print(f"  👤 Name: {entry.get('name', 'N/A')}")
            print(f"  📧 Email: {entry.get('email', 'N/A')}")
            print(f"  📞 Phone: {entry.get('phone', 'N/A')}")
            print(f"  🎂 Age: {entry.get('age', 'N/A')}")
            print(f"  🏢 Dept: {entry.get('department', 'N/A')}")
            if 'timestamp' in entry:
                print(f"  🕐 Date: {entry['timestamp'][:10]}")
    
    def search_entries(self):
        """Search entries"""
        self.print_header("🔍 SEARCH RECORDS")
        
        keyword = input("Enter search keyword: ").strip()
        if not keyword:
            print("❌ Please enter a search keyword")
            return
        
        print("\nSearch by:")
        print("  1. Name")
        print("  2. Email")
        print("  3. Department")
        
        field_choice = input("Choose (1-3): ").strip()
        field_map = {'1': 'name', '2': 'email', '3': 'department'}
        field = field_map.get(field_choice, 'name')
        
        results = self.bot.search_entries(keyword, field)
        
        if results:
            print(f"\n✅ Found {len(results)} result(s):")
            for i, result in enumerate(results[:10], 1):
                print(f"\n  {i}. {result.get('name', 'N/A')}")
                print(f"     📧 {result.get('email', 'N/A')}")
                print(f"     🏢 {result.get('department', 'N/A')}")
        else:
            print("\n❌ No matching records found")
    
    def export_data(self):
        """Export data to CSV"""
        self.print_header("📊 EXPORT DATA")
        filename = input("Filename (default: export.csv): ").strip() or "export.csv"
        if not filename.endswith('.csv'):
            filename += '.csv'
        result = self.bot.export_to_csv(filename)
        print(f"\n{result}")
    
    def import_data(self):
        """Import data from CSV"""
        self.print_header("📁 IMPORT DATA")
        filename = input("CSV filename: ").strip()
        if filename:
            result = self.bot.import_from_csv(filename)
            print(f"\n{result}")
    
    def show_stats(self):
        """Show statistics"""
        self.print_header("📈 DATABASE STATISTICS")
        stats = self.bot.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    def generate_sample(self):
        """Generate sample data"""
        self.print_header("🎲 GENERATE SAMPLE DATA")
        try:
            num = input("Number of records (default: 5): ").strip()
            num = int(num) if num else 5
            num = min(num, 50)  # Limit to 50
            sample_data = DataGenerator.generate_sample_data(num)
            result = self.bot.batch_import(sample_data)
            print(f"\n{result}")
        except ValueError:
            print("\n❌ Invalid number")
    
    def delete_entry(self):
        """Delete an entry"""
        if not self.bot.data:
            print("\n📭 No entries to delete")
            return
        
        self.view_entries()
        try:
            index = int(input("\nEnter entry number to delete: ")) - 1
            index = len(self.bot.data) - 1 - index  # Convert from displayed order
            
            if 0 <= index < len(self.bot.data):
                confirm = input(f"Delete '{self.bot.data[index].get('name')}'? (y/n): ").lower()
                if confirm == 'y':
                    success, message = self.bot.delete_entry(index)
                    print(f"\n{message}")
            else:
                print("\n❌ Invalid entry number")
        except ValueError:
            print("\n❌ Invalid input")

# ==================== SIMPLE TEXT MENU (Works everywhere) ====================
def run_text_menu():
    """Simple text-based menu that works in any environment"""
    bot = DataEntryBot()
    cli = DataEntryCLI(bot)
    cli.run()

# ==================== MAIN ====================
def main():
    """Main function to launch the bot"""
    print("\n" + "="*60)
    print("🤖 WELCOME TO DATA ENTRY BOT 🤖")
    print("="*60)
    
    # Always use command line interface for Jupyter compatibility
    print("\n📌 Running in text mode (best for Jupyter Notebook)")
    print("💡 Tip: All data is saved to 'data_entries.json'")
    
    run_text_menu()

# ==================== RUN ====================
if __name__ == "__main__":
    main()
