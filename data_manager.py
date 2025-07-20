import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data_folder = 'data'
        self.clients_file = os.path.join(self.data_folder, 'Clients.xlsx')
        self.produits_file = os.path.join(self.data_folder, 'Produits.xlsx')
        self.cartes_file = os.path.join(self.data_folder, 'CartesReduction.xlsx')
        self.factures_file = os.path.join(self.data_folder, 'Factures.xlsx')
        
        # Créer le fichier des factures s'il n'existe pas
        self.init_factures_file()
    
    def init_factures_file(self):
        """Initialiser le fichier des factures s'il n'existe pas"""
        if not os.path.exists(self.factures_file):
            factures_data = {
                'numero_facture': [],
                'code_client': [],
                'date_facture': [],
                'total_ht': [],
                'remise': [],
                'total_ht_remise': [],
                'tva': [],
                'total_ttc': []
            }
            df_factures = pd.DataFrame(factures_data)
            df_factures.to_excel(self.factures_file, index=False)
    
    def charger_clients(self):
        """Charger les données des clients"""
        try:
            return pd.read_excel(self.clients_file)
        except FileNotFoundError:
            print("Erreur: Fichier Clients.xlsx non trouvé")
            return pd.DataFrame()
    
    def charger_produits(self):
        """Charger les données des produits"""
        try:
            return pd.read_excel(self.produits_file)
        except FileNotFoundError:
            print("Erreur: Fichier Produits.xlsx non trouvé")
            return pd.DataFrame()
    
    def charger_cartes(self):
        """Charger les données des cartes de réduction"""
        try:
            return pd.read_excel(self.cartes_file)
        except FileNotFoundError:
            # Créer le fichier s'il n'existe pas
            cartes_data = {
                'numero_carte': [],
                'code_client': [],
                'taux_reduction': []
            }
            df_cartes = pd.DataFrame(cartes_data)
            df_cartes.to_excel(self.cartes_file, index=False)
            return df_cartes
    
    def charger_factures(self):
        """Charger les données des factures"""
        try:
            return pd.read_excel(self.factures_file)
        except FileNotFoundError:
            return pd.DataFrame()
    
    def ajouter_client(self, code_client, nom, contact, ifu):
        """Ajouter un nouveau client"""
        df_clients = self.charger_clients()
        
        # Vérifier si le code client existe déjà
        if code_client in df_clients['code_client'].values:
            return False, "Ce code client existe déjà"
        
        # Vérifier la longueur de l'IFU
        if len(ifu) != 13:
            return False, "L'IFU doit contenir exactement 13 caractères"
        
        # Ajouter le nouveau client
        nouveau_client = {
            'code_client': code_client,
            'nom': nom,
            'contact': contact,
            'IFU': ifu
        }
        
        df_clients = pd.concat([df_clients, pd.DataFrame([nouveau_client])], ignore_index=True)
        df_clients.to_excel(self.clients_file, index=False)
        
        return True, "Client ajouté avec succès"
    
    def ajouter_produit(self, code_produit, libelle, prix_unitaire):
        """Ajouter un nouveau produit"""
        df_produits = self.charger_produits()
        
        # Vérifier si le code produit existe déjà
        if code_produit in df_produits['code_produit'].values:
            return False, "Ce code produit existe déjà"
        
        # Vérifier la longueur du code produit
        if len(code_produit) != 6:
            return False, "Le code produit doit contenir exactement 6 caractères"
        
        # Vérifier le prix
        try:
            prix = float(prix_unitaire)
            if prix <= 0:
                return False, "Le prix unitaire doit être positif"
        except ValueError:
            return False, "Le prix unitaire doit être un nombre"
        
        # Ajouter le nouveau produit
        nouveau_produit = {
            'code_produit': code_produit,
            'libelle': libelle,
            'prix_unitaire': prix
        }
        
        df_produits = pd.concat([df_produits, pd.DataFrame([nouveau_produit])], ignore_index=True)
        df_produits.to_excel(self.produits_file, index=False)
        
        return True, "Produit ajouté avec succès"
    
    def obtenir_client(self, code_client):
        """Obtenir les informations d'un client"""
        df_clients = self.charger_clients()
        client = df_clients[df_clients['code_client'] == code_client]
        
        if client.empty:
            return None
        
        return client.iloc[0].to_dict()
    
    def obtenir_produit(self, code_produit):
        """Obtenir les informations d'un produit"""
        df_produits = self.charger_produits()
        produit = df_produits[df_produits['code_produit'] == code_produit]
        
        if produit.empty:
            return None
        
        return produit.iloc[0].to_dict()
    
    def obtenir_carte_client(self, code_client):
        """Obtenir la carte de réduction d'un client"""
        df_cartes = self.charger_cartes()
        carte = df_cartes[df_cartes['code_client'] == code_client]
        
        if carte.empty:
            return None
        
        return carte.iloc[0].to_dict()
    
    def creer_carte_reduction(self, code_client, total_facture):
        """Créer une carte de réduction basée sur le montant de la facture"""
        df_cartes = self.charger_cartes()
        
        # Vérifier si le client a déjà une carte
        if code_client in df_cartes['code_client'].values:
            return None
        
        # Définir les plages de réduction
        if total_facture >= 10000:
            taux_reduction = 15
        elif total_facture >= 5000:
            taux_reduction = 10
        elif total_facture >= 2000:
            taux_reduction = 5
        else:
            return None  # Pas de carte pour les petites factures
        
        # Générer un numéro de carte unique
        numero_carte = f"CARTE{len(df_cartes) + 1:04d}"
        
        # Ajouter la nouvelle carte
        nouvelle_carte = {
            'numero_carte': numero_carte,
            'code_client': code_client,
            'taux_reduction': taux_reduction
        }
        
        df_cartes = pd.concat([df_cartes, pd.DataFrame([nouvelle_carte])], ignore_index=True)
        df_cartes.to_excel(self.cartes_file, index=False)
        
        return nouvelle_carte
    
    def enregistrer_facture(self, numero_facture, code_client, total_ht, remise, total_ht_remise, tva, total_ttc):
        """Enregistrer une nouvelle facture"""
        df_factures = self.charger_factures()
        
        nouvelle_facture = pd.DataFrame([{
            'numero_facture': numero_facture,
            'code_client': code_client,
            'date_facture': datetime.now().strftime('%Y-%m-%d'),
            'total_ht': total_ht,
            'remise': remise,
            'total_ht_remise': total_ht_remise,
            'tva': tva,
            'total_ttc': total_ttc
        }])
        
        df_factures = pd.concat([df_factures, nouvelle_facture], ignore_index=True)
        df_factures.to_excel(self.factures_file, index=False)
    
    def obtenir_prochain_numero_facture(self):
        """Obtenir le prochain numéro de facture"""
        df_factures = self.charger_factures()
        
        if df_factures.empty:
            return "FACT001"
        
        # Extraire les numéros existants
        numeros_existants = df_factures['numero_facture'].tolist()
        
        # Trouver le prochain numéro
        for i in range(1, 1000):
            numero_candidat = f"FACT{i:03d}"
            if numero_candidat not in numeros_existants:
                return numero_candidat
        
        return f"FACT{len(numeros_existants) + 1:03d}"
    
    def obtenir_statistiques_ventes(self):
        """Obtenir des statistiques sur les ventes"""
        df_factures = self.charger_factures()
        df_produits = self.charger_produits()
        
        if df_factures.empty:
            return {
                'total_factures': 0,
                'chiffre_affaires_total': 0,
                'moyenne_facture': 0,
                'facture_plus_elevee': 0
            }
        
        stats = {
            'total_factures': len(df_factures),
            'chiffre_affaires_total': df_factures['total_ttc'].sum(),
            'moyenne_facture': df_factures['total_ttc'].mean(),
            'facture_plus_elevee': df_factures['total_ttc'].max()
        }
        
        return stats 