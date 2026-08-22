SPECIES_CLASSES = [
    {
        "id": 0,
        "species": "Caulerpa lentilifera",
        "common_name": "Sea Grapes",
        "commercial_uses": [
            "Fresh seafood delicacy",
            "Salad and garnish ingredient",
            "Nutraceutical and specialty food use",
        ],
        "commercial_value_inr": 320.0,
    },
    {
        "id": 1,
        "species": "Caulerpa sertularioides",
        "common_name": "Green Caviar Seaweed",
        "commercial_uses": [
            "Gourmet seafood garnish",
            "Aquarium and marine ornamental trade",
            "Specialty food product"
        ],
        "commercial_value_inr": 290.0,
    },
    {
        "id": 2,
        "species": "Kappaphycus",
        "common_name": "Cottonii",
        "commercial_uses": [
            "Carrageenan extraction",
            "Food stabilizer and thickener",
            "Cosmeceutical hydrocolloid use"
        ],
        "commercial_value_inr": 260.0,
    },
    {
        "id": 3,
        "species": "Padina australis",
        "common_name": "Peacock's Tail",
        "commercial_uses": [
            "Bioactive compound extraction",
            "Cosmetic ingredient",
            "Natural antioxidant source"
        ],
        "commercial_value_inr": 240.0,
    },
    {
        "id": 4,
        "species": "Sargassum muticum",
        "common_name": "Wireweed",
        "commercial_uses": [
            "Alginate and fucoidan extraction",
            "Biofertilizer and soil amendment",
            "Aquaculture feed and biostimulant"
        ],
        "commercial_value_inr": 200.0,
    },
    {
        "id": 5,
        "species": "Turbinaria australis",
        "common_name": "Australian Turbinaria",
        "commercial_uses": [
            "Alginate extraction",
            "Biomass for bioproducts",
            "Feed supplement and fertilizer"
        ],
        "commercial_value_inr": 190.0,
    },
    {
        "id": 6,
        "species": "Ulva lactuca",
        "common_name": "Sea Lettuce",
        "commercial_uses": [
            "Fresh food ingredient",
            "Nutrient-rich salads and soups",
            "Organic biofertilizer"
        ],
        "commercial_value_inr": 180.0,
    },
]

SPECIES_INDEX = {entry["id"]: entry for entry in SPECIES_CLASSES}
