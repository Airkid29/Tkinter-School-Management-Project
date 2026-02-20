from argon2 import PasswordHasher

ph = PasswordHasher()

# Hachage (le sel est géré automatiquement)
hash_mdp = ph.hash("mon_mot_de_passe_secret")

# Vérification
try:
    ph.verify(hash_mdp, "mon_mot_de_passe_secret")
    print("Succès !")
except:
    print("Échec !")
