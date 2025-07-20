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
        """Convertit un nombre entier en lettres (français, jusqu'à plusieurs milliards)"""
        if nombre == 0:
            return "zéro franc CFA"
        unite = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
        dizaine = ["", "dix", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]
        def convert_hundred(n):
            if n == 0:
                return ""
            elif n < 10:
                return unite[n]
            elif n < 20:
                return ["dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"][n-10]
            elif n < 100:
                d, u = divmod(n, 10)
                sep = " et " if u == 1 and d not in [8] else "-" if u > 0 else ""
                if d == 7 or d == 9:
                    return dizaine[d-1] + sep + convert_hundred(10+u)
                else:
                    return dizaine[d] + (sep + unite[u] if u else "")
            else:
                c, r = divmod(n, 100)
                cent = "cent" if c == 1 else unite[c] + " cent"
                if r == 0:
                    return cent + ("s" if c > 1 else "")
                else:
                    return cent + " " + convert_hundred(r)
        def group(n, singular, plural):
            if n == 0:
                return ""
            elif n == 1:
                return singular
            else:
                return convert_number(n) + " " + plural
        def convert_number(n):
            if n < 1000:
                return convert_hundred(n)
            elif n < 1000000:
                mille, r = divmod(n, 1000)
                prefix = "mille" if mille == 1 else convert_hundred(mille) + " mille"
                if r == 0:
                    return prefix
                else:
                    return prefix + " " + convert_hundred(r) if r < 1000 else prefix + " " + convert_number(r)
            elif n < 1000000000:
                million, r = divmod(n, 1000000)
                prefix = group(million, "un million", "millions")
                if r == 0:
                    return prefix
                else:
                    return prefix + " " + convert_number(r)
            else:
                milliard, r = divmod(n, 1000000000)
                prefix = group(milliard, "un milliard", "milliards")
                if r == 0:
                    return prefix
                else:
                    return prefix + " " + convert_number(r)
        lettres = convert_number(int(nombre)).strip()
        if not lettres.endswith("francs CFA"):
            lettres += " francs CFA"
        return lettres
    
    def generer_facture(self, numero_facture, client_info, produits_factures, total_ht, remise, total_ht_remise, tva, total_ttc, nom_groupe="Groupe d'Étudiants"):
        """Générer une facture en PDF selon le format demandé"""
        import copy
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
        # Ajout de lignes vides pour l'esthétique si moins de 3 produits
        while len(table_data) < 4:
            table_data.append(['', '', '', '', '', ''])
        # Tableau des totaux (collé à droite, même largeur que le tableau des produits)
        totaux_data = [
            ['', '', '', '', 'Total HT', f"{total_ht:.2f}"],
            ['', '', '', '', 'Remise', f"{remise:.2f}"],
            ['', '', '', '', 'THT remise', f"{total_ht_remise:.2f}"],
            ['', '', '', '', 'TVA (18%)', f"{tva:.2f}"],
            ['', '', '', '', 'Total TTC', f"{total_ttc:.2f}"]
        ]
        # Fusionner les deux tableaux pour avoir le rendu du modèle
        full_table_data = copy.deepcopy(table_data) + totaux_data
        table = Table(full_table_data, colWidths=[0.7*inch, 1.3*inch, 2.7*inch, 1*inch, 0.8*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Totaux à droite
            ('ALIGN', (4, len(table_data)), (4, -1), 'RIGHT'),
            ('ALIGN', (5, len(table_data)), (5, -1), 'RIGHT'),
            ('FONTNAME', (4, len(table_data)), (4, -1), 'Helvetica-Bold'),
            ('FONTNAME', (5, len(table_data)), (5, -1), 'Helvetica'),
            ('BACKGROUND', (4, -1), (5, -1), colors.lightgrey),
            ('FONTNAME', (4, -1), (5, -1), 'Helvetica-Bold'),
        ]))
        story.append(table)
        story.append(Spacer(1, 40))
        # Bas de page : "Arrêtée, la présente facture à la somme de : [Total TTC en lettres]" en italique
        total_en_lettres = self.nombre_en_lettres(int(total_ttc))
        story.append(Paragraph(
            f"<i>Arrêtée, la présente facture à la somme de : {total_en_lettres}</i>", 
            self.styles['TotalStyle']
        ))
        # Générer le PDF
        doc.build(story)
        return filename 

    def generer_carte_reduction(self, client_info, carte_info, nom_groupe="Groupe d'Étudiants"):
        """Générer une carte de réduction en PDF pour le client"""
        from reportlab.pdfgen import canvas
        from datetime import datetime
        # Format carte bancaire : 85.6mm x 53.98mm en points (1mm = 2.83465 points)
        width, height = 85.6 * 2.83465, 53.98 * 2.83465
        # Créer le dossier cartes s'il n'existe pas
        if not os.path.exists('cartes'):
            os.makedirs('cartes')
        filename = f"cartes/Carte_{carte_info['numero_carte']}.pdf"
        c = canvas.Canvas(filename, pagesize=(width, height))
        # Fond
        c.setFillColorRGB(0.95, 0.95, 1)
        c.rect(0, 0, width, height, fill=1, stroke=0)
        # Titre
        c.setFont("Helvetica-Bold", 12)
        c.setFillColorRGB(0.2, 0.2, 0.5)
        c.drawCentredString(width/2, height-20, f"{nom_groupe}")
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(width/2, height-35, "CARTE DE RÉDUCTION CLIENT")
        # Infos client
        c.setFont("Helvetica", 8)
        c.drawString(10, height-55, f"Nom : {client_info['nom']}")
        c.drawString(10, height-65, f"Code client : {client_info['code_client']}")
        c.drawString(10, height-75, f"Numéro carte : {carte_info['numero_carte']}")
        c.drawString(10, height-85, f"Taux de réduction : {carte_info['taux_reduction']}%")
        c.drawString(10, height-95, f"Date : {datetime.now().strftime('%d/%m/%Y')}")
        # Message
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawString(10, 10, "Valable sur toutes les prochaines factures, non cumulable.")
        c.save()
        return filename 