import sqlite3
from datetime import datetime
import json

class ValuationDB:
    def __init__(self, db_path='valuations.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Valuations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS valuations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rc_number TEXT NOT NULL,
                vehicle_make TEXT,
                vehicle_model TEXT,
                manufacturing_year TEXT,
                vehicle_age TEXT,
                fuel_type TEXT,
                owner_count INTEGER,
                city TEXT,
                fair_market_retail_value REAL,
                dealer_purchase_price REAL,
                current_ex_showroom REAL,
                estimated_odometer INTEGER,
                base_depreciation_percent REAL,
                book_value REAL,
                market_listings_mean REAL,
                confidence_score REAL,
                ai_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_response TEXT
            )
        ''')
        
        # RC Details table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rc_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rc_number TEXT UNIQUE NOT NULL,
                owner_name TEXT,
                maker_description TEXT,
                maker_model TEXT,
                registration_date TEXT,
                manufacturing_date TEXT,
                fuel_type TEXT,
                color TEXT,
                body_type TEXT,
                cubic_capacity TEXT,
                norms_type TEXT,
                registered_at TEXT,
                vehicle_category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_data TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_valuation(self, rc_number, rc_details, idv_calculation):
        """Save complete valuation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save RC details
        raw_data = rc_details.get('raw_data', {})
        cursor.execute('''
            INSERT OR REPLACE INTO rc_details 
            (rc_number, owner_name, maker_description, maker_model, registration_date,
             manufacturing_date, fuel_type, color, body_type, cubic_capacity, norms_type,
             registered_at, vehicle_category, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rc_number,
            raw_data.get('owner_name'),
            raw_data.get('maker_description'),
            raw_data.get('maker_model'),
            raw_data.get('registration_date'),
            raw_data.get('manufacturing_date_formatted'),
            raw_data.get('fuel_type'),
            raw_data.get('color'),
            raw_data.get('body_type'),
            raw_data.get('cubic_capacity'),
            raw_data.get('norms_type'),
            raw_data.get('registered_at'),
            raw_data.get('vehicle_category_description'),
            json.dumps(raw_data)
        ))
        
        # Save valuation
        cursor.execute('''
            INSERT INTO valuations 
            (rc_number, vehicle_make, vehicle_model, manufacturing_year, vehicle_age,
             fuel_type, owner_count, city, fair_market_retail_value, dealer_purchase_price,
             current_ex_showroom, estimated_odometer, base_depreciation_percent, book_value,
             market_listings_mean, confidence_score, ai_model, raw_response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rc_number,
            idv_calculation.get('vehicle_make'),
            idv_calculation.get('vehicle_model'),
            idv_calculation.get('manufacturing_year'),
            idv_calculation.get('vehicle_age'),
            raw_data.get('fuel_type'),
            idv_calculation.get('owner_count', 1),
            idv_calculation.get('city_used_for_price'),
            idv_calculation.get('fair_market_retail_value'),
            idv_calculation.get('dealer_purchase_price'),
            idv_calculation.get('current_ex_showroom'),
            idv_calculation.get('estimated_odometer'),
            idv_calculation.get('base_depreciation_percent'),
            idv_calculation.get('book_value'),
            idv_calculation.get('market_listings_mean'),
            idv_calculation.get('confidence_score'),
            idv_calculation.get('ai_model'),
            json.dumps(idv_calculation)
        ))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_valuation_history(self, rc_number):
        """Get all valuations for a specific RC number"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM valuations 
            WHERE rc_number = ? 
            ORDER BY created_at DESC
        ''', (rc_number,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_recent_valuations(self, limit=10):
        """Get recent valuations"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM valuations 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
