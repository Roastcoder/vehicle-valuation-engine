import mysql.connector
from datetime import datetime
import json
import os
from urllib.parse import urlparse

class ValuationDB:
    def __init__(self, db_url=None):
        # Parse MySQL URL or use SQLite fallback
        self.db_url = db_url or os.getenv('DATABASE_URL')
        
        if self.db_url and self.db_url.startswith('mysql://'):
            self.use_mysql = True
            parsed = urlparse(self.db_url)
            self.db_config = {
                'host': parsed.hostname,
                'port': parsed.port or 3306,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path.lstrip('/')
            }
        else:
            self.use_mysql = False
            self.db_path = 'valuations.db'
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        
        self.init_db()
    
    def init_db(self):
        """Initialize database with tables"""
        if self.use_mysql:
            try:
                conn = mysql.connector.connect(**self.db_config)
                cursor = conn.cursor()
                
                # Valuations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS valuations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        rc_number VARCHAR(20) NOT NULL,
                        vehicle_make VARCHAR(100),
                        vehicle_model VARCHAR(100),
                        manufacturing_year VARCHAR(10),
                        vehicle_age VARCHAR(50),
                        fuel_type VARCHAR(20),
                        owner_count INT,
                        city VARCHAR(100),
                        fair_market_retail_value DECIMAL(12,2),
                        dealer_purchase_price DECIMAL(12,2),
                        current_ex_showroom DECIMAL(12,2),
                        estimated_odometer INT,
                        base_depreciation_percent DECIMAL(5,2),
                        book_value DECIMAL(12,2),
                        market_listings_mean DECIMAL(12,2),
                        confidence_score DECIMAL(5,2),
                        ai_model VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        raw_response TEXT,
                        INDEX idx_rc_number (rc_number),
                        INDEX idx_created_at (created_at)
                    )
                ''')
                
                # RC Details table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS rc_details (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        rc_number VARCHAR(20) UNIQUE NOT NULL,
                        owner_name VARCHAR(200),
                        maker_description VARCHAR(200),
                        maker_model VARCHAR(100),
                        registration_date VARCHAR(20),
                        manufacturing_date VARCHAR(20),
                        fuel_type VARCHAR(20),
                        color VARCHAR(50),
                        body_type VARCHAR(50),
                        cubic_capacity VARCHAR(20),
                        norms_type VARCHAR(20),
                        registered_at VARCHAR(200),
                        vehicle_category VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        raw_data TEXT
                    )
                ''')
            except Exception as e:
                print(f"MySQL connection failed: {e}. Falling back to SQLite.")
                self.use_mysql = False
        
        if not self.use_mysql:
            import sqlite3
            self.db_path = 'valuations.db'
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Valuations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS valuations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rc_number TEXT NOT NULL,
                    vehicle_make TEXT,
                    vehicle_model TEXT,
                    vehicle_variant TEXT,
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
        if self.use_mysql:
            conn = mysql.connector.connect(**self.db_config)
        else:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
        
        cursor = conn.cursor()
        
        # Save RC details
        raw_data = rc_details.get('raw_data', {})
        
        if self.use_mysql:
            cursor.execute('''
                INSERT INTO rc_details 
                (rc_number, owner_name, maker_description, maker_model, registration_date,
                 manufacturing_date, fuel_type, color, body_type, cubic_capacity, norms_type,
                 registered_at, vehicle_category, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                owner_name=VALUES(owner_name), maker_description=VALUES(maker_description),
                maker_model=VALUES(maker_model), registration_date=VALUES(registration_date),
                manufacturing_date=VALUES(manufacturing_date), fuel_type=VALUES(fuel_type),
                color=VALUES(color), body_type=VALUES(body_type), cubic_capacity=VALUES(cubic_capacity),
                norms_type=VALUES(norms_type), registered_at=VALUES(registered_at),
                vehicle_category=VALUES(vehicle_category), raw_data=VALUES(raw_data)
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        else:
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
                (rc_number, vehicle_make, vehicle_model, vehicle_variant, manufacturing_year, vehicle_age,
                 fuel_type, owner_count, city, fair_market_retail_value, dealer_purchase_price,
                 current_ex_showroom, estimated_odometer, base_depreciation_percent, book_value,
                 market_listings_mean, confidence_score, ai_model, raw_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rc_number,
                idv_calculation.get('vehicle_make'),
                idv_calculation.get('vehicle_model'),
                idv_calculation.get('variant'),
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
        if self.use_mysql:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
        else:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        if self.use_mysql:
            cursor.execute('''
                SELECT * FROM valuations 
                WHERE rc_number = %s 
                ORDER BY created_at DESC
            ''', (rc_number,))
        else:
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
        if self.use_mysql:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
        else:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        if self.use_mysql:
            cursor.execute('''
                SELECT * FROM valuations 
                ORDER BY created_at DESC 
                LIMIT %s
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT * FROM valuations 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_rc_details(self, rc_number):
        """Get RC details for a specific RC number"""
        if self.use_mysql:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
        else:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        if self.use_mysql:
            cursor.execute('''
                SELECT * FROM rc_details 
                WHERE rc_number = %s
            ''', (rc_number,))
        else:
            cursor.execute('''
                SELECT * FROM rc_details 
                WHERE rc_number = ?
            ''', (rc_number,))
        
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def get_similar_vehicles(self, state, manufacturing_year, fuel_type, vehicle_model, limit=5):
        """Get similar vehicles based on state, year, fuel type, and model"""
        if self.use_mysql:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
        else:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        if self.use_mysql:
            cursor.execute('''
                SELECT v.rc_number, v.vehicle_model, v.manufacturing_year, 
                       v.fuel_type, v.fair_market_retail_value, v.dealer_purchase_price,
                       r.registered_at
                FROM valuations v
                LEFT JOIN rc_details r ON v.rc_number = r.rc_number
                WHERE v.manufacturing_year = %s 
                  AND v.fuel_type = %s
                  AND v.vehicle_model = %s
                  AND r.registered_at LIKE %s
                ORDER BY v.created_at DESC
                LIMIT %s
            ''', (manufacturing_year, fuel_type, vehicle_model, f'%{state}%', limit))
        else:
            cursor.execute('''
                SELECT v.rc_number, v.vehicle_model, v.manufacturing_year, 
                       v.fuel_type, v.fair_market_retail_value, v.dealer_purchase_price,
                       r.registered_at
                FROM valuations v
                LEFT JOIN rc_details r ON v.rc_number = r.rc_number
                WHERE v.manufacturing_year = ? 
                  AND v.fuel_type = ?
                  AND v.vehicle_model = ?
                  AND r.registered_at LIKE ?
                ORDER BY v.created_at DESC
                LIMIT ?
            ''', (manufacturing_year, fuel_type, vehicle_model, f'%{state}%', limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
