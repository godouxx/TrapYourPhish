import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Module pour gérer les images dans Tkinter

# Fonction pour scanner l'email
def scanner_email():
    email = email_entry.get()
    if "@" in email:  # Vérifie si l'email contient un '@'
        messagebox.showinfo("Résultat", f"L'e-mail '{email}' a été scanné avec succès !")
    else:
        messagebox.showerror("Erreur", "Veuillez entrer une adresse e-mail valide.")

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Scanner d'E-mail")
fenetre.geometry("400x300")  # Taille de la fenêtre

# Charger le logo
logo_path = "logo startup.png"  # Chemin vers ton logo
try:
    logo_image = Image.open(logo_path)
    logo_image = logo_image.resize((100, 100), Image.ANTIALIAS)  # Redimensionner l'image si nécessaire
    logo_photo = ImageTk.PhotoImage(logo_image)
    
    # Afficher le logo dans la fenêtre
    logo_label = tk.Label(fenetre, image=logo_photo)
    logo_label.pack(pady=10)
except Exception as e:
    print(f"Erreur lors du chargement du logo : {e}")

# Ajout du label pour l'email
email_label = tk.Label(fenetre, text="Entrez votre e-mail :", font=("Calibri", 12))
email_label.pack(pady=10)

# Champ de saisie pour l'email
email_entry = tk.Entry(fenetre, width=30, font=("Calibri", 12))
email_entry.pack(pady=10)

# Bouton pour lancer le scan
scan_button = tk.Button(fenetre, text="Scanner", command=scanner_email, font=("Calibri", 12), bg="blue", fg="white")
scan_button.pack(pady=10)

# Boucle principale de la fenêtre
fenetre.mainloop()

