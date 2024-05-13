import itertools
import time
import csv
import random

TIME_LIMIT = 150

def read_instance(filename):
    with open(filename, 'r') as f:
        # Lire le nombre de créneaux
        
        nb_creneaux = int(f.readline().strip()[:3])
        

        # Lire les créneaux et les stocker dans une liste de dictionnaires
        creneaux = []
        for i in range(nb_creneaux):
            ligne = f.readline().strip().split(';')
            creneau = {
                'id': ligne[0],
                'plage_horaire': ligne[1],
                'type': ligne[2],
                'coefficient': int(ligne[3])
            }
            creneaux.append(creneau)

        # Lire les bénévoles et les stocker dans une liste de dictionnaires
        nb_benevoles = int(f.readline().strip()[:3])
        benevoles = []
        for i in range(nb_benevoles):
            ligne = f.readline().strip().split(';')
            benevole = {
                'id': ligne[0],
                'choix_mission1': ligne[1],
                'choix_mission2': ligne[2],
                'choix_mission3': ligne[3],
                'choix_equipier1': ligne[4],
                'choix_equipier2': ligne[5]
            }
            benevoles.append(benevole)

        # Retourner les données lues
        return {
            'creneaux': creneaux,
            'benevoles': benevoles
        }


def eval_solution(solution, instance):
    # Initialiser la valeur de l'objectif à 0
    valeur_objectif = 0

    # Parcourir la solution et ajouter les coefficients de priorité et de préférence
    for creneau_id, benevoles in solution.items():
        creneau = next((c for c in instance['creneaux'] if c['id'] == creneau_id), None)
        if creneau is None:
            # Gérer le cas où le créneau n'a pas été trouvé
            continue
        # Ajouter le coefficient de priorité du créneau à la valeur de l'objectif
        valeur_objectif += creneau['coefficient']

        # Ajouter les coefficients de préférence des bénévoles pour leurs affectations
        for benevole_id in benevoles:
            benevole = next((b for b in instance['benevoles'] if b['id'] == benevole_id), None)
            if benevole is None:
                # Gérer le cas où le bénévole n'a pas été trouvé
                continue
            if benevole['choix_mission1'] == creneau['type']:
                valeur_objectif += 3
            elif benevole['choix_mission2'] == creneau['type']:
                valeur_objectif += 2
            elif benevole['choix_mission3'] == creneau['type']:
                valeur_objectif += 1
            elif benevole['choix_mission1'] == "nochoice":
                valeur_objectif += 3
            elif benevole['choix_mission2'] == "nochoice":
                valeur_objectif += 2
            elif benevole['choix_mission3'] == "nochoice":
                valeur_objectif += 1

            # Ajouter les coefficients de préférence des bénévoles pour leurs équipiers
            if benevoles[0] == benevole_id and benevole['choix_equipier1'] == benevoles[1]:
                valeur_objectif += 200
            elif benevoles[0] == benevole_id and benevole['choix_equipier2'] == benevoles[1]:
                valeur_objectif += 100
            elif benevoles[1] == benevole_id and benevole['choix_equipier1'] == benevoles[0]:
                valeur_objectif += 200
            elif benevoles[1] == benevole_id and benevole['choix_equipier2'] == benevoles[0]:
                valeur_objectif += 100
            elif benevoles[0] == benevole_id and benevole['choix_equipier1'] == "nochoice":
                valeur_objectif += 200
            elif benevoles[0] == benevole_id and benevole['choix_equipier2'] == "nochoice":
                valeur_objectif += 100
            elif benevoles[1] == benevole_id and benevole['choix_equipier1'] == "nochoice":
                valeur_objectif += 200
            elif benevoles[1] == benevole_id and benevole['choix_equipier2'] == "nochoice":
                valeur_objectif += 100
            

    # Retourner la valeur de l'objectif
    return valeur_objectif


def backtrack(instance, creneaux, benevoles, solution, meilleure_solution, start_time):
    # Vérifier si le temps limite est atteint
    if time.time() - start_time > TIME_LIMIT:
        return
    
    # Cas de base : tous les créneaux ont été affectés
    if len(benevoles) == 0 or len(creneaux) == 0:
        # Évaluer la solution courante et mettre à jour la meilleure solution
        valeur = eval_solution(solution, instance)
        if valeur > eval_solution(meilleure_solution, instance):
            meilleure_solution.clear()
            meilleure_solution.update(solution)
            print(f"Meilleure solution : {meilleure_solution}")
            print(f"Valeur : {valeur}")
        return

    # Sélectionner le créneau actuel
    creneau = creneaux[0]

    # Générer tous les binômes de bénévoles compatibles avec le créneau actuel
    # Assuming each dictionary has an 'id' key
    id_list = [b['id'] for b in benevoles]
    binomes = [b for b in itertools.combinations(id_list, 2)]
    # On mélange les binômes pour éviter de toujours commencer par l'ordre croissant quelque soit l'instance 
    #(le hasard nous fait peut etre commencer par une meilleure solution)
    binomes = random.sample(binomes, len(binomes))
    
    

    

    # Parcourir tous les binômes compatibles
    for binome in binomes:
        # Affecter le binôme au créneau actuel et mettre à jour la solution
        solution[creneau['id']] = binome
        benevoles_copy = benevoles.copy()
        benevoles_copy = [b for b in benevoles_copy if b['id'] != binome[0]]
        benevoles_copy = [b for b in benevoles_copy if b['id'] != binome[1]]
        

        # Appeler récursivement la fonction backtrack sur le créneau suivant
        backtrack(instance, creneaux[1:], benevoles_copy, solution, meilleure_solution, start_time)
        

        # Annuler l'affectation du binôme et restaurer la solution
        del solution[creneau['id']]
        benevoles_copy.append(binome[0])
        benevoles_copy.append(binome[1])

def resolution_backtracking(instance, numero_instance):
    # Initialiser le temps de départ
    start_time = time.time()
    # Initialiser une solution vide et un ensemble de bénévoles non affectés
    solution = {}
    benevoles = instance['benevoles']

    # Trier les créneaux par ordre décroissant de coefficient de priorité
    creneaux = sorted(instance['creneaux'], key=lambda c: c['coefficient'], reverse=True)

    # Appeler la fonction backtrack sur le premier créneau
    meilleure_solution = {}
    print(meilleure_solution)
    backtrack(instance, creneaux, benevoles, solution, meilleure_solution, start_time)

    # Retourner la meilleure solution trouvée
    return write_solution(meilleure_solution, instance, f'solutionPb{numero_instance}_1.txt')

def write_solution(solution, instance, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Creneau', 'Type', 'Equipier1', 'Equipier2'])
        for creneau, equipiers in solution.items():
            type_creneau  = next((c['type'] for c in instance['creneaux'] if c['id'] == creneau), None)
            writer.writerow([creneau, type_creneau, equipiers[0], equipiers[1]])
        writer.writerow(['Valeur objectif', eval_solution(solution, instance)])

# Lire l'instance à partir d'un fichier

for i in range(0,9):
    instance = read_instance(f'Pb{i}.txt')
    # Résoudre l'instance avec le backtracking
    solution = resolution_backtracking(instance, i)
    print(solution)
    i += 1


