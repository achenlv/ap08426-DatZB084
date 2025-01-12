# Projekta Dokumentācija

## app.py

Šis ir galvenais lietojumprogrammas sākumpunkts. Tas inicializē Flask lietojumprogrammu, iestata žurnālu veidošanu, inicializē datubāzi un reģistrē maršrutu zilās izdrukas.

### Funkcijas:
- `create_app()`: Inicializē Flask lietojumprogrammu, ielādē konfigurāciju, iestata žurnālu veidošanu, inicializē datubāzi un reģistrē zilās izdrukas.

## utils/validators.py

Šis fails satur utilītu funkcijas IP adrešu, CSV failu un fail2ban failu validēšanai.

### Funkcijas:
- `validate_ip(ip: str) -> Optional[str]`: Validē IP adresi vai CIDR notāciju.
- `validate_csv_file(filepath: str) -> bool`: Validē, vai fails pastāv un ir derīgs CSV.
- `validate_fail2ban_file(filepath: str) -> bool`: Validē, vai fails pastāv un tam ir fail2ban formāts.
- `parse_ip_range(ip_range: str) -> list[str]`: Parsē IP diapazonu un atgriež individuālu IP sarakstu.

## utils/logging.py

Šis fails iestata žurnālu veidošanu lietojumprogrammai.

### Funkcijas:
- `get_log_dir()`: Atgriež žurnālu direktoriju no konfigurācijas vai noklusējuma vērtību.
- `setup_logging()`: Konfigurē žurnālu veidošanu ar failu apstrādātāju un konsoles apstrādātāju.

## db/database.py

Šis fails satur funkcijas mijiedarbībai ar SQLite datubāzi.

### Funkcijas:
- `get_db()`: Konteksta pārvaldnieks datubāzes savienojuma iegūšanai.
- `init_db()`: Inicializē datubāzi ar nepieciešamajām tabulām.
- `add_to_blacklist(ip: str, source: str, reason: Optional[str], comment: Optional[str]) -> str`: Pievieno vienu IP melnajam sarakstam.
- `add_to_whitelist(ip: str, source: str, reason: Optional[str], comment: Optional[str]) -> str`: Pievieno vienu IP baltajam sarakstam.
- `get_list(source: Optional[str] = None, list_type: str = 'blacklist') -> List[dict]`: Iegūst ierakstu sarakstu no norādītā saraksta veida.
- `get_blacklist(source: Optional[str] = None) -> List[dict]`: Iegūst melno sarakstu, izņemot ierakstus baltajā sarakstā.
- `get_whitelist(source: Optional[str] = None) -> List[dict]`: Iegūst balto sarakstu.
- `bulk_add(entries: List[tuple], list_type: str, source: Optional[str] = None) -> str`: Masveidā pievieno IP norādītajam saraksta veidam.
- `bulk_add_to_blacklist(entries: List[tuple], source: Optional[str] = None)`: Masveidā pievieno IP melnajam sarakstam.
- `bulk_add_to_whitelist(entries: List[tuple], source: Optional[str] = None)`: Masveidā pievieno IP baltajam sarakstam.

## config/settings.py

Šis fails satur konfigurācijas iestatījumus API, Host un Controller.

### Klases:
- `APISettings`: Konfigurācijas iestatījumi API.
- `HostSettings`: Konfigurācijas iestatījumi Host.
- `ControllerSettings`: Konfigurācijas iestatījumi Controller.

## app/models/__init__.py

Šis fails inicializē Flask lietojumprogrammu un iestata versiju.

### Mainīgie:
- `__version__`: Lietojumprogrammas versija.