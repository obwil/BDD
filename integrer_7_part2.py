tous = list(range(1,13))

# 226 - Concours d'anecdotes
update_activite(226,
    "Jeu d\u2019expression orale o\u00f9 les enfants racontent tour \u00e0 tour une courte anecdote vraie ou invent\u00e9e. Le groupe vote pour d\u00e9cider si l\u2019histoire est vraie ou fausse, puis le conteur r\u00e9v\u00e8le la r\u00e9ponse. Le conteur gagne s\u2019il a r\u00e9ussi \u00e0 tromper la majorit\u00e9, sinon c\u2019est le public qui gagne.",
    "S\u2019exprimer en public et d\u00e9velopper la coh\u00e9sion de groupe \u00e0 travers un jeu de devinette narrative.",
    'grand groupe', 40, tous, [126, 127], [17])

# 293 - Jeu des 10s
update_activite(293,
    "Jeu coop\u00e9ratif o\u00f9 les enfants doivent, sans se parler ni se d\u00e9placer, faire en sorte qu\u2019exactement X d\u2019entre eux l\u00e8vent la main en 10 secondes. Les d\u00e9fis se complexifient progressivement (par genre, par zone, par caract\u00e9ristique visible).",
    "D\u00e9velopper la coop\u00e9ration silencieuse, la strat\u00e9gie collective et la gestion de la frustration.",
    'grand groupe', 30, tous, [125, 126], [16])

# 486 - Histoire loopstation (thematiques deja en BDD)
update_activite(486,
    "L\u2019animateur construit en direct une composition musicale par enregistrement en boucle (loopstation), \u00e0 partir des sons produits par les enfants (voix, percussions, instruments). Une histoire est racont\u00e9e et les enfants ajoutent des sons correspondant aux actions. Des jeux de danse et de statues s\u2019int\u00e8grent \u00e0 la s\u00e9ance.",
    "Cr\u00e9er collectivement une ambiance musicale et d\u00e9velopper la cr\u00e9ativit\u00e9, l\u2019\u00e9coute et l\u2019expression corporelle.",
    'grand groupe', 45, tous, [], [15, 17])

# 259 - Qu'est-ce qu'un etre vivant (thematique 13 deja en BDD, on ajoute 14,15,16,17)
update_activite(259,
    "En ext\u00e9rieur, face \u00e0 un arbre, un insecte et un animal, les enfants cherchent les points communs entre ces \u00eatres vivants et eux-m\u00eames. R\u00e9partis en 5 groupes, ils miment chacun une des 5 caract\u00e9ristiques du vivant (na\u00eetre, grandir, se nourrir, se reproduire, mourir), puis les d\u00e9taillent collectivement.",
    "Comprendre et m\u00e9moriser les 5 caract\u00e9ristiques communes \u00e0 tous les \u00eatres vivants.",
    'petit groupe', 15, tous, [14, 15, 16, 17], [4, 6])

# 921 - Balade musicale contee (thematiques deja en BDD)
update_activite(921,
    "Les enfants partent seuls, l\u2019un apr\u00e8s l\u2019autre, explorer un chemin en for\u00eat jusqu\u2019\u00e0 un point de rendez-vous. L\u2019animateur raconte ensuite l\u2019histoire invisible de la for\u00eat (animaux cach\u00e9s, faune du sol) et propose des activit\u00e9s d\u2019\u00e9coute collective. Une composition musicale est construite \u00e0 la loopstation \u00e0 partir des sons de la for\u00eat et des enfants.",
    "Cr\u00e9er un lien sensoriel et \u00e9motionnel avec la for\u00eat par l\u2019exploration autonome et l\u2019\u00e9coute musicale collective.",
    'grand groupe', 30, tous, [], [1, 2])

# 1054 - Redonner un visage a l'arbre
update_activite(1054,
    "En for\u00eat, les enfants observent les formes \u00e9vocatrices de visages sur les troncs d\u2019arbres, puis cr\u00e9ent avec de l\u2019argile et des \u00e9l\u00e9ments naturels le visage d\u2019un arbre. Ils lui imaginent ensuite une histoire \u00e0 raconter.",
    "D\u00e9velopper le lien affectif avec les arbres en combinant observation, cr\u00e9ation plastique et r\u00e9cit imaginaire.",
    'individuel', 90, [3,4,5,6,7,8,9,10,11], [122, 54], [15, 5])

# 242 - Sexualite des fleurs
update_activite(242,
    "Les enfants r\u00e9coltent des fleurs ou les observent en classe, les dessinent dans leur \u00e9tat entier puis d\u00e9cortiqu\u00e9. Par groupes, ils comparent les diff\u00e9rences entre fleurs m\u00e2les et femelles et se questionnent sur la reproduction des plantes. Des loupes permettent l\u2019observation fine.",
    "Observer et comprendre les diff\u00e9rences morphologiques entre fleurs et d\u00e9couvrir les m\u00e9canismes de reproduction v\u00e9g\u00e9tale.",
    'petit groupe', 45, [4,5,6,7,8], [17, 54], [3, 6])

conn.commit()
conn.close()
print("Termine.")
