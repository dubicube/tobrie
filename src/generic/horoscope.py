import random

def generate_horoscope(sign=None):
    zodiac_traits = {
        "Bélier": {"style": "audacieux et fougueux"},
        "Taureau": {"style": "ancré et sensuel"},
        "Gémeaux": {"style": "curieux et vif"},
        "Cancer": {"style": "émotif et protecteur"},
        "Lion": {"style": "rayonnant et dramatique"},
        "Vierge": {"style": "précis et réfléchi"},
        "Balance": {"style": "harmonieux et charmant"},
        "Scorpion": {"style": "intense et mystérieux"},
        "Sagittaire": {"style": "aventurier et optimiste"},
        "Capricorne": {"style": "discipliné et ambitieux"},
        "Verseau": {"style": "excentrique et visionnaire"},
        "Poissons": {"style": "rêveur et intuitif"}
    }

    zodiac_signs = list(zodiac_traits.keys())

    if sign is None:
        sign = random.choice(zodiac_signs)
    elif sign.capitalize() not in zodiac_signs:
        return "Signe du zodiaque invalide."

    sign = sign.capitalize()
    style = zodiac_traits[sign]["style"]

    openings = [
        "Les étoiles s’alignent avec une lenteur presque théâtrale",
        "Une vibration étrange traverse l’univers jusqu’à toi",
        "Le cosmos semble légèrement distrait aujourd’hui",
        "Un courant invisible relie tes pensées aux étoiles",
        "Quelque chose d’inexplicable flotte dans l’air cosmique"
    ]

    love_texts = [
        "En amour, les émotions prennent de l’ampleur. Une discussion anodine pourrait révéler des sentiments cachés. Si tu es en couple, un moment simple peut devenir étonnamment profond. Si tu es célibataire, une rencontre improbable pourrait te faire sourire sans raison logique.",
        "Côté cœur, l’ambiance est douce mais imprévisible. Tu pourrais ressentir un besoin de connexion sincère, ou au contraire, l’envie de te perdre dans tes propres pensées. Dans tous les cas, laisse une place à la spontanéité.",
        "Les énergies affectives sont légèrement chaotiques aujourd’hui. Cela peut créer des étincelles… ou des malentendus. Respire, observe, et rappelle-toi que tout le monde improvise un peu."
    ]

    work_texts = [
        "Au travail, une opportunité discrète pourrait apparaître là où tu ne regardais pas. Ce n’est peut-être pas spectaculaire, mais cela pourrait évoluer en quelque chose de solide si tu y prêtes attention.",
        "Professionnellement, ton esprit fonctionne de manière légèrement inhabituelle (ce qui est une bonne chose). Une idée étrange pourrait en réalité être brillante. Note-la avant qu’elle ne disparaisse dans le vide cosmique.",
        "La motivation fluctue, mais ce n’est pas grave. Même un petit progrès aujourd’hui peut avoir des conséquences étonnamment positives plus tard."
    ]

    money_texts = [
        "Côté finances, évite les décisions impulsives. Une dépense inutile pourrait sembler essentielle sur le moment (surtout si elle concerne quelque chose de bizarrement spécifique). Prends du recul.",
        "L’argent circule avec une énergie… disons, créative. Ce n’est pas forcément le moment d’être ultra-stratégique, mais plutôt d’observer tes habitudes et d’apprendre quelque chose sur toi.",
        "Une petite opportunité financière pourrait apparaître, mais elle demandera de l’attention. Rien de magique, mais potentiellement utile."
    ]

    advice = [
        "Aujourd’hui, fais confiance à ton rythme, même s’il semble étrange.",
        "N’essaie pas de tout contrôler. Même les étoiles improvisent parfois.",
        "Accorde de l’importance aux petits détails, ils cachent souvent quelque chose.",
        "Laisse une place au hasard. Il fait parfois du bon travail.",
        "Rappelle-toi : ne pas comprendre est aussi une forme de compréhension."
    ]

    weird_extras = [
        "Un objet banal pourrait soudain te sembler chargé de sens.",
        "Les coïncidences sont probablement un peu trop nombreuses pour être ignorées.",
        "Quelque part, quelqu’un vit exactement le même moment que toi (c’est troublant).",
        "Un léger sentiment de déjà-vu pourrait apparaître sans prévenir.",
        "Même le silence semble avoir quelque chose à dire aujourd’hui."
    ]

    lucky_colors = [
        "Cramoisi", "Azur", "Émeraude", "Jaune doré", "Lavande",
        "Corail", "Turquoise", "Indigo", "Argent", "Rose"
    ]

    horoscope = f"""
🔮 Horoscope du jour pour {sign} ({style}) 🔮

{random.choice(openings)}. Tu pourrais ressentir une légère distorsion dans ta perception des choses, comme si tout avait un sens… ou aucun.

❤️ Amour :
{random.choice(love_texts)}

💼 Travail :
{random.choice(work_texts)}

💰 Argent :
{random.choice(money_texts)}

✨ Conseil :
{random.choice(advice)}

🎨 Couleur porte-bonheur : {random.choice(lucky_colors)}
🔢 Nombre chanceux : {random.randint(1, 99)}

🌌 Bonus cosmique :
{random.choice(weird_extras)}
"""

    return horoscope.strip()


# # Exemple
# print(generate_horoscope("Balance"))
# print()
# print(generate_horoscope())  # aléatoire