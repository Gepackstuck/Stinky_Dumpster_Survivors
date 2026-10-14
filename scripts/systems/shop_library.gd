class_name ShopLibrary
extends RefCounted
## Витрина Ларька (Brotato): 4 слота с оружием и перками, цены растут с волной и тиром, заморозка, реролл.
## Предложение — словарь {kind: weapon|perk, id, tier, price, locked, sold}.


static func perk_id_of(weapon_id: StringName) -> StringName:
	return StringName("w_" + String(weapon_id))


static func base_price(kind: StringName, id: StringName) -> float:
	if kind == &"weapon":
		return float(Balance.WEAPON_PRICE.get(id, 20))
	return float(Balance.PERK_PRICE.get(id, 15))


static func price(kind: StringName, id: StringName, tier: int, wave: int) -> int:
	return maxi(roundi(base_price(kind, id) * Balance.SHOP_PRICE_TIER_MULT[tier - 1] * (1.0 + Balance.SHOP_PRICE_WAVE_GROWTH * wave)), 1)


static func roll_tier(wave: int) -> int:
	var c2: float = clampf((wave - 1) * Balance.SHOP_TIER2_PER_WAVE, 0.0, 0.5)
	var c3: float = clampf((wave - 3) * Balance.SHOP_TIER3_PER_WAVE, 0.0, 0.35)
	var c4: float = clampf((wave - 7) * Balance.SHOP_TIER4_PER_WAVE, 0.0, 0.2)
	var roll: float = randf()
	if roll < c4:
		return 4
	if roll < c4 + c3:
		return 3
	if roll < c4 + c3 + c2:
		return 2
	return 1


static func new_offer(wave: int) -> Dictionary:
	var perk_pool: Array[StringName] = []
	for perk_id: StringName in PerkLibrary.ALL:
		if perk_id in PerkLibrary.WEAPON_PERKS:
			continue
		var cap: int = PerkLibrary.max_stacks(perk_id)
		if cap == 0 or GameState.get_perk_stacks(perk_id) < cap:
			perk_pool.append(perk_id)
	var offer: Dictionary = {"locked": false, "sold": false}
	if randf() < Balance.SHOP_WEAPON_CHANCE or perk_pool.is_empty():
		var weapon_perk: StringName = PerkLibrary.WEAPON_PERKS[randi() % PerkLibrary.WEAPON_PERKS.size()]
		offer["kind"] = &"weapon"
		offer["id"] = StringName(String(weapon_perk).trim_prefix("w_"))
		offer["tier"] = roll_tier(wave)
	else:
		offer["kind"] = &"perk"
		offer["id"] = perk_pool[randi() % perk_pool.size()]
		offer["tier"] = 1
	offer["price"] = price(offer["kind"], offer["id"], offer["tier"], wave)
	return offer


## Заполнить витрину: замороженные и непроданные остаются, остальное — новое (реролл и новая волна).
static func fill_offers(existing: Array[Dictionary], wave: int, keep_unlocked: bool = false) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for i: int in Balance.SHOP_SLOTS:
		if i < existing.size() and existing[i]["locked"] and not existing[i]["sold"]:
			result.append(existing[i])
		elif keep_unlocked and i < existing.size() and not existing[i]["sold"]:
			result.append(existing[i])
		else:
			result.append(new_offer(wave))
	return result


static func title(offer: Dictionary) -> String:
	if offer["kind"] == &"weapon":
		return PerkLibrary.title(perk_id_of(offer["id"]))
	return PerkLibrary.title(offer["id"])


static func icon(offer: Dictionary) -> Texture2D:
	if offer["kind"] == &"weapon":
		return PerkLibrary.icon(perk_id_of(offer["id"]))
	return PerkLibrary.icon(offer["id"])


static func description(offer: Dictionary) -> String:
	var text: String = "ЦЕНА: %d\n" % offer["price"]
	if offer["kind"] == &"weapon":
		var stats: Dictionary = Balance.WEAPONS[offer["id"]]
		var tier: int = offer["tier"]
		text += "ОРУЖИЕ\nУРОН: %d\nПАУЗА: %.2f С" % [roundi(stats["damage"] * Balance.WEAPON_TIER_DAMAGE[tier - 1]), stats["cooldown"] * Balance.WEAPON_TIER_COOLDOWN[tier - 1]]
	else:
		text += PerkLibrary.description(offer["id"])
	if offer["locked"]:
		text += "\n[ЗАМОРОЖЕНО]"
	return text


## Пустая строка — можно купить, иначе причина отказа (жёсткая фраза).
static func why_not(offer: Dictionary) -> String:
	if offer["sold"]:
		return "УЖЕ КУПЛЕНО."
	if GameState.coins < offer["price"]:
		return "НЕ ХВАТАЕТ ГОВНА, БОМЖ."
	if offer["kind"] == &"weapon":
		if GameState.weapons.size() >= Balance.WEAPON_SLOTS and GameState.find_weapon(offer["id"], offer["tier"]) < 0:
			return "СЛОТЫ ЗАБИТЫ. ПЕРЕРАБОТАЙ ХЛАМ."
	else:
		var cap: int = PerkLibrary.max_stacks(offer["id"])
		if cap > 0 and GameState.get_perk_stacks(offer["id"]) >= cap:
			return "ЭТО УЖЕ НА МАКСИМУМЕ."
	return ""


static func buy(offer: Dictionary) -> void:
	GameState.coins -= offer["price"]
	offer["sold"] = true
	if offer["kind"] == &"weapon":
		if GameState.weapons.size() < Balance.WEAPON_SLOTS:
			GameState.add_weapon(offer["id"], offer["tier"])
		else:
			var index: int = GameState.find_weapon(offer["id"], offer["tier"])
			GameState.weapons[index]["tier"] += 1
			EventBus.weapons_changed.emit()
	else:
		GameState.apply_perk(offer["id"])
