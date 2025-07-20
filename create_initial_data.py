import pandas as pd
import os

def create_initial_files():
    """Créer les fichiers Excel initiaux avec les données de base"""
    
    # Créer le dossier data s'il n'existe pas
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Données des clients
    clients_data = {
        'code_client': ['CLI001', 'CLI002'],
        'nom': ['Entreprise ABC', 'Société XYZ'],
        'contact': ['contact@abc.com', 'info@xyz.com'],
        'IFU': ['1234567890123', '9876543210987']
    }
    
    # Données des produits
    produits_data = {
        'code_produit': ['PROD01', 'PROD02', 'PROD03', 'PROD04', 'PROD05', 
                        'PROD06', 'PROD07', 'PROD08', 'PROD09', 'PROD10'],
        'libelle': ['Ordinateur portable', 'Souris sans fil', 'Clavier mécanique', 
                   'Écran 24"', 'Imprimante laser', 'Scanner', 'Webcam HD', 
                   'Casque audio', 'Disque dur externe', 'Clé USB 32GB'],
        'prix_unitaire': [800.0, 25.0, 120.0, 180.0, 350.0, 150.0, 80.0, 95.0, 120.0, 15.0]
    }
    
    # Données des cartes de réduction (vide au début)
    cartes_data = {
        'numero_carte': [],
        'code_client': [],
        'taux_reduction': []
    }
    
    # Créer les DataFrames
    df_clients = pd.DataFrame(clients_data)
    df_produits = pd.DataFrame(produits_data)
    df_cartes = pd.DataFrame(cartes_data)
    
    # Sauvegarder en Excel
    df_clients.to_excel('data/Clients.xlsx', index=False)
    df_produits.to_excel('data/Produits.xlsx', index=False)
    df_cartes.to_excel('data/CartesReduction.xlsx', index=False)
    
    print("Fichiers Excel initiaux créés avec succès dans le dossier 'data'")
    print("- Clients.xlsx : 2 clients")
    print("- Produits.xlsx : 10 produits")
    print("- CartesReduction.xlsx : vide (sera rempli automatiquement)")

if __name__ == "__main__":
    create_initial_files() 