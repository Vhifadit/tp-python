#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import webbrowser
from data_manager import DataManager
from facture_generator import FactureGenerator

class ApplicationFacturation:
    def __init__(self):
        self.data_manager = DataManager()
        self.facture_generator = FactureGenerator()
        
    def afficher_menu_principal(self):
        """Afficher le menu principal"""
        print("\n" + "="*60)
        print("           APPLICATION DE FACTURATION ET STATISTIQUES")
        print("="*60)
        print("1. Consulter un fichier")
        print("2. Générer une facture")
        print("3. Ajouter un produit")
        print("4. Statistiques de ventes")
        print("5. Quitter l'application")
        print("="*60)
    
    def afficher_menu_consultation(self):
        """Afficher le menu de consultation"""
        print("\n" + "-"*40)
        print("           CONSULTATION DES FICHIERS")
        print("-"*40)
        print("a. Afficher les clients")
        print("b. Afficher les produits")
        print("c. Afficher les cartes de réduction")
        print("d. Retour au menu principal")
        print("-"*40)
    
    def consulter_fichier(self):
        """Gérer la consultation des fichiers"""
        while True:
            self.afficher_menu_consultation()
            choix = input("Votre choix (a/b/c/d) : ").lower()
            
            if choix == 'a':
                self.afficher_clients()
            elif choix == 'b':
                self.afficher_produits()
            elif choix == 'c':
                self.afficher_cartes_reduction()
            elif choix == 'd':
                break
            else:
                print("Choix invalide. Veuillez réessayer.")
    
    def afficher_clients(self):
        """Afficher la liste des clients"""
        print("\n" + "="*80)
        print("                                    CLIENTS")
        print("="*80)
        
        df_clients = self.data_manager.charger_clients()
        
        if df_clients.empty:
            print("Aucun client trouvé.")
            return
        
        print(f"{'Code':<10} {'Nom':<30} {'Contact':<25} {'IFU':<15}")
        print("-" * 80)
        
        for _, client in df_clients.iterrows():
            print(f"{client['code_client']:<10} {client['nom']:<30} {client['contact']:<25} {client['IFU']:<15}")
        
        print("="*80)
        input("Appuyez sur Entrée pour continuer...")
    
    def afficher_produits(self):
        """Afficher la liste des produits"""
        print("\n" + "="*70)
        print("                                PRODUITS")
        print("="*70)
        
        df_produits = self.data_manager.charger_produits()
        
        if df_produits.empty:
            print("Aucun produit trouvé.")
            return
        
        print(f"{'Code':<10} {'Libellé':<35} {'Prix Unitaire':<15}")
        print("-" * 70)
        
        for _, produit in df_produits.iterrows():
            print(f"{produit['code_produit']:<10} {produit['libelle']:<35} {produit['prix_unitaire']:<15.2f}")
        
        print("="*70)
        input("Appuyez sur Entrée pour continuer...")
    
    def afficher_cartes_reduction(self):
        """Afficher la liste des cartes de réduction"""
        print("\n" + "="*60)
        print("                        CARTES DE RÉDUCTION")
        print("="*60)
        
        df_cartes = self.data_manager.charger_cartes()
        
        if df_cartes.empty:
            print("Aucune carte de réduction trouvée.")
            return
        
        print(f"{'Numéro Carte':<15} {'Code Client':<12} {'Taux Réduction':<15}")
        print("-" * 60)
        
        for _, carte in df_cartes.iterrows():
            print(f"{carte['numero_carte']:<15} {carte['code_client']:<12} {carte['taux_reduction']:<15}%")
        
        print("="*60)
        input("Appuyez sur Entrée pour continuer...")
    
    def generer_facture(self):
        """Générer une nouvelle facture"""
        print("\n" + "="*50)
        print("           GÉNÉRATION DE FACTURE")
        print("="*50)
        
        # Demander si nouveau client ou client existant
        print("1. Client existant")
        print("2. Nouveau client")
        choix_client = input("Votre choix (1/2) : ")
        
        if choix_client == "2":
            # Créer un nouveau client
            client_info = self.creer_nouveau_client()
            if not client_info:
                return
        else:
            # Sélectionner un client existant
            client_info = self.selectionner_client()
            if not client_info:
                return
        
        # Saisir les produits
        produits_factures = self.saisir_produits()
        if not produits_factures:
            return
        
        # Calculer les totaux
        total_ht = sum(prod['total_ht'] for prod in produits_factures)
        
        # Vérifier s'il y a une carte de réduction
        carte_client = self.data_manager.obtenir_carte_client(client_info['code_client'])
        remise = 0
        
        if carte_client:
            remise = total_ht * (carte_client['taux_reduction'] / 100)
            print(f"\nCarte de réduction appliquée : {carte_client['taux_reduction']}%")
            print(f"Montant de la remise : {remise:.2f} FCFA")
        
        total_ht_remise = total_ht - remise
        tva = total_ht_remise * 0.18
        total_ttc = total_ht_remise + tva
        
        # Afficher le récapitulatif
        self.afficher_recapitulatif_facture(client_info, produits_factures, total_ht, remise, total_ht_remise, tva, total_ttc)
        
        # Générer la facture automatiquement
        numero_facture = self.data_manager.obtenir_prochain_numero_facture()
        
        try:
            filename = self.facture_generator.generer_facture(
                numero_facture, client_info, produits_factures,
                total_ht, remise, total_ht_remise, tva, total_ttc
            )
            
            # Enregistrer la facture dans la base
            self.data_manager.enregistrer_facture(
                numero_facture, client_info['code_client'],
                total_ht, remise, total_ht_remise, tva, total_ttc
            )
            
            # Créer une carte de réduction si nécessaire
            if not carte_client and total_ttc >= 2000:
                nouvelle_carte = self.data_manager.creer_carte_reduction(client_info['code_client'], total_ttc)
                if nouvelle_carte:
                    print(f"\n🎉 Une carte de réduction de {nouvelle_carte['taux_reduction']}% a été créée pour ce client !")
            
            print(f"\n✅ Facture générée avec succès : {filename}")
            
            # Ouvrir le fichier PDF dans le navigateur web
            try:
                webbrowser.open(f'file:///{os.path.abspath(filename)}')
                print("🌐 Ouverture de la facture dans le navigateur...")
            except Exception as e:
                print(f"⚠️ Impossible d'ouvrir automatiquement la facture : {e}")
                print(f"📁 Vous pouvez l'ouvrir manuellement : {filename}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération de la facture : {e}")
    
    def creer_nouveau_client(self):
        """Créer un nouveau client"""
        print("\n--- Création d'un nouveau client ---")
        
        code_client = input("Code client : ").strip()
        nom = input("Nom : ").strip()
        contact = input("Contact (email/téléphone) : ").strip()
        ifu = input("IFU (13 caractères) : ").strip()
        
        if not all([code_client, nom, contact, ifu]):
            print("❌ Tous les champs sont obligatoires.")
            return None
        
        success, message = self.data_manager.ajouter_client(code_client, nom, contact, ifu)
        
        if success:
            print(f"✅ {message}")
            return self.data_manager.obtenir_client(code_client)
        else:
            print(f"❌ {message}")
            return None
    
    def selectionner_client(self):
        """Sélectionner un client existant"""
        df_clients = self.data_manager.charger_clients()
        
        if df_clients.empty:
            print("❌ Aucun client disponible.")
            return None
        
        print("\n--- Clients disponibles ---")
        for i, (_, client) in enumerate(df_clients.iterrows(), 1):
            print(f"{i}. {client['code_client']} - {client['nom']}")
        
        try:
            choix = int(input("\nChoisissez le numéro du client : ")) - 1
            if 0 <= choix < len(df_clients):
                return df_clients.iloc[choix].to_dict()
            else:
                print("❌ Choix invalide.")
                return None
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
            return None
    
    def saisir_produits(self):
        """Saisir les produits à facturer"""
        produits_factures = []
        df_produits = self.data_manager.charger_produits()
        
        if df_produits.empty:
            print("❌ Aucun produit disponible.")
            return None
        
        print("\n--- Produits disponibles ---")
        for _, produit in df_produits.iterrows():
            print(f"{produit['code_produit']} - {produit['libelle']} - {produit['prix_unitaire']:.2f} FCFA")
        
        print("\n--- Saisie des produits ---")
        
        while True:
            code_produit = input("\nCode produit : ").strip().upper()
            
            produit = self.data_manager.obtenir_produit(code_produit)
            if not produit:
                print("❌ Produit non trouvé.")
                continue
            
            # Boucle pour la saisie de la quantité
            while True:
                try:
                    quantite = int(input(f"Quantité pour {produit['libelle']} : "))
                    if quantite <= 0:
                        print("❌ La quantité doit être positive.")
                        continue
                    break  # Sortir de la boucle si la quantité est valide
                except ValueError:
                    print("❌ Veuillez entrer un nombre valide.")
                    continue  # Redemander la quantité pour le même produit
            
            total_ht = produit['prix_unitaire'] * quantite
            
            produit_facture = {
                'code_produit': produit['code_produit'],
                'libelle': produit['libelle'],
                'prix_unitaire': produit['prix_unitaire'],
                'quantite': quantite,
                'total_ht': total_ht
            }
            
            produits_factures.append(produit_facture)
            print(f"✅ Ajouté : {quantite}x {produit['libelle']} = {total_ht:.2f} FCFA")
            print(f"Produits ajoutés : {len(produits_factures)}")
            
            # Demander si l'utilisateur veut continuer
            while True:
                continuer = input("\nVoulez-vous ajouter un autre produit ? (o/n) : ").lower().strip()
                if continuer in ['o', 'oui', 'y', 'yes']:
                    break
                elif continuer in ['n', 'non', 'no']:
                    if len(produits_factures) == 0:
                        print("❌ Vous devez ajouter au moins un produit.")
                        continue
                    return produits_factures
                else:
                    print("❌ Veuillez répondre par 'o' (oui) ou 'n' (non).")
        
        return produits_factures
    
    def afficher_recapitulatif_facture(self, client_info, produits_factures, total_ht, remise, total_ht_remise, tva, total_ttc):
        """Afficher le récapitulatif de la facture"""
        print("\n" + "="*60)
        print("                    RÉCAPITULATIF DE LA FACTURE")
        print("="*60)
        
        print(f"Client : {client_info['nom']} ({client_info['code_client']})")
        print(f"Contact : {client_info['contact']}")
        print("-" * 60)
        
        print(f"{'Produit':<30} {'Qté':<5} {'P.U.':<10} {'Total HT':<12}")
        print("-" * 60)
        
        for produit in produits_factures:
            print(f"{produit['libelle']:<30} {produit['quantite']:<5} {produit['prix_unitaire']:<10.2f} {produit['total_ht']:<12.2f}")
        
        print("-" * 60)
        print(f"{'Total HT':<45} {total_ht:<12.2f}")
        print(f"{'Remise':<45} {remise:<12.2f}")
        print(f"{'THT remise':<45} {total_ht_remise:<12.2f}")
        print(f"{'TVA (18%)':<45} {tva:<12.2f}")
        print(f"{'Total TTC':<45} {total_ttc:<12.2f}")
        print("="*60)
    
    def ajouter_produit(self):
        """Ajouter un nouveau produit"""
        print("\n" + "="*50)
        print("           AJOUT D'UN NOUVEAU PRODUIT")
        print("="*50)
        
        code_produit = input("Code produit (6 caractères) : ").strip().upper()
        libelle = input("Libellé : ").strip()
        prix_unitaire = input("Prix unitaire : ").strip()
        
        if not all([code_produit, libelle, prix_unitaire]):
            print("❌ Tous les champs sont obligatoires.")
            return
        
        success, message = self.data_manager.ajouter_produit(code_produit, libelle, prix_unitaire)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    def afficher_statistiques(self):
        """Afficher les statistiques de ventes"""
        print("\n" + "="*50)
        print("           STATISTIQUES DE VENTES")
        print("="*50)
        
        stats = self.data_manager.obtenir_statistiques_ventes()
        
        if stats['total_factures'] == 0:
            print("Aucune facture générée pour le moment.")
            return
        
        print(f"Nombre total de factures : {stats['total_factures']}")
        print(f"Chiffre d'affaires total : {stats['chiffre_affaires_total']:.2f} FCFA")
        print(f"Moyenne par facture : {stats['moyenne_facture']:.2f} FCFA")
        print(f"Facture la plus élevée : {stats['facture_plus_elevee']:.2f} FCFA")
        
        # Statistiques par client
        df_factures = self.data_manager.charger_factures()
        df_clients = self.data_manager.charger_clients()
        
        if not df_factures.empty and not df_clients.empty:
            print("\n--- Chiffre d'affaires par client ---")
            for _, client in df_clients.iterrows():
                client_factures = df_factures[df_factures['code_client'] == client['code_client']]
                if not client_factures.empty:
                    total_client = client_factures['total_ttc'].sum()
                    print(f"{client['nom']} : {total_client:.2f} FCFA")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def demarrer(self):
        """Démarrer l'application"""
        print("🚀 Démarrage de l'Application de Facturation...")
        
        # Vérifier que les fichiers de données existent
        if not os.path.exists('data'):
            print("❌ Le dossier 'data' est introuvable. Merci de placer vos fichiers Excel dans ce dossier.")
            return
        if not os.path.exists(os.path.join('data', 'Clients.xlsx')) or not os.path.exists(os.path.join('data', 'Produits.xlsx')):
            print("❌ Les fichiers 'Clients.xlsx' et/ou 'Produits.xlsx' sont manquants dans le dossier 'data'.")
            print("Merci de placer les fichiers fournis par le professeur dans le dossier 'data'.")
            return
        
        while True:
            self.afficher_menu_principal()
            choix = input("Votre choix (1-5) : ")
            
            if choix == '1':
                self.consulter_fichier()
            elif choix == '2':
                self.generer_facture()
            elif choix == '3':
                self.ajouter_produit()
            elif choix == '4':
                self.afficher_statistiques()
            elif choix == '5':
                print("\n👋 Merci d'avoir utilisé l'Application de Facturation !")
                break
            else:
                print("❌ Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    app = ApplicationFacturation()
    app.demarrer() 