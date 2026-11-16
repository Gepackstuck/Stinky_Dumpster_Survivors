"""БИБЛИЯ ОФОРМЛЕНИЯ «ВОНЮЧАЯ ПОМОЙКА»: единый промпт стиля и описания ВСЕХ героев, врагов и боссов для FLUX (tools/hd/flux_gen.py).

Формула каждого описания (иначе выходят «базовые спрайты»):
  1) КТО ЭТО по лору игры (docs/LORE.md, scripts/systems/enemy_names.gd) - 2-3 главные приметы, по которым узнают;
  2) УРОДСТВО - одна жуткая телесная деталь (кишки, лишние глаза, гниль, опарыши, щупальца);
  3) АБСУРД - одна шутка-деталь помойного быта (бутылка, семки, бычок, квитанция, тапок);
  4) ГРЯЗЬ - что из него течёт: блевотина, кровь, понос.
Правило цвета: мир тёмный и гнилой, ярко светится только мерзость (кислотно-зелёная блевотина, алая кровь, блестящий коричневый понос).
Пропорции карикатурные: огромная голова, маленькое тело, глаза разного размера - лицо читается на спрайте в 90 пикселей.

Запуск: python3 tools/hd/bible.py heroes|enemies|bosses|all -> tools/_hd_raw/fx/jobs_<группа>.json
"""
import json
import os
import sys

PRE = "Detailed 16-bit pixel art game sprite. Dark horror mixed with absurd filthy black humor, a stinking garbage dump apocalypse. "
LOOK = ("Grotesque caricature: oversized head, small body, bulging bloodshot eyes of different sizes. Dark grimy palette of rot, rust and mold; "
        "only the vomit glows acid green, the blood is bright red, the diarrhea is glossy brown. Thick black outline, crisp chunky pixels, dramatic rim light. ")
ONE = "One single figure, full body from head to feet, centered, isolated on a plain flat mid-grey background, no text, no scenery, no ground shadow."
SHEET = ("Character turnaround sheet: exactly three full-body views of the SAME character standing side by side in a row, same size, same clothes, same colors: "
         "FRONT view facing the viewer, SIDE view in profile facing left, BACK view from behind. ")
SHEET_END = "Three separate figures in a row with gaps between them, full body from head to feet, plain flat mid-grey background, no text, no labels, no scenery, no ground shadow."
OBJ = ("Dark grimy palette of rot, rust and mold; only the vomit glows acid green, the blood is bright red, the diarrhea is glossy brown. "
       "Thick black outline, crisp chunky pixels, dramatic rim light. One single object, centered, isolated on a plain flat mid-grey background, no text, no scenery, no ground shadow.")

# ---------------------------------------------------------------- ГЕРОИ (лист: фас, бок влево, спина)
HEROES = {
    "hobo": "Hobo Vasya, a drunk homeless man in a torn fur ushanka with one ear flap sticking up, enormous swollen red nose, matted beard full of crumbs and maggots, one eye huge and one tiny, toothless grin drooling green vomit. Ragged acid-green coat covered with colorful patches, a string of guts hangs from his torn belly like sausages, he hugs a vodka bottle, bare dirty feet, flies circle his head.",
    "squid": "A gopnik squid thug: bloated blue squid head with a beard of slimy tentacles, flat cap tilted sideways, a cigarette butt stuck in its beak, cocky confident eyes of different sizes. Black tracksuit with three white stripes, gold chain, pointy shoes, sunflower seed husks stuck to the tentacles, one tentacle holds a beer bottle, slime dripping.",
    "clerk": "An office plankton clerk, a pale exhausted office zombie: white shirt with sweat stains, red tie strangling his neck like a noose, name badge, thick cracked glasses with one eyeball popped out and hanging on a nerve, mouth stapled shut and leaking blood, dark bags under eyes. He clutches a coffee mug full of maggots, a stapler is stuck in his skull.",
    "janitor": "Yard janitor Palych, an old street sweeper: peaked cap, huge grey walrus mustache with garbage tangled in it, orange safety vest with reflective stripes, rubber boots. He holds a broom made of a human spine and hair, one eye is replaced by a bottle cap, rotten teeth, a rat peeks out of his vest pocket, brown sludge on his boots.",
    "uncle_vitya": "Uncle Vitya, a bloated alcoholic in a dirty white sleeveless undershirt stretched over a giant hairy beer belly, rosy purple nose, grey stubble, a vodka bottle sticking out of his tracksuit pants pocket. He sways drunk, his liver hangs out of a hole in his side and he holds it like a handbag, green vomit on his chest, slippers on bare feet, a cigarette behind his ear.",
    "blogger": "A zombie blogger: rotten green zombie with bright pink hair, dark circles under the eyes, gold chain, ring light halo stuck on his head. One hand holds a glowing cracked smartphone on a selfie stick, his lower jaw hangs on one tendon, a worm crawls out of his eye socket making a duck face, torn hoodie, exposed ribs with a like-button heart inside.",
    "granny": "Granny from the bench, an evil old woman in a polka dot headscarf, thick glasses, a shark-toothed grin too wide for her face, a flowery house robe, a crooked cane, a string bag full of sunflower seeds and human eyeballs. Seed husks stuck in her bloody teeth, varicose legs in felt slippers, a third tiny hand grows from her hump.",
    "courier": "A delivery courier in a green jacket and cap with a giant yellow thermal box on his back. The box is rotting: tentacles, flies and brown sludge leak out of it, the long-cold order has come alive and looks out with one eye. His face is gaunt with sunken cheeks, bicycle chain wrapped around his arm, torn sneakers, a pizza slice with teeth stuck to his shoulder.",
    "pigeon": "A mutant pigeon hero: fat grey pigeon with white wing stripes, iridescent green and purple neck, crazy bulging eyes and a third red eye on the forehead. Scabby featherless patches, a human finger in its beak, pink scaly legs with one too many toes, bread crumbs and white droppings stuck to its chest, a tiny crown made of a bottle cap.",
    "punk": "A punk rat: rat with a tall acid-green mohawk, torn pink ears with safety pins, long yellow buck teeth, a studded black leather jacket, tail sticking up defiantly with a rusty ring on it. One eye is a red button, mangy fur with bald spots, combat boots too big for it, it holds a broken bottle, anarchy sign scratched on its belly.",
    "shawarma": "Shawarma cook Edik: tall dirty chef hat, enormous black mustache, gold chain on a hairy chest, an apron covered with stains of unknown origin and blood. He carries a vertical kebab spit with a suspicious meat cone that has a tail, paws and an eye in it, a big knife in the other hand, greasy sweat, flies, a rat tail sticks out of his pocket.",
    "guard": "Security guard Sanych: dark blue uniform, peaked cap with a cockade, big mustache, belt with a rubber truncheon. Bloated and half-asleep, one eye closed, a crossword puzzle glued to his hand with spider web, mold growing on his shoulders because he never left his post, a thermos, his legs have taken root into a piece of asphalt he drags along.",
    "student": "A debtor student: purple hoodie, wild messy hair, giant dark circles under red insomniac eyes, an energy drink can fused into his fist with veins. Skinny, shaking, a debt receipt nailed to his forehead, instant noodles hanging from his mouth like tentacles, backpack with a skull, one sneaker missing, twitching eyelid.",
    "plumber": "Plumber Valera: red cap, enormous mustache, blue overalls over a yellow t-shirt, a huge rusty pipe wrench. Brown sewage sludge drips from him, a toilet plunger is stuck on his head under the cap, a rusty pipe goes through his chest in one side and out the other with a rat living in it, rubber boots full of sludge.",
    "dacha": "Aunt Zina from the dacha: straw hat with flowers, pink dress, white apron, rosy cheeks, a bucket in her hand. The flowers on the hat are carnivorous with teeth, the bucket is full of manure and worms, seedlings grow out of her ears and back, a garden trowel dripping blood, dirt under long nails, a sweet smile with rotten teeth.",
    "skater": "An eternal skater: red sun visor, yellow t-shirt, big headphones, a skateboard under his arm. His knees are smeared with brilliant green antiseptic and a bone sticks out of one shin, the skateboard has teeth and a tongue, band-aids everywhere, one eye swollen shut, missing front teeth in a happy grin, long skinny arms.",
    "gopnik_jock": "A gopnik jock: blue track jacket with white stripes, eight-panel flat cap, gold chain, a gold tooth in a small dumb face. His arms are absurdly gigantic, wider than his shoulders, covered with veins and prison tattoos, tiny head, tiny legs in pointy shoes, he squeezes a kettlebell made of a skull, sunflower seeds spill from his pocket.",
    "cat": "A grey striped street tomcat standing upright on two legs, with a torn ear, a scar across his face and two different eyes, one yellow and one milky white, wearing old oversized leather boots. A fish skeleton in his teeth, nine tally marks scratched on his chest, mangy tail with a bandage, fleas jumping, a smug evil look.",
    "slime": "Slime Grisha: a green lump of sewer slime with huge bulging eyes on stalks, a long tongue hanging out, and small brown legs. Inside its translucent body float garbage, a boot, bones, a toilet brush and a rubber duck, brown sludge drips from it, a proud stupid smile, flies above it.",
}

# ---------------------------------------------------------------- ВРАГИ (один вид)
ENEMIES = {
    "squid_gopnik": "A gopnik squid thug standing with hands in pockets: bloated crimson squid head with a beard of writhing tentacles and a gaping maw of crooked teeth, a red flat cap, a cigarette butt, a black tracksuit with three stripes. He spits sunflower seed husks, brass knuckles on a tentacle, slime and blood dripping. Menacing and stupid. Front view.",
    "microbe": "A giant slimy microbe that grew in an old fridge: a translucent sickly green blob with dozens of tiny eyes of different sizes, a drooling toothless mouth, hairy cilia, bubbles and mold spots inside, a piece of rotten sausage and a fridge magnet stuck in its body. Slow and dumb. Front view.",
    "npc_bot": "A soulless NPC bot: a stiff grey mannequin office worker with a blank smooth face that has only a pasted paper smile, a wind-up key in its back, a yellow exclamation mark floating above its head, cheap suit, arms stretched forward like a sleepwalker, cracks in its plastic skin leaking black oil. Front view.",
    "cockroach": "A small fast disgusting cockroach standing on its hind legs: glossy brown shell, long twitching antennae, a tiny human face with a mustache, six hairy legs, it carries a bread crumb, crushed wing oozing yellow goo. Front view.",
    "wifi_ghost": "The ghost of bad wifi signal: a translucent pale blue floating ghost whose body is an old router with two bent antennas, loading spinner circles for eyes, a screaming mouth, a torn ethernet cable for a tail, weak signal bars glowing on its forehead, glitch pixels around it. Floating, front view.",
    "chaser": "A fat dung fly in flight: bloated hairy black body, huge red faceted eyes, a human mouth with yellow teeth and a long licking tongue, dirty transparent wings, legs smeared with brown dung, a stinger dripping. Flying, front view.",
    "charger": "A killer shopping cart monster: a rusty supermarket trolley whose metal basket is a giant jaw with crooked bloody teeth, a long tongue of rotten sausages, two crazed eyeballs on the handle bar, wobbly wheels leaving blood tracks, the basket is full of rotting groceries, a severed hand and a dead pigeon. It leans forward ready to ram. Three-quarter front view.",
    "spitter": "An acid spitter: a cowardly bloated toad-like creature with warty skin covered in sores, enormous swollen cheeks full of glowing acid-green bile, a puckered mouth ready to spit, small scared eyes, skinny trembling legs, bile dripping from its chin and burning holes in its belly. Front view.",
    "bruiser": "A loader thug: a huge fat mover in dirty blue overalls with an enormous belly, tiny bald head sunk into the shoulders, small angry eyes, massive hairy arms carrying a crate of kefir on his shoulder, a cigarette, a hernia bulging from his side, sweat stains. Front view.",
    "looter": "A thief rat: a fat cunning grey rat standing upright, a black robber mask over its eyes, a big patched sack full of coins and stolen things over its shoulder, long greasy tail, yellow teeth in a sly grin, gold coins falling out of the sack. Front view.",
    "healer": "A suck-up medic: a creepy thin paramedic in a dirty white coat with a red cross, a medical mask soaked with blood, a huge syringe full of green liquid, leeches hanging from his arms, a bag of pills, a fawning servile smile seen through the mask, bandages trailing behind. Front view.",
    "blinker": "A glitchy hobo who drank a teleport potion: a ragged homeless man whose body is half broken into purple glitch pixels and static, his head displaced sideways from his neck, a purple swirling hole in his belly, an empty vial in his hand, surprised stupid face, torn coat. Front view.",
    "thief": "A pickpocket: a small sneaky hunched man in a flat cap pulled over his eyes and a long coat, extremely long thin fingers, a sack full of brown turd-shaped coins on his back, tiptoeing, a sly toothy grin, wallets and watches hanging inside his open coat. Front view.",
    "shield_bearer": "A gopnik with a dumpster lid: a squat thug in a tracksuit and flat cap hiding behind a big round rusty garbage can lid used as a shield, covered with dents and blood, only his mean eyes and cap are visible above it, he chews sunflower seeds, a crowbar in the other hand. Front view.",
    "mirror": "A mutant vanity mirror: grandma's old wooden three-panel dressing table mirror that has grown fleshy tentacles instead of legs, the cracked glass shows a distorted screaming face, shards of glass float around it, lace doily and perfume bottles on its shelf, blood runs from the cracks. Front view.",
    "egg": "A larva egg: a big pulsating slimy translucent egg with veins, a dark creature with one eye visible curled inside pressing a clawed hand against the shell, cracks leaking green slime, it sits in a nest of garbage and hair. Front view.",
    "mamka": "Mamka, a breeding mother monster: an enormous fat woman-creature in a stained nightgown with curlers in her hair, a gigantic swollen belly with small hands and faces pushing out from inside, several larva babies crawling on her and hanging from her, a rolling pin in her hand, tired furious face. Front view.",
    "glutton": "A glutton: a monstrously fat creature that is mostly a giant mouth, sitting in a broken armchair, a tongue hanging to the floor, chewing a leg of another monster, grease and green vomit on its many chins, bones and wrappers around it, tiny greedy eyes, the belly is splitting at the seams. Front view.",
    "trash_bin": "An ordinary small round metal trash can, a plain lifeless object with no face, no legs and no eyes: dented rusty zinc bin with a crooked lid half open, stuffed with garbage bags, a fish skeleton, a boot and empty bottles, brown sludge dripping down its side, flies above, a gold coin glinting inside. Three-quarter top-down view.",
}

# ---------------------------------------------------------------- БОССЫ (один вид)
BOSSES = {
    "boss_roach_king": "The Roach King: a huge muscular bodybuilder cockroach standing upright and flexing, glossy brown shell like armor, a golden champion wrestling belt, a small crown, veiny arms, six-pack abs on its belly plates, a tub of protein powder from the dump in one hand, an egg sac on its back. Front view.",
    "boss_trash_golem": "The Trash Golem: a towering giant made of black garbage bags tied together, with a rusty bin for a head with two glowing eyes, arms made of rotten furniture and pipes, bags are torn and leak brown sludge, rats and flies live in it, a fish skeleton necklace, it holds a garbage bag ready to throw. Front view.",
    "boss_uk": "The Management Company boss: a shabby soviet housing office booth standing on two giant scaly chicken legs. A small service window with a hateful bureaucrat woman's face in curlers peeking out, a sign plate on top, rubber stamps and utility bills flying out, rusty pipes leaking brown sludge, a red rotary phone hanging on a cord. Huge and intimidating. Three-quarter front view.",
    "boss_mother_in_law": "The Mother-in-law: a giant furious woman in a flowery house robe with hair curlers, a rolling pin raised in her fist, her mouth is opened impossibly wide in a scream with letters and spit flying out, a hairy wart, fluffy slippers, a tiny scared husband hides in her robe pocket, veins bulging on her neck. Front view.",
    "boss_pigeon_papa": "The Pigeon Papa: a giant fat pigeon mafia boss in a black bowler hat, with an iridescent green and purple neck, a monocle, a cigar, one wing spread showing knives made of feathers, white droppings bombs strapped to its belly, red mad eyes, scaly feet with rings. Front view.",
    "boss_rat_queen": "The Rat Queen: an obese giant rat sitting on a throne of garbage, a crown made of beer bottle caps, a royal mantle made of a black garbage bag, a scepter made of a bone with a tin can, long greasy tail, many small rats peeking from under her mantle, yellow teeth, cruel eyes. Front view.",
    "boss_blue_whale": "The Blue Whale: a huge sad blue whale stranded on a garbage dump, lying on its belly on bags and tires, crying big salty tears, a mouth full of garbage and a shopping cart stuck in its baleen, barnacles and plastic bags on its skin, a harpoon in its back, a fountain of brown water from its blowhole. Side view facing left.",
    "boss_mega_hamster": "The Mega Hamster: a giant enraged hamster as big as a car, grown on rotten shawarma, cheeks stuffed to bursting with garbage and bones, red hateful eyes, a kebab skewer through its ear, greasy fur with bald patches, its belly is cracking and tiny slimy microbes crawl out of the cracks. Front view.",
    "boss_zakhar": "Zakhar from Morkovsk: a mad village man with a giant carrot-shaped orange head and green carrot-top hair, a long beard, a quilted jacket and felt boots, a bandolier of carrots across his chest, a green toxic fart cloud behind him, one leg raised for a running kick, crazy grin. Front view.",
    "boss_minion": "A psycho minion: a small yellow pill-shaped creature in blue overalls with one giant bloodshot goggle eye, twitching and insane, a mad grin of sharp teeth, it throws rusty wrenches, a brown puddle spreads under it, straitjacket straps hanging from its arms, foam at its mouth. Front view.",
}


# ---------------------------------------------------------------- ОРУЖИЕ В РУКАХ (лежит горизонтально, рабочим концом ВПРАВО)
WEAPON_END = "The object lies horizontally, its business end points to the RIGHT, side view, no hands, no person. "
WEAPONS = {
    "lighter": "A battered cheap plastic cigarette lighter with a sparking flint wheel and a tall crooked flame, a naked lady sticker peeling off, greasy fingerprints, a burnt fly stuck to it.",
    "sock": "A stiff stinking week-old sock full of holes, standing on its own, with a big toe hole like a screaming mouth, green toxic stink fumes rising from it, flies falling dead around it, mold spots.",
    "slingshot": "A crude wooden Y-shaped slingshot made of a chewed branch and a condom-colored rubber band, loaded with a tooth, electrical tape on the handle, a dried blood stain.",
    "mop": "A filthy mop on a long wooden stick, its head is a mass of grey rotten rags like wet hair with a staring eyeball and worms tangled in it, dripping brown water.",
    "bottle": "A broken green glass vodka bottle held by the neck, a jagged 'rose' edge with blood and a piece of skin on it, the label half torn, a drop of vodka inside.",
    "condensed_milk": "A dented blue and white tin can of condensed milk with a jagged opened lid, thick yellowish milk oozing out with ants and a cockroach drowning in it, a bent spoon stuck inside.",
    "crossbow": "A homemade crossbow built from a chair leg, a bicycle spring and wire, loaded with a rusty rebar bolt that has a pigeon skewered on it, electrical tape everywhere.",
    "extension_cord": "A coiled dirty white extension cord with a power strip at the end, bare sparking wires, a burnt rat stuck in one socket, blue electric sparks jumping.",
    "frying_pan": "A heavy black cast iron frying pan with burnt fried eggs stuck to it that look like two terrified eyes, a dent shaped like a face, blood and hair on the edge, grease dripping.",
    "laser_pointer": "A cheap keychain laser pointer shooting a thin bright red beam, the beam burns a smoking hole, a cat hair ball and a tiny burnt eye hang on its chain.",
    "mosin": "An old Mosin rifle with a cracked wooden stock wrapped with tape, a rusty bayonet with a dried sausage on it, carved tally marks, a spider web in the sight.",
    "pipe_gun": "A homemade sawn-off pipe shotgun made of two rusty water pipes, duct tape and a door bolt, smoke curling from the barrels, a nail and a tooth sticking out of the muzzle.",
    "plunger": "A dirty toilet plunger with a cracked red rubber cup dripping brown sludge, a tangle of hair and a goldfish skeleton stuck to it, the wooden handle chewed.",
    "rolling_pin": "A heavy wooden rolling pin stained with blood and dough, a tooth embedded in it, flour hand prints, a hair curler stuck to one handle.",
    "rotten_cheese": "A wedge of rotten cheese covered with green and blue fuzzy mold, big holes with maggots peeking out and waving, a green stink cloud above it, a mouse trap tail stuck to it.",
    "shiv": "A prison shiv: a sharpened spoon with a handle wrapped in dirty cloth and thread, blood on the blade, a tiny tattoo-style skull scratched on it.",
    "shovel": "A rusty garden shovel with a chipped blade covered with grave dirt, blood and a worm, a skull fragment stuck to it, the wooden handle split and taped.",
    "slipper": "An old worn plaid house slipper flattened by years, a hole at the toe with a cockroach looking out, a squashed bug on the sole, legendary and menacing.",
    "spray_can": "A rusty aerosol spray can of insect poison with a skull label, spraying a cloud of sickly green gas, dead flies glued to the can, a dented bottom.",
    "syringe": "A huge used glass syringe full of glowing acid green liquid with a bubble, a bent bloody needle with a drop hanging from it, cracked glass, dirty finger grips.",
    "tin_bomb": "A homemade bomb from a rusty tin can stuffed with nails, wrapped in blue electrical tape, a sparking burning fuse, an alarm clock taped to it, a smiley face drawn in marker.",
    "blowtorch": "A rusty gas blowtorch with a dented red canister and a roaring blue and orange flame jet, soot, a burnt sausage skewered on its nozzle guard.",
}

# ---------------------------------------------------------------- РЕКВИЗИТ АРЕНЫ (вид 3/4 сверху, предметы без лиц)
PROP_END = "A lifeless prop object for a top-down game, three-quarter top-down view. "
PROPS = {
    "dumpster": "A big rusty green metal dumpster overflowing with rotting garbage, a bloated purple dead hand hangs over the edge holding a bottle, a fat rat sits on the lid, green vomit drips down the side, flies.",
    "container": "A rusty dented blue shipping container with bloody handprints dragged along its side, a puddle of brown sludge leaking from under the door, a crooked graffiti skull, a boot sticking out of the gap.",
    "car_wreck": "A burnt-out rusty soviet sedan car wreck without wheels standing on bricks, a skeleton in a flat cap behind the wheel, grass and garbage inside, broken glass, a pigeon nest on the roof.",
    "tires": "A pile of old black tires with a rotting dead dog on top, flies, a syringe and bottles in the middle tire, green slime pooled inside.",
    "barrel_fire": "A rusty oil barrel with a fire burning inside, orange flames and sparks, a rat roasting on a stick over it, soot streaks, two empty vodka bottles beside it.",
    "lamp": "A bent rusty street lamp post with a flickering sickly yellow lamp, a noose and a pair of boots hanging from it, moths, torn posters glued to the pole.",
    "fence": "A section of broken rotten wooden fence with rusty barbed wire, a crow sitting on it, bloody rags and a torn jacket hanging on the nails, a crude skull drawn in paint.",
    "trash_pile": "A huge heap of black garbage bags, torn open with rotting meat, bones and a doll head spilling out, a pair of legs in sneakers sticking out upside down, maggots, a stink cloud.",
    "fridge": "An old white soviet fridge lying open on its side, full of black mold and rotting meat, something with eyes hiding inside, a magnet and a child's drawing on the door, yellow liquid leaking.",
    "mattress": "A filthy striped mattress with yellow and brown stains and springs sticking out, a bloated drunk hobo sleeping on it face down with a bottle, a puddle of green vomit beside his head.",
    "toilet": "A cracked white porcelain toilet standing alone in the dirt, overflowing with brown sludge, a hand reaching out of the bowl, toilet paper trailing, flies, a newspaper beside it.",
    "gravestone": "A crooked grave marker made of an old door and a tire, a portrait photo oval, plastic flowers, empty vodka bottles and a shot glass with a slice of bread on top, fresh dirt mound with a hand sticking out.",
    "corpse": "A bloated rotting corpse of a hobo lying on its back, belly burst open with guts, covered with flies and maggots, in a puddle of green and red slime, one boot missing, a bottle still in the hand.",
    "bones": "A pile of gnawed bones and human skulls mixed with garbage, a rat crown of bottle caps on one skull, candles made of fat, dried blood.",
    "sofa": "A rotten torn brown sofa with springs sticking out, a dead rat on the cushion, a big stain shaped like a person, an old TV with a broken screen standing on it.",
    "bathtub": "A rusty cast iron bathtub full of thick brown and green sludge with bubbles, a rubber duck and an eyeball floating in it, an arm hanging over the edge, a shower hose like a snake.",
}

GROUND = ("Top-down seamless texture of the ground at a stinking garbage dump at night, detailed 16-bit pixel art: dark wet black-brown mud, squashed cans, bottle caps, "
          "cigarette butts, small bones, rags, a few maggots, faint dried blood stains and faint dull green puke stains. Very dark, low contrast, calm and even, no big objects, "
          "no characters, flat view straight from above, uniform lighting, tileable.")


def jobs(group):
    out = []
    root = "tools/_hd_raw/fx/"
    if group in ("heroes", "all"):
        for i, (name, d) in enumerate(HEROES.items()):
            for s in (1, 2):
                out.append({"out": "%shero_%s_%d.png" % (root, name, s), "seed": 100 + i * 2 + s, "w": 1152, "h": 640,
                            "prompt": PRE + SHEET + "The character: " + d + " " + LOOK + SHEET_END})
    if group in ("enemies", "all"):
        for i, (name, d) in enumerate(ENEMIES.items()):
            for s in (1, 2):
                out.append({"out": "%senemy_%s_%d.png" % (root, name, s), "seed": 300 + i * 2 + s, "w": 768, "h": 768,
                            "prompt": PRE + d + " " + (OBJ if name == "trash_bin" else LOOK + ONE)})
    if group in ("bosses", "all"):
        for i, (name, d) in enumerate(BOSSES.items()):
            for s in (1, 2):
                out.append({"out": "%s%s_%d.png" % (root, name, s), "seed": 500 + i * 2 + s, "w": 896, "h": 896, "prompt": PRE + d + " " + LOOK + ONE})
    if group in ("weapons", "all"):
        for i, (name, d) in enumerate(WEAPONS.items()):
            for sd in (1, 2):
                out.append({"out": "%sweapon_%s_%d.png" % (root, name, sd), "seed": 700 + i * 2 + sd, "w": 768, "h": 768, "prompt": PRE + WEAPON_END + d + " " + OBJ})
    if group in ("props", "all"):
        for i, (name, d) in enumerate(PROPS.items()):
            for sd in (1, 2):
                out.append({"out": "%sprop_%s_%d.png" % (root, name, sd), "seed": 800 + i * 2 + sd, "w": 768, "h": 768, "prompt": PRE + PROP_END + d + " " + OBJ})
        for sd in range(1, 5):
            out.append({"out": "%sground_%d.png" % (root, sd), "seed": 900 + sd, "w": 1024, "h": 1024, "prompt": GROUND, "any_bg": True})
    return out


if __name__ == "__main__":
    g = sys.argv[1] if len(sys.argv) > 1 else "all"
    os.makedirs("tools/_hd_raw/fx", exist_ok=True)
    j = jobs(g)
    json.dump(j, open("tools/_hd_raw/fx/jobs_%s.json" % g, "w"), indent=1, ensure_ascii=False)
    print(len(j), "jobs ->", "tools/_hd_raw/fx/jobs_%s.json" % g)
