"""
Ring Checker Pro - Implementasi Lengkap dalam Satu File
Aplikasi Analisis Teori Ring yang Canggih
Versi 2.0 - Edisi All-in-One
Dibuat untuk analisis struktur ring matematika dengan GUI modern
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import sqlite3
import threading
import time
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import sys
import traceback
import functools

# ============================================================================
# KONFIGURASI DAN KELAS DATA
# ============================================================================

@dataclass
class AppConfig:
    """Konfigurasi aplikasi"""
    window_width: int = 1400
    window_height: int = 900
    theme_name: str = "azure"
    theme_mode: str = "dark"
    max_table_size: int = 15
    validation_timeout: int = 30
    auto_save: bool = True
    logging_level: str = "INFO"
    database_path: str = "ring_checker.db"

class RingProperty(Enum):
    """Enumerasi properti ring"""
    ASSOCIATIVE_MULTIPLICATION = "associative_multiplication"
    COMMUTATIVE_MULTIPLICATION = "commutative_multiplication"
    DISTRIBUTIVE = "distributive"
    HAS_UNITY = "has_unity"
    HAS_ZERO_DIVISORS = "has_zero_divisors"
    HAS_INVERSES = "has_inverses"
    ABELIAN_ADDITION = "abelian_addition"

@dataclass
class RingAnalysisResult:
    """Kelas data untuk hasil analisis ring"""
    is_ring: bool
    properties: Dict[RingProperty, bool]
    details: Dict[str, Any]
    analysis_time: float
    error_messages: List[str]
    classification: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_ring': self.is_ring,
            'properties': {prop.value: value for prop, value in self.properties.items()},
            'details': self.details,
            'analysis_time': self.analysis_time,
            'error_messages': self.error_messages,
            'classification': self.classification
        }

# ============================================================================
# EXCEPTION CLASSES KHUSUS
# ============================================================================

class RingCheckerError(Exception):
    """Exception dasar untuk Ring Checker"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        self.timestamp = datetime.now()
        super().__init__(self.message)

class ValidationError(RingCheckerError):
    """Exception untuk error validasi"""
    pass

class CalculationError(RingCheckerError):
    """Exception untuk error kalkulasi"""
    pass

# ============================================================================
# ERROR HANDLER
# ============================================================================

class ErrorHandler:
    """Sistem penanganan error yang komprehensif"""
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("RingChecker")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def handle_validation_error(self, error: Exception, context: str = "") -> None:
        error_msg = f"Error Validasi di {context}: {str(error)}"
        self.logger.error(error_msg)
        user_msg = self._get_user_friendly_message(error, "validation")
        messagebox.showerror("Error Validasi", user_msg)
    
    def handle_calculation_error(self, error: Exception, context: str = "") -> None:
        error_msg = f"Error Kalkulasi di {context}: {str(error)}"
        self.logger.error(error_msg)
        user_msg = self._get_user_friendly_message(error, "calculation")
        messagebox.showerror("Error Kalkulasi", user_msg)
    
    def handle_critical_error(self, error: Exception, context: str = "") -> None:
        error_msg = f"Error Kritis di {context}: {str(error)}"
        self.logger.critical(error_msg)
        user_msg = f"Terjadi error kritis: {str(error)}\nSilakan periksa log aplikasi."
        messagebox.showerror("Error Kritis", user_msg)
    
    def _get_user_friendly_message(self, error: Exception, error_type: str) -> str:
        error_messages = {
            "validation": {
                "ValueError": "Silakan periksa nilai input Anda. Pastikan semua field berisi data yang valid.",
                "TypeError": "Tipe data tidak valid terdeteksi. Silakan periksa entri Anda.",
                "KeyError": "Informasi yang diperlukan hilang. Silakan lengkapi semua field.",
            },
            "calculation": {
                "ZeroDivisionError": "Pembagian dengan nol ditemukan dalam kalkulasi.",
                "OverflowError": "Nilai yang dihitung terlalu besar untuk diproses.",
                "ArithmeticError": "Terjadi error aritmatika selama kalkulasi.",
            }
        }
        
        error_name = type(error).__name__
        category_messages = error_messages.get(error_type, {})
        return category_messages.get(error_name, f"Terjadi error yang tidak terduga: {str(error)}")

# ============================================================================
# THEME MANAGER
# ============================================================================

class ModernThemeManager:
    """Sistem manajemen tema modern"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_theme = "azure"
        self.current_mode = "dark"
        self.style = ttk.Style()
        
        # Definisi warna tema
        self.theme_colors = {
            "azure": {
                "dark": {
                    "bg": "#1e1e1e", "fg": "#ffffff", "select_bg": "#007acc",
                    "select_fg": "#ffffff", "button_bg": "#0d7377", "button_fg": "#ffffff",
                    "entry_bg": "#2d2d2d", "entry_fg": "#ffffff", "frame_bg": "#2d2d2d",
                    "accent": "#007acc"
                },
                "light": {
                    "bg": "#ffffff", "fg": "#000000", "select_bg": "#cce7ff",
                    "select_fg": "#000000", "button_bg": "#e1f5fe", "button_fg": "#000000",
                    "entry_bg": "#f5f5f5", "entry_fg": "#000000", "frame_bg": "#f0f0f0",
                    "accent": "#1976d2"
                }
            },
            "forest": {
                "dark": {
                    "bg": "#313131", "fg": "#ffffff", "select_bg": "#217346",
                    "select_fg": "#ffffff", "button_bg": "#217346", "button_fg": "#ffffff",
                    "entry_bg": "#404040", "entry_fg": "#ffffff", "frame_bg": "#404040",
                    "accent": "#217346"
                },
                "light": {
                    "bg": "#ffffff", "fg": "#000000", "select_bg": "#c3e88d",
                    "select_fg": "#000000", "button_bg": "#c3e88d", "button_fg": "#000000",
                    "entry_bg": "#f5f5f5", "entry_fg": "#000000", "frame_bg": "#f0f0f0",
                    "accent": "#388e3c"
                }
            }
        }
    
    def apply_theme(self, theme_name: str = "azure", mode: str = "dark") -> bool:
        """Terapkan tema ke aplikasi"""
        try:
            self.current_theme = theme_name
            self.current_mode = mode
            
            if theme_name not in self.theme_colors:
                theme_name = "azure"  # fallback ke tema default
            
            colors = self.theme_colors[theme_name][mode]
            
            # Konfigurasi root window
            self.root.configure(bg=colors["bg"])
            
            # Konfigurasi style ttk
            self.style.theme_use('clam')
            
            # Style untuk tombol
            self.style.configure("Modern.TButton",
                               background=colors["button_bg"],
                               foreground=colors["button_fg"],
                               focuscolor="none",
                               borderwidth=1,
                               relief="flat",
                               padding=(10, 5))
            
            self.style.map("Modern.TButton",
                          background=[('active', colors["accent"]),
                                    ('pressed', colors["select_bg"])])
            
            # Style untuk entry
            self.style.configure("Modern.TEntry",
                               fieldbackground=colors["entry_bg"],
                               foreground=colors["entry_fg"],
                               bordercolor=colors["accent"],
                               focuscolor=colors["accent"])
            
            # Style untuk frame
            self.style.configure("Modern.TFrame",
                               background=colors["frame_bg"])
            
            # Style untuk label
            self.style.configure("Modern.TLabel",
                               background=colors["bg"],
                               foreground=colors["fg"])
            
            # Style untuk labelframe
            self.style.configure("Modern.TLabelframe",
                               background=colors["frame_bg"],
                               foreground=colors["fg"],
                               bordercolor=colors["accent"])
            
            # Style untuk treeview
            self.style.configure("Modern.Treeview",
                               background=colors["entry_bg"],
                               foreground=colors["entry_fg"],
                               fieldbackground=colors["entry_bg"])
            
            self.style.configure("Modern.Treeview.Heading",
                               background=colors["button_bg"],
                               foreground=colors["button_fg"])
            
            return True
        except Exception as e:
            print(f"Gagal menerapkan tema: {e}")
            return False
    
    def get_current_colors(self) -> Dict[str, str]:
        """Dapatkan warna tema saat ini"""
        return self.theme_colors[self.current_theme][self.current_mode]
    
    def toggle_mode(self) -> bool:
        """Toggle antara mode gelap dan terang"""
        new_mode = "light" if self.current_mode == "dark" else "dark"
        return self.apply_theme(self.current_theme, new_mode)

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Manajemen database sederhana untuk aplikasi single file"""
    
    def __init__(self, db_path: str = "ring_checker.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Inisialisasi database dengan tabel yang diperlukan"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ring_calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    addition_table TEXT NOT NULL,
                    multiplication_table TEXT NOT NULL,
                    results TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Inisialisasi database gagal: {e}")
    
    def save_calculation(self, data: Dict[str, Any]) -> Optional[int]:
        """Simpan kalkulasi ke database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ring_calculations 
                (name, size, addition_table, multiplication_table, results)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['name'],
                data['size'],
                json.dumps(data['addition_table']),
                json.dumps(data['multiplication_table']),
                json.dumps(data['results'])
            ))
            
            calc_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return calc_id
        except Exception as e:
            print(f"Gagal menyimpan kalkulasi: {e}")
            return None
    
    def load_calculation(self, calc_id: int) -> Optional[Dict[str, Any]]:
        """Muat kalkulasi dari database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, size, addition_table, multiplication_table, results, created_at
                FROM ring_calculations WHERE id = ?
            """, (calc_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': calc_id,
                    'name': result[0],
                    'size': result[1],
                    'addition_table': json.loads(result[2]),
                    'multiplication_table': json.loads(result[3]),
                    'results': json.loads(result[4]),
                    'created_at': result[5]
                }
            return None
        except Exception as e:
            print(f"Gagal memuat kalkulasi: {e}")
            return None
    
    def get_calculation_list(self) -> List[Dict[str, Any]]:
        """Dapatkan daftar semua kalkulasi yang tersimpan"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, size, created_at
                FROM ring_calculations
                ORDER BY created_at DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {'id': row[0], 'name': row[1], 'size': row[2], 'created_at': row[3]}
                for row in results
            ]
        except Exception as e:
            print(f"Gagal mendapatkan daftar kalkulasi: {e}")
            return []

# ============================================================================
# ENGINE TEORI RING CANGGIH
# ============================================================================

class AdvancedRingTheory:
    """Engine analisis teori ring yang canggih"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
    
    def analyze_ring(self, elements: List[str], 
                    addition_table: List[List[str]], 
                    multiplication_table: List[List[str]]) -> RingAnalysisResult:
        """Analisis ring yang komprehensif"""
        start_time = time.time()
        
        try:
            self._validate_input(elements, addition_table, multiplication_table)
            
            properties = {}
            details = {}
            error_messages = []
            
            # Periksa grup abelian untuk penjumlahan
            abelian_result = self._check_abelian_group(elements, addition_table)
            properties[RingProperty.ABELIAN_ADDITION] = abelian_result[0]
            details['abelian_addition'] = abelian_result[1]
            
            # Periksa asosiatifitas perkalian
            assoc_result = self._check_associativity(elements, multiplication_table)
            properties[RingProperty.ASSOCIATIVE_MULTIPLICATION] = assoc_result[0]
            details['associative_multiplication'] = assoc_result[1]
            
            # Periksa distributifitas
            dist_result = self._check_distributivity(elements, addition_table, multiplication_table)
            properties[RingProperty.DISTRIBUTIVE] = dist_result[0]
            details['distributive'] = dist_result[1]
            
            # Periksa komutatifitas perkalian
            comm_result = self._check_commutativity(elements, multiplication_table)
            properties[RingProperty.COMMUTATIVE_MULTIPLICATION] = comm_result[0]
            details['commutative_multiplication'] = comm_result[1]
            
            # Periksa elemen unity
            unity_result = self._check_unity(elements, multiplication_table)
            properties[RingProperty.HAS_UNITY] = unity_result[0]
            details['unity'] = unity_result[1]
            
            # Periksa zero divisor
            zero_div_result = self._check_zero_divisors(elements, addition_table, multiplication_table)
            properties[RingProperty.HAS_ZERO_DIVISORS] = zero_div_result[0]
            details['zero_divisors'] = zero_div_result[1]
            
            # Periksa invers perkalian
            inv_result = self._check_multiplicative_inverses(elements, multiplication_table)
            properties[RingProperty.HAS_INVERSES] = inv_result[0]
            details['inverses'] = inv_result[1]
            
            # Tentukan apakah ini ring
            is_ring = (
                properties.get(RingProperty.ABELIAN_ADDITION, False) and
                properties.get(RingProperty.ASSOCIATIVE_MULTIPLICATION, False) and
                properties.get(RingProperty.DISTRIBUTIVE, False)
            )
            
            # Klasifikasi
            classification = self._classify_ring(properties)
            
            analysis_time = time.time() - start_time
            
            result = RingAnalysisResult(
                is_ring=is_ring,
                properties=properties,
                details=details,
                analysis_time=analysis_time,
                error_messages=error_messages,
                classification=classification
            )
            
            return result
            
        except Exception as e:
            analysis_time = time.time() - start_time
            return RingAnalysisResult(
                is_ring=False,
                properties={},
                details={},
                analysis_time=analysis_time,
                error_messages=[str(e)],
                classification="Error selama analisis"
            )
    
    def _validate_input(self, elements: List[str], 
                       addition_table: List[List[str]], 
                       multiplication_table: List[List[str]]) -> None:
        """Validasi input data"""
        n = len(elements)
        if n < 2:
            raise ValidationError("Ring harus memiliki setidaknya 2 elemen")
        
        if len(addition_table) != n or any(len(row) != n for row in addition_table):
            raise ValidationError("Dimensi tabel penjumlahan tidak sesuai")
            
        if len(multiplication_table) != n or any(len(row) != n for row in multiplication_table):
            raise ValidationError("Dimensi tabel perkalian tidak sesuai")
        
        element_set = set(elements)
        for table in [addition_table, multiplication_table]:
            for row in table:
                for entry in row:
                    if entry not in element_set:
                        raise ValidationError(f"Entri tabel '{entry}' tidak ada dalam set elemen")
    
    def _check_abelian_group(self, elements: List[str], 
                           addition_table: List[List[str]]) -> Tuple[bool, Dict[str, Any]]:
        """Periksa apakah penjumlahan membentuk grup abelian"""
        details = {}
        
        # Periksa asosiatifitas
        associative = self._check_associativity(elements, addition_table)[0]
        details['associativity'] = associative
        
        # Periksa komutatifitas
        commutative = self._check_commutativity(elements, addition_table)[0]
        details['commutativity'] = commutative
        
        # Periksa identitas
        identity_result = self._check_identity(elements, addition_table)
        identity_exists = identity_result[0]
        details['identity'] = identity_result[1]
        
        # Periksa invers
        if identity_exists:
            inverses_result = self._check_inverses(elements, addition_table, identity_result[1].get('element'))
            inverses_exist = inverses_result[0]
            details['inverses'] = inverses_result[1]
        else:
            inverses_exist = False
            details['inverses'] = {'reason': 'Tidak ada elemen identitas'}
        
        is_abelian = associative and commutative and identity_exists and inverses_exist
        return is_abelian, details
    
    def _check_associativity(self, elements: List[str], 
                           table: List[List[str]]) -> Tuple[bool, Dict[str, Any]]:
        """Periksa sifat asosiatif"""
        details = {'counterexamples': []}
        element_to_index = {elem: i for i, elem in enumerate(elements)}
        
        for a in elements:
            for b in elements:
                for c in elements:
                    # (a op b) op c
                    ab_index = element_to_index[table[element_to_index[a]][element_to_index[b]]]
                    left = table[ab_index][element_to_index[c]]
                    
                    # a op (b op c)
                    bc_index = element_to_index[table[element_to_index[b]][element_to_index[c]]]
                    right = table[element_to_index[a]][bc_index]
                    
                    if left != right:
                        details['counterexamples'].append({
                            'a': a, 'b': b, 'c': c,
                            'left_result': left, 'right_result': right
                        })
                        if len(details['counterexamples']) >= 3:
                            return False, details
        
        return len(details['counterexamples']) == 0, details
    
    def _check_commutativity(self, elements: List[str], 
                           table: List[List[str]]) -> Tuple[bool, Dict[str, Any]]:
        """Periksa sifat komutatif"""
        details = {'counterexamples': []}
        element_to_index = {elem: i for i, elem in enumerate(elements)}
        
        for a in elements:
            for b in elements:
                ab = table[element_to_index[a]][element_to_index[b]]
                ba = table[element_to_index[b]][element_to_index[a]]
                
                if ab != ba:
                    details['counterexamples'].append({
                        'a': a, 'b': b, 'ab': ab, 'ba': ba
                    })
                    if len(details['counterexamples']) >= 3:
                        return False, details
        
        return len(details['counterexamples']) == 0, details
    
    def _check_identity(self, elements: List[str], 
                       table: List[List[str]]) -> Tuple[bool, Dict[str, Any]]:
        """Periksa elemen identitas"""
        element_to_index = {elem: i for i, elem in enumerate(elements)}
        
        for candidate in elements:
            is_identity = True
            candidate_index = element_to_index[candidate]
            
            for elem in elements:
                elem_index = element_to_index[elem]
                if (table[candidate_index][elem_index] != elem or 
                    table[elem_index][candidate_index] != elem):
                    is_identity = False
                    break
            
            if is_identity:
                return True, {'element': candidate, 'index': candidate_index}
        
        return False, {'element': None}
    
    def _check_inverses(self, elements: List[str], table: List[List[str]], 
                       identity: Optional[str]) -> Tuple[bool, Dict[str, Any]]:
        """Periksa elemen invers"""
        if identity is None:
            return False, {'reason': 'Tidak ditemukan elemen identitas'}
        
        details = {'inverses': {}, 'missing_inverses': []}
        element_to_index = {elem: i for i, elem in enumerate(elements)}
        
        for elem in elements:
            elem_index = element_to_index[elem]
            inverse_found = False
            
            for candidate in elements:
                candidate_index = element_to_index[candidate]
                
                if (table[elem_index][candidate_index] == identity and 
                    table[candidate_index][elem_index] == identity):
                    details['inverses'][elem] = candidate
                    inverse_found = True
                    break
            
            if not inverse_found:
                details['missing_inverses'].append(elem)
        
        return len(details['missing_inverses']) == 0, details
    
    def _check_distributivity(self, elements: List[str], 
                            addition_table: List[List[str]], 
                            multiplication_table: List[List[str]]) -> Tuple[bool, Dict[str, Any]]:
        """Periksa sifat distributif"""
        details = {'counterexamples': []}
        element_to_index = {elem: i for i, elem in enumerate(elements)}
        
        for a in elements:
            for b in elements:
                for c in elements:
                    # a * (b + c)
                    bc_sum = addition_table[element_to_index[b]][element_to_index[c]]
                    left = multiplication_table[element_to_index[a]][element_to_index[bc_sum]]
                    
                    # (a * b) + (a * c)
                    ab = multiplication_table[element_to_index[a]][element_to_index[b]]
                    ac = multiplication_table[element_to_index[a]][element_to_index[c]]
                    right = addition_table[element_to_index[ab]][element_to_index[ac]]
                    
                    if left != right:
                        details['counterexamples'].append({
                            'a': a, 'b': b, 'c': c,
                            'left_distributive': left, 'right_distributive': right
                        })
                        if len(details['counterexamples']) >= 3:
                            return False, details
        
        return len(details['counterexamples']) == 0, details
    
    def _check_unity(self, elements: List[str], 
                    multiplication_table: List[List[str]]) -> Tuple[bool, Dict[str, Any]]:
        """Periksa elemen unity (identitas perkalian)"""
        return self._check_identity(elements, multiplication_table)
    
    def _check_zero_divisors(self, elements: List[str], 
                           addition_table: List[List[str]], 
                           multiplication_table: List[List[str]]) -> Tuple[bool, Dict[str, Any]]:
        """Periksa zero divisor"""
        # Cari identitas aditif
        zero_result = self._check_identity(elements, addition_table)
        if not zero_result[0]:
            return False, {'reason': 'Tidak ditemukan identitas aditif'}
        
        zero_element = zero_result[1]['element']
        details = {'zero_divisors': [], 'zero_element': zero_element}
        element_to_index = {elem: i for i, elem in enumerate(elements)}
        
        for a in elements:
            if a == zero_element:
                continue
            for b in elements:
                if b == zero_element:
                    continue
                
                product = multiplication_table[element_to_index[a]][element_to_index[b]]
                if product == zero_element:
                    details['zero_divisors'].append({'a': a, 'b': b})
        
        return len(details['zero_divisors']) > 0, details
    
    def _check_multiplicative_inverses(self, elements: List[str], 
                                     multiplication_table: List[List[str]]) -> Tuple[bool, Dict[str, Any]]:
        """Periksa invers perkalian"""
        unity_result = self._check_identity(elements, multiplication_table)
        if not unity_result[0]:
            return False, {'reason': 'Tidak ditemukan identitas perkalian'}
        
        unity_element = unity_result[1]['element']
        return self._check_inverses(elements, multiplication_table, unity_element)
    
    def _classify_ring(self, properties: Dict[RingProperty, bool]) -> str:
        """Klasifikasi ring berdasarkan properti"""
        if not properties.get(RingProperty.ABELIAN_ADDITION, False):
            return "Bukan ring - penjumlahan bukan abelian"
        
        if not properties.get(RingProperty.ASSOCIATIVE_MULTIPLICATION, False):
            return "Bukan ring - perkalian tidak asosiatif"
        
        if not properties.get(RingProperty.DISTRIBUTIVE, False):
            return "Bukan ring - hukum distributif gagal"
        
        # Ini adalah ring, klasifikasi lebih lanjut
        has_unity = properties.get(RingProperty.HAS_UNITY, False)
        is_commutative = properties.get(RingProperty.COMMUTATIVE_MULTIPLICATION, False)
        has_zero_divisors = properties.get(RingProperty.HAS_ZERO_DIVISORS, False)
        has_inverses = properties.get(RingProperty.HAS_INVERSES, False)
        
        if has_inverses and has_unity and not has_zero_divisors:
            if is_commutative:
                return "Field (Lapangan)"
            else:
                return "Division Ring (Skew Field)"
        elif has_unity and is_commutative and not has_zero_divisors:
            return "Integral Domain"
        elif has_unity and is_commutative:
            return "Ring Komutatif dengan Unity"
        elif is_commutative:
            return "Ring Komutatif"
        elif has_unity:
            return "Ring dengan Unity"
        else:
            return "Ring"

# ============================================================================
# KELAS APLIKASI UTAMA
# ============================================================================

class RingCheckerPro:
    """Kelas aplikasi utama - semua dalam satu file"""
    
    def __init__(self):
        # Inisialisasi komponen dasar terlebih dahulu
        self.config = AppConfig()
        self.error_handler = ErrorHandler()
        self.db_manager = DatabaseManager(self.config.database_path)
        self.ring_theory = AdvancedRingTheory()
        
        # Inisialisasi tkinter root PERTAMA
        self.root = tk.Tk()
        self.root.title("Ring Checker Pro v2.0 - Edisi Single File")
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        self.root.minsize(1000, 700)
        
        # Buat theme manager SEBELUM setup GUI lainnya
        self.theme_manager = ModernThemeManager(self.root)
        
        # Sekarang aman untuk setup komponen GUI
        self._setup_menu()
        self._setup_layout()
        
        # Terapkan tema setelah semua diinisialisasi
        self.theme_manager.apply_theme(self.config.theme_name, self.config.theme_mode)
        
        # Inisialisasi variabel data
        self.current_calculation = None
        self.table_entries_add = []
        self.table_entries_mul = []
        
        print("Ring Checker Pro berhasil diinisialisasi")
    
    def _setup_menu(self):
        """Setup menu aplikasi"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Kalkulasi Baru", command=self._new_calculation)
        file_menu.add_command(label="Simpan Kalkulasi", command=self._save_calculation)
        file_menu.add_command(label="Muat Kalkulasi", command=self._load_calculation)
        file_menu.add_separator()
        file_menu.add_command(label="Ekspor ke JSON", command=self._export_to_json)
        file_menu.add_command(label="Impor dari JSON", command=self._import_from_json)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self._on_closing)
        
        # Menu View
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tampilan", menu=view_menu)
        view_menu.add_command(label="Toggle Tema", command=self._toggle_theme)
        view_menu.add_command(label="Bersihkan Tabel", command=self._clear_tables)
        view_menu.add_command(label="Mode Layar Penuh", command=self._toggle_fullscreen)
        
        # Menu Help
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Bantuan", menu=help_menu)
        help_menu.add_command(label="Tentang", command=self._show_about)
        help_menu.add_command(label="Panduan Penggunaan", command=self._show_guide)
    
    def _setup_layout(self):
        """Setup layout utama"""
        # Konfigurasi grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Container utama
        self.main_container = ttk.Frame(self.root, style="Modern.TFrame")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Header
        self._create_header()
        
        # Notebook utama
        self._create_notebook()
        
        # Status bar
        self._create_status_bar()
        
        # Event bindings
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.bind("<Control-n>", lambda e: self._new_calculation())
        self.root.bind("<Control-s>", lambda e: self._save_calculation())
        self.root.bind("<F11>", lambda e: self._toggle_fullscreen())
    
    def _create_header(self):
        """Buat header dengan kontrol"""
        header_frame = ttk.LabelFrame(
            self.main_container, 
            text="Konfigurasi Analisis Ring",
            style="Modern.TLabelframe"
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Input ukuran
        ttk.Label(header_frame, text="Ukuran Ring:", style="Modern.TLabel").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        
        self.size_var = tk.StringVar(value="3")
        size_spinbox = ttk.Spinbox(
            header_frame, 
            from_=2, 
            to=self.config.max_table_size,
            width=5,
            textvariable=self.size_var,
            command=self._on_size_changed
        )
        size_spinbox.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        # Tombol-tombol
        ttk.Button(
            header_frame,
            text="Generate Tabel",
            command=self._generate_tables,
            style="Modern.TButton"
        ).grid(row=0, column=2, padx=10, pady=10)
        
        self.analyze_btn = ttk.Button(
            header_frame,
            text="Analisis Ring",
            command=self._start_analysis,
            style="Modern.TButton",
            state="disabled"
        )
        self.analyze_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            header_frame,
            variable=self.progress_var,
            mode='determinate'
        )
        self.progress_bar.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=(0, 10))
    
    def _create_notebook(self):
        """Buat notebook utama"""
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # Tab tabel
        self._create_tables_tab()
        
        # Tab hasil
        self._create_results_tab()
        
        # Tab sampel
        self._create_samples_tab()
        
        # Tab riwayat
        self._create_history_tab()
    
    def _create_tables_tab(self):
        """Buat tab input tabel"""
        tables_frame = ttk.Frame(self.notebook)
        self.notebook.add(tables_frame, text="Tabel Operasi")
        
        tables_frame.grid_rowconfigure(0, weight=1)
        tables_frame.grid_columnconfigure(0, weight=1)
        tables_frame.grid_columnconfigure(1, weight=1)
        
        # Tabel penjumlahan
        self.add_frame = ttk.LabelFrame(
            tables_frame, 
            text="Tabel Penjumlahan (+)", 
            style="Modern.TLabelframe"
        )
        self.add_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Tabel perkalian
        self.mul_frame = ttk.LabelFrame(
            tables_frame, 
            text="Tabel Perkalian (×)", 
            style="Modern.TLabelframe"
        )
        self.mul_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
    
    def _create_results_tab(self):
        """Buat tab hasil"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Hasil Analisis")
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Area teks dengan scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        self.results_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#2d2d2d",
            fg="#ffffff"
        )
        self.results_text.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        v_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_text.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal", command=self.results_text.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.results_text.configure(xscrollcommand=h_scrollbar.set)
    
    def _create_samples_tab(self):
        """Buat tab sampel"""
        samples_frame = ttk.Frame(self.notebook)
        self.notebook.add(samples_frame, text="Sampel Ring")
        
        # Tombol sampel ring
        samples = [
            ("Field (Z₃)", "Contoh field 3x3", self._load_field_sample),
            ("Ring Boolean", "Ring boolean 2x2", self._load_boolean_sample),
            ("Ring Zero", "Ring dengan perkalian nol", self._load_zero_sample),
            ("Integral Domain", "Domain integral 4x4", self._load_integral_sample),
            ("Non-Komutatif", "Ring non-komutatif", self._load_noncomm_sample),
            ("Zero Divisors", "Ring dengan zero divisor", self._load_zerodiv_sample)
        ]
        
        for i, (name, desc, command) in enumerate(samples):
            frame = ttk.LabelFrame(samples_frame, text=name, style="Modern.TLabelframe")
            frame.grid(row=i//2, column=i%2, sticky="ew", padx=10, pady=5)
            
            ttk.Label(frame, text=desc, style="Modern.TLabel").pack(pady=5)
            ttk.Button(frame, text="Muat Sampel", command=command, style="Modern.TButton").pack(pady=5)
    
    def _create_history_tab(self):
        """Buat tab riwayat"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="Riwayat Kalkulasi")
        
        # Daftar riwayat
        columns = ("Nama", "Ukuran", "Klasifikasi", "Tanggal")
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings",
            style="Modern.Treeview"
        )
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        self.history_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Scrollbar untuk riwayat
        hist_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        hist_scrollbar.grid(row=0, column=1, sticky="ns")
        self.history_tree.configure(yscrollcommand=hist_scrollbar.set)
        
        # Kontrol riwayat
        hist_controls = ttk.Frame(history_frame)
        hist_controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Button(hist_controls, text="Muat Terpilih", command=self._load_from_history, style="Modern.TButton").pack(side="left", padx=5)
        ttk.Button(hist_controls, text="Hapus Terpilih", command=self._delete_from_history, style="Modern.TButton").pack(side="left", padx=5)
        ttk.Button(hist_controls, text="Refresh", command=self._refresh_history, style="Modern.TButton").pack(side="left", padx=5)
        
        # Konfigurasi grid
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        
        # Muat riwayat
        self._refresh_history()
    
    def _create_status_bar(self):
        """Buat status bar"""
        self.status_bar = ttk.Frame(self.main_container)
        self.status_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Siap")
        status_label = ttk.Label(self.status_bar, textvariable=self.status_var, style="Modern.TLabel")
        status_label.pack(side="left", padx=10)
        
        # Indikator tema
        self.theme_var = tk.StringVar(value=f"{self.config.theme_name.title()} ({self.config.theme_mode.title()})")
        theme_label = ttk.Label(self.status_bar, textvariable=self.theme_var, style="Modern.TLabel")
        theme_label.pack(side="right", padx=10)
    
    # Event handlers
    def _on_size_changed(self):
        """Handle perubahan ukuran"""
        try:
            size = int(self.size_var.get())
            if 2 <= size <= self.config.max_table_size:
                self._update_status(f"Ukuran ring diset ke {size}x{size}")
            else:
                messagebox.showwarning("Ukuran Tidak Valid", f"Ukuran harus antara 2 dan {self.config.max_table_size}")
                self.size_var.set("3")
        except ValueError:
            self.size_var.set("3")
    
    def _generate_tables(self):
        """Generate tabel operasi"""
        try:
            size = int(self.size_var.get())
            self._create_table_grids(size)
            self.analyze_btn.configure(state="normal")
            self._update_status(f"Generated tabel {size}x{size}")
        except Exception as e:
            self.error_handler.handle_critical_error(e, "generate tabel")
    
    def _create_table_grids(self, size: int):
        """Buat grid tabel interaktif"""
        # Hapus yang ada
        for widget in self.add_frame.winfo_children():
            widget.destroy()
        for widget in self.mul_frame.winfo_children():
            widget.destroy()
        
        self.table_entries_add = []
        self.table_entries_mul = []
        
        # Generate elemen
        elements = [self._number_to_letters(i) for i in range(size)]
        
        # Buat tabel
        self._create_single_table(self.add_frame, elements, self.table_entries_add, "+")
        self._create_single_table(self.mul_frame, elements, self.table_entries_mul, "×")
    
    def _create_single_table(self, parent, elements, entries_list, operation):
        """Buat satu tabel operasi"""
        size = len(elements)
        
        # Header
        ttk.Label(parent, text=operation, style="Modern.TLabel").grid(row=0, column=0, padx=2, pady=2)
        
        # Header kolom
        for j, elem in enumerate(elements):
            ttk.Label(parent, text=elem, style="Modern.TLabel").grid(row=0, column=j+1, padx=2, pady=2)
        
        # Baris
        for i, elem in enumerate(elements):
            # Header baris
            ttk.Label(parent, text=elem, style="Modern.TLabel").grid(row=i+1, column=0, padx=2, pady=2)
            
            # Entri
            row_entries = []
            for j in range(size):
                entry = ttk.Entry(parent, width=4, justify="center", style="Modern.TEntry")
                entry.grid(row=i+1, column=j+1, padx=1, pady=1)
                entry.bind("<KeyRelease>", self._on_table_change)
                row_entries.append(entry)
            
            entries_list.append(row_entries)
    
    def _on_table_change(self, event=None):
        """Handle perubahan konten tabel"""
        pass  # Bisa implement auto-validation di sini
    
    def _start_analysis(self):
        """Mulai analisis ring"""
        if not self._validate_tables():
            return
        
        # Disable tombol dan tampilkan progress
        self.analyze_btn.configure(state="disabled")
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()
        self._update_status("Menganalisis properti ring...")
        
        # Mulai analisis dalam thread
        threading.Thread(target=self._perform_analysis, daemon=True).start()
    
    def _perform_analysis(self):
        """Lakukan analisis (dalam thread)"""
        try:
            size = int(self.size_var.get())
            elements = [self._number_to_letters(i) for i in range(size)]
            
            # Ekstrak tabel
            addition_table = []
            multiplication_table = []
            
            for i in range(size):
                add_row = [entry.get().upper() for entry in self.table_entries_add[i]]
                mul_row = [entry.get().upper() for entry in self.table_entries_mul[i]]
                addition_table.append(add_row)
                multiplication_table.append(mul_row)
            
            # Analisis
            result = self.ring_theory.analyze_ring(elements, addition_table, multiplication_table)
            
            # Update GUI
            self.root.after(0, self._analysis_complete, result)
            
        except Exception as e:
            self.root.after(0, self._analysis_error, e)
    
    def _analysis_complete(self, result: RingAnalysisResult):
        """Handle penyelesaian analisis"""
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')
        self.analyze_btn.configure(state="normal")
        
        # Tampilkan hasil
        self._display_results(result)
        
        # Pindah ke tab hasil
        self.notebook.select(1)
        
        # Update status
        self._update_status(f"Analisis selesai: {result.classification} ({result.analysis_time:.2f}s)")
        
        # Simpan ke riwayat
        if result.is_ring:
            self._save_to_history(result)
    
    def _analysis_error(self, error: Exception):
        """Handle error analisis"""
        self.progress_bar.stop()
        self.analyze_btn.configure(state="normal")
        self.error_handler.handle_calculation_error(error, "analisis ring")
        self._update_status("Analisis gagal")
    
    def _display_results(self, result: RingAnalysisResult):
        """Tampilkan hasil analisis"""
        self.results_text.delete(1.0, tk.END)
        
        # Header
        self.results_text.insert(tk.END, "HASIL ANALISIS RING\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Klasifikasi
        if result.is_ring:
            self.results_text.insert(tk.END, "✓ Struktur ini ADALAH ring!\n\n")
            self.results_text.insert(tk.END, f"Klasifikasi: {result.classification}\n\n")
        else:
            self.results_text.insert(tk.END, "✗ Struktur ini BUKAN ring.\n\n")
            self.results_text.insert(tk.END, f"Alasan: {result.classification}\n\n")
        
        # Properti
        self.results_text.insert(tk.END, "PROPERTI:\n")
        self.results_text.insert(tk.END, "-" * 12 + "\n")
        
        property_names = {
            'ABELIAN_ADDITION': 'Grup Abelian Penjumlahan',
            'ASSOCIATIVE_MULTIPLICATION': 'Perkalian Asosiatif',
            'DISTRIBUTIVE': 'Sifat Distributif',
            'COMMUTATIVE_MULTIPLICATION': 'Perkalian Komutatif',
            'HAS_UNITY': 'Unity Perkalian',
            'HAS_ZERO_DIVISORS': 'Zero Divisor Ada',
            'HAS_INVERSES': 'Invers Perkalian'
        }
        
        for prop, value in result.properties.items():
            prop_name = property_names.get(prop.name, prop.name)
            status = "✓" if value else "✗"
            self.results_text.insert(tk.END, f"{status} {prop_name}\n")
        
        # Analisis detail
        if result.details:
            self.results_text.insert(tk.END, f"\n\nANALISIS DETAIL:\n")
            self.results_text.insert(tk.END, "-" * 18 + "\n")
            
            for key, value in result.details.items():
                if key != 'classification':
                    self.results_text.insert(tk.END, f"\n{key.replace('_', ' ').title()}:\n")
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, list) and subvalue:
                                self.results_text.insert(tk.END, f"  {subkey}: {len(subvalue)} ditemukan\n")
                                if len(subvalue) <= 3:  # Tampilkan beberapa contoh pertama
                                    for item in subvalue[:3]:
                                        self.results_text.insert(tk.END, f"    {item}\n")
                            else:
                                self.results_text.insert(tk.END, f"  {subkey}: {subvalue}\n")
                    else:
                        self.results_text.insert(tk.END, f"  {value}\n")
        
        # Performa
        self.results_text.insert(tk.END, f"\n\nPERFORMA:\n")
        self.results_text.insert(tk.END, "-" * 12 + "\n")
        self.results_text.insert(tk.END, f"Waktu analisis: {result.analysis_time:.4f} detik\n")
        
        # Error
        if result.error_messages:
            self.results_text.insert(tk.END, f"\n\nERROR:\n")
            self.results_text.insert(tk.END, "-" * 8 + "\n")
            for msg in result.error_messages:
                self.results_text.insert(tk.END, f"⚠ {msg}\n")
    
    def _validate_tables(self) -> bool:
        """Validasi konten tabel"""
        try:
            size = int(self.size_var.get())
            elements = [self._number_to_letters(i) for i in range(size)]
            element_set = set(elements)
            
            for table in [self.table_entries_add, self.table_entries_mul]:
                for row in table:
                    for entry in row:
                        value = entry.get().upper()
                        if not value:
                            messagebox.showerror("Tabel Tidak Lengkap", "Silakan isi semua entri tabel")
                            entry.focus()
                            return False
                        if value not in element_set:
                            messagebox.showerror("Entri Tidak Valid", f"'{value}' bukan elemen yang valid")
                            entry.focus()
                            return False
            return True
        except Exception as e:
            self.error_handler.handle_validation_error(e, "validasi tabel")
            return False
    
    def _save_to_history(self, result: RingAnalysisResult):
        """Simpan hasil ke riwayat"""
        try:
            size = int(self.size_var.get())
            elements = [self._number_to_letters(i) for i in range(size)]
            
            # Ekstrak tabel
            addition_table = []
            multiplication_table = []
            
            for i in range(size):
                add_row = [entry.get().upper() for entry in self.table_entries_add[i]]
                mul_row = [entry.get().upper() for entry in self.table_entries_mul[i]]
                addition_table.append(add_row)
                multiplication_table.append(mul_row)
            
            data = {
                'name': f"Ring_{size}x{size}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'size': size,
                'addition_table': addition_table,
                'multiplication_table': multiplication_table,
                'results': result.to_dict()
            }
            
            calc_id = self.db_manager.save_calculation(data)
            if calc_id:
                self._refresh_history()
                print(f"Kalkulasi disimpan dengan ID: {calc_id}")
        except Exception as e:
            print(f"Gagal menyimpan ke riwayat: {e}")
    
    # Menu handlers
    def _new_calculation(self):
        """Mulai kalkulasi baru"""
        if messagebox.askyesno("Kalkulasi Baru", "Mulai kalkulasi baru? Perubahan yang belum disimpan akan hilang."):
            self._clear_tables()
            self.current_calculation = None
            self._update_status("Kalkulasi baru dimulai")
    
    def _save_calculation(self):
        """Simpan kalkulasi saat ini"""
        if not self._validate_tables():
            return
        
        name = simpledialog.askstring("Simpan Kalkulasi", "Masukkan nama kalkulasi:")
        if name:
            try:
                size = int(self.size_var.get())
                
                # Ekstrak tabel
                addition_table = []
                multiplication_table = []
                
                for i in range(size):
                    add_row = [entry.get().upper() for entry in self.table_entries_add[i]]
                    mul_row = [entry.get().upper() for entry in self.table_entries_mul[i]]
                    addition_table.append(add_row)
                    multiplication_table.append(mul_row)
                
                data = {
                    'name': name,
                    'size': size,
                    'addition_table': addition_table,
                    'multiplication_table': multiplication_table,
                    'results': {}
                }
                
                calc_id = self.db_manager.save_calculation(data)
                if calc_id:
                    self._refresh_history()
                    self._update_status(f"Kalkulasi '{name}' disimpan")
                    messagebox.showinfo("Berhasil", f"Kalkulasi disimpan dengan ID: {calc_id}")
                else:
                    messagebox.showerror("Error", "Gagal menyimpan kalkulasi")
            except Exception as e:
                self.error_handler.handle_critical_error(e, "simpan kalkulasi")
    
    def _load_calculation(self):
        """Muat kalkulasi dari database"""
        self.notebook.select(3)  # Pindah ke tab riwayat
        messagebox.showinfo("Muat Kalkulasi", "Silakan pilih kalkulasi dari tab Riwayat")
    
    def _export_to_json(self):
        """Ekspor kalkulasi saat ini ke JSON"""
        if not self._validate_tables():
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("File JSON", "*.json"), ("Semua file", "*.*")]
        )
        
        if filename:
            try:
                size = int(self.size_var.get())
                
                # Ekstrak tabel
                addition_table = []
                multiplication_table = []
                
                for i in range(size):
                    add_row = [entry.get().upper() for entry in self.table_entries_add[i]]
                    mul_row = [entry.get().upper() for entry in self.table_entries_mul[i]]
                    addition_table.append(add_row)
                    multiplication_table.append(mul_row)
                
                data = {
                    'name': f"Exported_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'size': size,
                    'elements': [self._number_to_letters(i) for i in range(size)],
                    'addition_table': addition_table,
                    'multiplication_table': multiplication_table,
                    'export_time': datetime.now().isoformat()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self._update_status(f"Diekspor ke {filename}")
                messagebox.showinfo("Berhasil", f"Kalkulasi diekspor ke {filename}")
                
            except Exception as e:
                self.error_handler.handle_critical_error(e, "ekspor ke JSON")
    
    def _import_from_json(self):
        """Impor kalkulasi dari JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("File JSON", "*.json"), ("Semua file", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validasi struktur data
                required_fields = ['size', 'addition_table', 'multiplication_table']
                if not all(field in data for field in required_fields):
                    messagebox.showerror("File Tidak Valid", "File JSON tidak memiliki field yang diperlukan")
                    return
                
                # Muat data
                size = data['size']
                self.size_var.set(str(size))
                self._generate_tables()
                
                # Isi tabel
                for i in range(size):
                    for j in range(size):
                        self.table_entries_add[i][j].delete(0, tk.END)
                        self.table_entries_add[i][j].insert(0, data['addition_table'][i][j])
                        
                        self.table_entries_mul[i][j].delete(0, tk.END)
                        self.table_entries_mul[i][j].insert(0, data['multiplication_table'][i][j])
                
                self._update_status(f"Diimpor dari {filename}")
                messagebox.showinfo("Berhasil", f"Kalkulasi diimpor dari {filename}")
                
            except Exception as e:
                self.error_handler.handle_critical_error(e, "impor dari JSON")
    
    def _toggle_theme(self):
        """Toggle mode tema"""
        self.theme_manager.toggle_mode()
        self.config.theme_mode = self.theme_manager.current_mode
        self.theme_var.set(f"{self.config.theme_name.title()} ({self.config.theme_mode.title()})")
        self._update_status(f"Beralih ke mode {self.config.theme_mode}")
        
        # Update warna teks hasil
        colors = self.theme_manager.get_current_colors()
        self.results_text.configure(
            bg=colors["entry_bg"],
            fg=colors["entry_fg"],
            insertbackground=colors["accent"]
        )
    
    def _clear_tables(self):
        """Bersihkan semua tabel"""
        for table in [self.table_entries_add, self.table_entries_mul]:
            for row in table:
                for entry in row:
                    entry.delete(0, tk.END)
        
        self.results_text.delete(1.0, tk.END)
        self._update_status("Tabel dibersihkan")
    
    def _toggle_fullscreen(self):
        """Toggle mode layar penuh"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
    
    def _show_about(self):
        """Tampilkan dialog tentang"""
        about_text = """Ring Checker Pro v2.0
Edisi Single File

Aplikasi Analisis Teori Ring yang Canggih

Fitur:
• Analisis properti ring yang komprehensif
• GUI modern dengan tema gelap/terang
• Integrasi database untuk riwayat
• Kemampuan impor/ekspor
• Perpustakaan sampel ring
• Analisis multi-threaded

Dibuat dengan Python, Tkinter, dan SQLite
Semua fungsionalitas dalam satu file untuk distribusi mudah!
        """
        messagebox.showinfo("Tentang Ring Checker Pro", about_text)
    
    def _show_guide(self):
        """Tampilkan panduan penggunaan"""
        guide_text = """PANDUAN PENGGUNAAN RING CHECKER PRO

1. MEMBUAT TABEL OPERASI:
   - Pilih ukuran ring (2-15)
   - Klik "Generate Tabel"
   - Isi tabel penjumlahan dan perkalian

2. ANALISIS RING:
   - Pastikan semua sel terisi
   - Klik "Analisis Ring"
   - Lihat hasil di tab "Hasil Analisis"

3. MENYIMPAN & MEMUAT:
   - File > Simpan Kalkulasi (ke database)
   - File > Ekspor ke JSON (file eksternal)
   - Gunakan tab "Riwayat" untuk memuat kembali

4. SAMPEL RING:
   - Tab "Sampel Ring" berisi contoh-contoh
   - Klik "Muat Sampel" untuk auto-fill

5. KEYBOARD SHORTCUTS:
   - Ctrl+N: Kalkulasi baru
   - Ctrl+S: Simpan kalkulasi
   - F11: Mode layar penuh

TIPS:
- Gunakan huruf A, B, C, ... untuk elemen
- Pastikan closure: hasil operasi harus elemen ring
- Periksa konsistensi entri tabel
        """
        
        # Buat window baru untuk panduan
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Panduan Penggunaan")
        guide_window.geometry("600x500")
        
        text_widget = tk.Text(guide_window, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert(1.0, guide_text)
        text_widget.configure(state="disabled")
    
    def _on_closing(self):
        """Handle penutupan aplikasi"""
        if messagebox.askyesno("Keluar", "Anda yakin ingin keluar?"):
            print("Ring Checker Pro ditutup...")
            self.root.destroy()
    
    # Method untuk memuat sampel
    def _load_field_sample(self):
        """Muat sampel field (Z₃)"""
        self.size_var.set("3")
        self._generate_tables()
        
        add_data = [['A', 'B', 'C'], ['B', 'C', 'A'], ['C', 'A', 'B']]
        mul_data = [['A', 'A', 'A'], ['A', 'B', 'C'], ['A', 'C', 'B']]
        
        self._fill_tables(add_data, mul_data)
        self._update_status("Dimuat sampel field Z₃")
    
    def _load_boolean_sample(self):
        """Muat sampel ring boolean"""
        self.size_var.set("2")
        self._generate_tables()
        
        add_data = [['A', 'B'], ['B', 'A']]
        mul_data = [['A', 'A'], ['A', 'B']]
        
        self._fill_tables(add_data, mul_data)
        self._update_status("Dimuat sampel ring boolean")
    
    def _load_zero_sample(self):
        """Muat sampel ring zero"""
        self.size_var.set("3")
        self._generate_tables()
        
        add_data = [['A', 'B', 'C'], ['B', 'C', 'A'], ['C', 'A', 'B']]
        mul_data = [['A', 'A', 'A'], ['A', 'A', 'A'], ['A', 'A', 'A']]
        
        self._fill_tables(add_data, mul_data)
        self._update_status("Dimuat sampel ring zero")
    
    def _load_integral_sample(self):
        """Muat sampel integral domain"""
        self.size_var.set("4")
        self._generate_tables()
        
        add_data = [['A', 'B', 'C', 'D'], ['B', 'A', 'D', 'C'], 
                   ['C', 'D', 'A', 'B'], ['D', 'C', 'B', 'A']]
        mul_data = [['A', 'A', 'A', 'A'], ['A', 'B', 'C', 'D'], 
                   ['A', 'C', 'C', 'A'], ['A', 'D', 'A', 'D']]
        
        self._fill_tables(add_data, mul_data)
        self._update_status("Dimuat sampel integral domain")
    
    def _load_noncomm_sample(self):
        """Muat sampel non-komutatif"""
        self.size_var.set("3")
        self._generate_tables()
        
        add_data = [['A', 'B', 'C'], ['B', 'C', 'A'], ['C', 'A', 'B']]
        mul_data = [['A', 'A', 'A'], ['A', 'B', 'C'], ['A', 'C', 'A']]
        
        self._fill_tables(add_data, mul_data)
        self._update_status("Dimuat sampel non-komutatif")
    
    def _load_zerodiv_sample(self):
        """Muat sampel zero divisor"""
        self.size_var.set("4")
        self._generate_tables()
        
        add_data = [['A', 'B', 'C', 'D'], ['B', 'A', 'D', 'C'], 
                   ['C', 'D', 'A', 'B'], ['D', 'C', 'B', 'A']]
        mul_data = [['A', 'A', 'A', 'A'], ['A', 'B', 'C', 'D'], 
                   ['A', 'A', 'A', 'A'], ['A', 'B', 'C', 'D']]
        
        self._fill_tables(add_data, mul_data)
        self._update_status("Dimuat sampel zero divisor")
    
    def _fill_tables(self, add_data, mul_data):
        """Isi tabel dengan data sampel"""
        for i, row in enumerate(add_data):
            for j, value in enumerate(row):
                self.table_entries_add[i][j].delete(0, tk.END)
                self.table_entries_add[i][j].insert(0, value)
        
        for i, row in enumerate(mul_data):
            for j, value in enumerate(row):
                self.table_entries_mul[i][j].delete(0, tk.END)
                self.table_entries_mul[i][j].insert(0, value)
    
    # Method riwayat
    def _refresh_history(self):
        """Refresh riwayat kalkulasi"""
        # Hapus item yang ada
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Muat dari database
        calculations = self.db_manager.get_calculation_list()
        
        for calc in calculations:
            # Coba dapatkan klasifikasi dari hasil
            try:
                calc_data = self.db_manager.load_calculation(calc['id'])
                if calc_data and 'results' in calc_data:
                    results = calc_data['results']
                    classification = results.get('classification', 'Tidak diketahui')
                else:
                    classification = 'Belum dianalisis'
            except:
                classification = 'Tidak diketahui'
            
            self.history_tree.insert('', 'end', values=(
                calc['name'],
                f"{calc['size']}x{calc['size']}",
                classification,
                calc['created_at']
            ))
    
    def _load_from_history(self):
        """Muat kalkulasi terpilih dari riwayat"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Tidak Ada Pilihan", "Silakan pilih kalkulasi untuk dimuat")
            return
        
        item = self.history_tree.item(selection[0])
        calc_name = item['values'][0]
        
        # Cari kalkulasi berdasarkan nama (pendekatan sederhana)
        calculations = self.db_manager.get_calculation_list()
        calc_id = None
        for calc in calculations:
            if calc['name'] == calc_name:
                calc_id = calc['id']
                break
        
        if calc_id:
            calc_data = self.db_manager.load_calculation(calc_id)
            if calc_data:
                # Muat kalkulasi
                size = calc_data['size']
                self.size_var.set(str(size))
                self._generate_tables()
                
                # Isi tabel
                add_table = calc_data['addition_table']
                mul_table = calc_data['multiplication_table']
                
                for i in range(size):
                    for j in range(size):
                        self.table_entries_add[i][j].delete(0, tk.END)
                        self.table_entries_add[i][j].insert(0, add_table[i][j])
                        
                        self.table_entries_mul[i][j].delete(0, tk.END)
                        self.table_entries_mul[i][j].insert(0, mul_table[i][j])
                
                # Pindah ke tab tabel
                self.notebook.select(0)
                
                self._update_status(f"Dimuat kalkulasi: {calc_name}")
                messagebox.showinfo("Berhasil", f"Dimuat kalkulasi: {calc_name}")
            else:
                messagebox.showerror("Error", "Gagal memuat data kalkulasi")
        else:
            messagebox.showerror("Error", "Kalkulasi tidak ditemukan")
    
    def _delete_from_history(self):
        """Hapus kalkulasi terpilih dari riwayat"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Tidak Ada Pilihan", "Silakan pilih kalkulasi untuk dihapus")
            return
        
        if messagebox.askyesno("Konfirmasi Hapus", "Anda yakin ingin menghapus kalkulasi ini?"):
            item = self.history_tree.item(selection[0])
            calc_name = item['values'][0]
            
            # Cari dan hapus kalkulasi
            calculations = self.db_manager.get_calculation_list()
            for calc in calculations:
                if calc['name'] == calc_name:
                    # Hapus dari database (disederhanakan)
                    try:
                        conn = sqlite3.connect(self.db_manager.db_path)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM ring_calculations WHERE id = ?", (calc['id'],))
                        conn.commit()
                        conn.close()
                        
                        self._refresh_history()
                        self._update_status(f"Dihapus kalkulasi: {calc_name}")
                        messagebox.showinfo("Berhasil", f"Dihapus kalkulasi: {calc_name}")
                        break
                    except Exception as e:
                        messagebox.showerror("Error", f"Gagal menghapus kalkulasi: {e}")
    
    # Method utilitas
    def _number_to_letters(self, n: int) -> str:
        """Konversi angka ke huruf (A, B, C, ...)"""
        result = ""
        while True:
            result = chr(65 + n % 26) + result
            n = n // 26 - 1
            if n < 0:
                break
        return result
    
    def _update_status(self, message: str):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def run(self):
        """Jalankan aplikasi"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error aplikasi: {e}")
            self.error_handler.handle_critical_error(e, "aplikasi utama")

# ============================================================================
# TITIK MASUK UTAMA
# ============================================================================

def main():
    """Titik masuk utama"""
    try:
        print("Memulai Ring Checker Pro...")
        app = RingCheckerPro()
        app.run()
    except Exception as e:
        print(f"Gagal memulai aplikasi: {e}")
        messagebox.showerror("Error Kritis", f"Gagal memulai Ring Checker Pro:\n{e}")

if __name__ == "__main__":
    main()
