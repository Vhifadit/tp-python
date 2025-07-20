from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
from datetime import datetime

class FactureGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configuration des styles personnalisés"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            spaceBefore=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='HeaderInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ClientInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='TotalStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            alignment=TA_RIGHT
        ))
    
    def nombre_en_lettres(self, nombre):
        """Convertir un nombre en lettres (version simplifiée)"""
        unites = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
        dizaines = ["", "", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]
        
        if nombre == 0:
            return "zéro"
        
        if nombre < 10:
            return unites[nombre]
        elif nombre < 20:
            teens = ["dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
            return teens[nombre - 10]
        elif nombre < 100:
            if nombre % 10 == 0:
                return dizaines[nombre // 10]
            elif nombre // 10 == 7:
                return "soixante-" + unites[nombre % 10 + 10]
            elif nombre // 10 == 9:
                return "quatre-vingt-" + unites[nombre % 10 + 10]
            else:
                return dizaines[nombre // 10] + "-" + unites[nombre % 10]
        else:
            # Version simplifiée pour les grands nombres
            return f"{nombre} francs CFA"
    
    def generer_facture(self, numero_facture, client_info, produits_factures, total_ht, remise, total_ht_remise, tva, total_ttc, nom_groupe="Groupe d'Étudiants"):
        """Générer une facture en PDF selon le format demandé"""
        
        # Créer le dossier factures s'il n'existe pas
        if not os.path.exists('factures'):
            os.makedirs('factures')
        
        filename = f"factures/Facture_{numero_facture}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        story = []
        
        # En-tête : nom du groupe à gauche, date à droite
        header_data = [
            [Paragraph(f"<b>{nom_groupe}</b>", self.styles['HeaderInfo']), 
             Paragraph(f"Date d'émission : {datetime.now().strftime('%d/%m/%Y')}", self.styles['HeaderInfo'])]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Informations du client
        client_info_data = [
            [Paragraph("<b>INFORMATIONS DU CLIENT</b>", self.styles['ClientInfo'])],
            [Paragraph(f"Code client : {client_info['code_client']}", self.styles['ClientInfo'])],
            [Paragraph(f"Nom : {client_info['nom']}", self.styles['ClientInfo'])],
            [Paragraph(f"Contact : {client_info['contact']}", self.styles['ClientInfo'])],
            [Paragraph(f"IFU : {client_info['IFU']}", self.styles['ClientInfo'])]
        ]
        
        for info in client_info_data:
            story.append(Paragraph(info[0].text, self.styles['ClientInfo']))
        
        story.append(Spacer(1, 30))
        
        # Titre centré : FACTURE n° XXXXXX
        story.append(Paragraph(f"FACTURE n° {numero_facture}", self.styles['CustomTitle']))
        story.append(Spacer(1, 30))
        
        # Tableau des produits avec les colonnes exactes demandées
        table_data = [['N°', 'Code Produit', 'Libellé', 'P.U.', 'Qté', 'Total HT']]
        
        for i, produit in enumerate(produits_factures, 1):
            table_data.append([
                str(i),
                produit['code_produit'],
                produit['libelle'],
                f"{produit['prix_unitaire']:.2f}",
                str(produit['quantite']),
                f"{produit['total_ht']:.2f}"
            ])
        
        # Créer le tableau principal des produits
        table = Table(table_data, colWidths=[0.4*inch, 1.2*inch, 2.8*inch, 1*inch, 0.6*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Tableau des totaux (à droite)
        totaux_data = [
            ['Total HT', f"{total_ht:.2f}"],
            ['Remise', f"{remise:.2f}"],
            ['THT remise', f"{total_ht_remise:.2f}"],
            ['TVA (18%)', f"{tva:.2f}"],
            ['Total TTC', f"{total_ttc:.2f}"]
        ]
        
        totaux_table = Table(totaux_data, colWidths=[2*inch, 1.5*inch])
        totaux_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        # Positionner le tableau des totaux à droite
        totaux_container = Table([[totaux_table]], colWidths=[3.5*inch])
        totaux_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ]))
        
        story.append(totaux_container)
        story.append(Spacer(1, 40))
        
        # Bas de page : "Arrêtée, la présente facture à la somme de : [Total TTC en lettres]"
        total_en_lettres = self.nombre_en_lettres(int(total_ttc))
        story.append(Paragraph(
            f"<b>Arrêtée, la présente facture à la somme de : {total_en_lettres} francs CFA</b>", 
            self.styles['TotalStyle']
        ))
        
        # Générer le PDF
        doc.build(story)
        return filename 