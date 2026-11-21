import re

# Lista Marche
CAR_BRANDS = [
    "Abarth", "Alfa Romeo", "Audi", "BMW", "Citroën", "Cupra", "Dacia", 
    "Ferrari", "Fiat", "Ford", "Honda", "Hyundai", "Jaguar", "Jeep", 
    "Kia", "Lamborghini", "Lancia", "Land Rover", "Lexus", "Maserati", 
    "Mazda", "Mercedes-Benz", "Mini", "Mitsubishi", "Nissan", "Opel", 
    "Peugeot", "Porsche", "Renault", "Seat", "Skoda", "Smart", "Subaru", 
    "Suzuki", "Tesla", "Toyota", "Volkswagen", "Volvo", "Altro"
]

# Configurazione Targhe per Paese
PLATE_CONFIG = {
    "Italia": {
        "regex": r"^[A-Za-z]{2}\d{3}[A-Za-z]{2}$",
        "placeholder": "AA123BB",
        "desc": "2 Lettere, 3 Numeri, 2 Lettere",
        "max_len": 7
    },
    "Germania": {
        "regex": r"^[A-Za-z]{1,3}-[A-Za-z]{1,2} \d{1,4}$",
        "placeholder": "B-MW 1234",
        "desc": "Codice Città - Lettere Numeri",
        "max_len": 10
    },
    "Francia": {
        "regex": r"^[A-Za-z]{2}-\d{3}-[A-Za-z]{2}$",
        "placeholder": "AB-123-CD",
        "desc": "2 Lettere - 3 Numeri - 2 Lettere",
        "max_len": 9
    },
    "Spagna": {
        "regex": r"^\d{4}\s?[BCDFGHJKLMNPRSTVWXYZ]{3}$",
        "placeholder": "1234 BCD",
        "desc": "4 Numeri e 3 Consonanti",
        "max_len": 8
    },
    "Regno Unito": {
        "regex": r"^[A-Z]{2}\d{2}\s?[A-Z]{3}$",
        "placeholder": "AB12 CDE",
        "desc": "Formato post-2001 (es. AB12 CDE)",
        "max_len": 8
    },
    "Paesi Bassi": {
        "regex": r"^[A-Z0-9-]{6,8}$", # Semplificata, NL ha molti formati
        "placeholder": "G-123-BB",
        "desc": "Vari formati (es. X-999-XX)",
        "max_len": 10
    }
}